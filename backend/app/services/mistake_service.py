import json
from datetime import datetime, timezone

from sqlalchemy import func

from ..extensions import db
from ..models import MistakeRecord
from .llm_service import generate_reply

_ALLOWED_TYPES = {"concept", "logic", "boundary", "syntax", "expression", "debugging"}
_LEGACY_SAMPLE_QUESTIONS = {
    "reactive 解构后为什么会失去响应式",
    "接口返回后直接 map 为什么容易报错",
    "回答 LRU 设计题时为什么不能只说哈希表",
}


def _extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model did not return valid JSON")

    return json.loads(text[start : end + 1])


def _normalize_type(mistake_type: str) -> str:
    value = mistake_type.strip()

    if value not in _ALLOWED_TYPES:
        raise ValueError("Model returned an invalid mistake type")

    return value


def _build_manual_card_prompts(topic: str, question: str, note: str):
    system_prompt = (
        "You are a teaching assistant that organizes knowledge gap cards. "
        "Based on the topic, title and optional note, return strict JSON only. "
        "The JSON keys must be summary, mistakeType, mistakeReason, improvementSuggestion. "
        "mistakeType must be one of concept, logic, boundary, syntax, expression, debugging. "
        "summary should explain the knowledge point itself in one or two sentences. "
        "Do not output markdown or extra explanation."
    )
    user_prompt = (
        "Please organize this knowledge gap card and return JSON only.\n"
        f"Topic: {topic}\n"
        f"Title: {question}\n"
        f"Note: {note or 'None'}\n"
    )
    return system_prompt, user_prompt


def _build_classification_prompts(question: str, user_answer: str, reference_answer: str):
    system_prompt = (
        "You are a teaching assistant that analyzes programming mistakes. "
        "Based on the question, student answer and reference answer, return strict JSON only. "
        "The JSON keys must be summary, mistakeType, mistakeReason, improvementSuggestion. "
        "mistakeType must be one of concept, logic, boundary, syntax, expression, debugging. "
        "summary should explain the key knowledge point in one or two sentences. "
        "Do not output markdown or extra explanation."
    )
    user_prompt = (
        "Please analyze this mistake record and return JSON only.\n"
        f"Question: {question}\n"
        f"Student answer: {user_answer}\n"
        f"Reference answer: {reference_answer}\n"
    )
    return system_prompt, user_prompt


def _build_gap_extraction_prompts(question: str, reply: str):
    system_prompt = (
        "You are a teaching assistant that extracts potential knowledge gaps from a Q&A exchange. "
        "Return JSON only in the form "
        '{"items":[{"topic":"","question":"","summary":"","mistakeType":"","mistakeReason":"","improvementSuggestion":""}]}. '
        "Return at most 2 items. "
        "mistakeType must be one of concept, logic, boundary, syntax, expression, debugging. "
        'If there is no obvious knowledge gap, return {"items":[]}. '
        "Do not output markdown or extra explanation."
    )
    user_prompt = (
        "Please extract potential knowledge gaps from this Q&A exchange.\n"
        f"User question: {question}\n"
        f"Assistant reply: {reply}\n"
    )
    return system_prompt, user_prompt


def _normalize_analysis(payload: dict) -> dict:
    return {
        "summary": str(payload.get("summary", "")).strip() or "This is a knowledge point that still needs reinforcement.",
        "mistakeType": _normalize_type(str(payload.get("mistakeType", ""))),
        "mistakeReason": str(payload.get("mistakeReason", "")).strip()
        or "The current understanding is not stable enough and needs further clarification.",
        "improvementSuggestion": str(payload.get("improvementSuggestion", "")).strip()
        or "Review the definition, common use cases, and a minimal example together.",
    }


def _classify_manual_card(topic: str, question: str, note: str) -> dict:
    system_prompt, user_prompt = _build_manual_card_prompts(topic=topic, question=question, note=note)
    raw_reply = generate_reply(system_prompt=system_prompt, user_prompt=user_prompt)
    return _normalize_analysis(_extract_json(raw_reply))


def _classify_full_record(question: str, user_answer: str, reference_answer: str) -> dict:
    system_prompt, user_prompt = _build_classification_prompts(
        question=question,
        user_answer=user_answer,
        reference_answer=reference_answer,
    )
    raw_reply = generate_reply(system_prompt=system_prompt, user_prompt=user_prompt)
    return _normalize_analysis(_extract_json(raw_reply))


def list_mistakes() -> list[dict]:
    records = MistakeRecord.query.order_by(MistakeRecord.sort_order.asc(), MistakeRecord.created_at.desc()).all()
    return [record.to_dict() for record in records]


def create_mistake_record(entry: dict) -> dict:
    topic = entry["topic"]
    question = entry["question"]
    note = (entry.get("note") or "").strip()
    user_answer = (entry.get("userAnswer") or "").strip()
    reference_answer = (entry.get("referenceAnswer") or "").strip()

    if not user_answer and not reference_answer:
        analysis = _classify_manual_card(topic=topic, question=question, note=note)
        stored_user_answer = note
        stored_reference_answer = analysis["summary"]
    else:
        analysis = _classify_full_record(
            question=question,
            user_answer=user_answer,
            reference_answer=reference_answer,
        )
        stored_user_answer = user_answer
        stored_reference_answer = reference_answer or analysis["summary"]

    max_sort_order = db.session.query(func.max(MistakeRecord.sort_order)).scalar() or 0
    now = datetime.now(timezone.utc)

    record = MistakeRecord(
        topic=topic,
        mode=entry.get("mode") or "general",
        question=question,
        user_answer=stored_user_answer,
        reference_answer=stored_reference_answer,
        mistake_type=analysis["mistakeType"],
        mistake_reason=analysis["mistakeReason"],
        improvement_suggestion=analysis["improvementSuggestion"],
        sort_order=max_sort_order + 1,
        created_at=now,
        updated_at=now,
    )
    db.session.add(record)
    db.session.commit()
    return record.to_dict()


def create_mistakes_from_assistant(question: str, reply: str) -> list[dict]:
    system_prompt, user_prompt = _build_gap_extraction_prompts(question=question, reply=reply)
    raw_reply = generate_reply(system_prompt=system_prompt, user_prompt=user_prompt)
    payload = _extract_json(raw_reply)
    raw_items = payload.get("items")

    if not isinstance(raw_items, list) or not raw_items:
        return []

    max_sort_order = db.session.query(func.max(MistakeRecord.sort_order)).scalar() or 0
    now = datetime.now(timezone.utc)
    records: list[MistakeRecord] = []

    for index, item in enumerate(raw_items[:2], start=1):
        try:
            normalized = _normalize_analysis(item)
        except ValueError:
            continue

        title = str(item.get("question", "")).strip()
        topic = str(item.get("topic", "")).strip() or "General"

        if not title:
            continue

        records.append(
            MistakeRecord(
                topic=topic,
                mode="general",
                question=title,
                user_answer="来自一次答疑过程的自动提炼。",
                reference_answer=normalized["summary"],
                mistake_type=normalized["mistakeType"],
                mistake_reason=normalized["mistakeReason"],
                improvement_suggestion=normalized["improvementSuggestion"],
                sort_order=max_sort_order + index,
                created_at=now,
                updated_at=now,
            )
        )

    if not records:
        return []

    db.session.add_all(records)
    db.session.commit()
    return [record.to_dict() for record in records]


def delete_mistake_record(record_id: int) -> None:
    record = db.session.get(MistakeRecord, record_id)

    if not record:
        raise ValueError("知识点记录不存在")

    db.session.delete(record)
    db.session.commit()
    _normalize_sort_order()


def move_mistake_record(record_id: int, direction: str) -> list[dict]:
    record = db.session.get(MistakeRecord, record_id)

    if not record:
        raise ValueError("知识点记录不存在")

    if direction not in {"up", "down"}:
        raise ValueError("direction 只能是 up 或 down")

    if direction == "up":
        neighbor = (
            MistakeRecord.query.filter(MistakeRecord.sort_order < record.sort_order)
            .order_by(MistakeRecord.sort_order.desc())
            .first()
        )
    else:
        neighbor = (
            MistakeRecord.query.filter(MistakeRecord.sort_order > record.sort_order)
            .order_by(MistakeRecord.sort_order.asc())
            .first()
        )

    if not neighbor:
        return list_mistakes()

    record.sort_order, neighbor.sort_order = neighbor.sort_order, record.sort_order
    now = datetime.now(timezone.utc)
    record.updated_at = now
    neighbor.updated_at = now
    db.session.commit()
    return list_mistakes()


def reorder_mistake_records(ordered_ids: list[int]) -> list[dict]:
    if not ordered_ids:
        raise ValueError("orderedIds 不能为空")

    records = MistakeRecord.query.filter(MistakeRecord.id.in_(ordered_ids)).all()

    if len(records) != len(set(ordered_ids)):
        raise ValueError("orderedIds 中包含无效记录")

    record_map = {record.id: record for record in records}
    now = datetime.now(timezone.utc)

    for index, record_id in enumerate(ordered_ids, start=1):
        record = record_map[record_id]
        record.sort_order = index
        record.updated_at = now

    db.session.commit()
    return list_mistakes()


def _normalize_sort_order() -> None:
    records = MistakeRecord.query.order_by(MistakeRecord.sort_order.asc(), MistakeRecord.id.asc()).all()

    for index, record in enumerate(records, start=1):
        record.sort_order = index

    db.session.commit()


def seed_sample_mistakes() -> None:
    existing_records = MistakeRecord.query.order_by(MistakeRecord.sort_order.asc(), MistakeRecord.id.asc()).all()
    existing_questions = {record.question for record in existing_records}

    if existing_records and existing_questions != _LEGACY_SAMPLE_QUESTIONS:
        return

    if existing_records and existing_questions == _LEGACY_SAMPLE_QUESTIONS:
        for record in existing_records:
            db.session.delete(record)
        db.session.commit()

    now = datetime.now(timezone.utc)
    samples = [
        MistakeRecord(
            topic="Go",
            mode="general",
            question="goroutine 和线程到底是什么关系",
            user_answer="容易把 goroutine 直接等同成系统线程。",
            reference_answer="goroutine 是 Go 运行时调度的轻量执行单元，不等于操作系统线程，但会被映射到线程上运行。",
            mistake_type="concept",
            mistake_reason="把运行时调度层和操作系统线程层混在一起后，后面的调度模型就很难继续理解。",
            improvement_suggestion="后面看 GPM 模型时，先固定住 goroutine、M、P 三者各自负责什么。",
            sort_order=1,
            created_at=now,
            updated_at=now,
        ),
        MistakeRecord(
            topic="Rust",
            mode="general",
            question="所有权转移和借用什么时候最容易混淆",
            user_answer="看到变量传进函数时，常常分不清是 move 还是 borrow。",
            reference_answer="Rust 默认优先保证所有权清晰，是否发生 move 取决于类型特征和函数参数签名，借用则通过引用显式表达。",
            mistake_type="logic",
            mistake_reason="如果不先看参数签名，只凭感觉判断 move 或 borrow，后续借用检查器报错会越来越难定位。",
            improvement_suggestion="读函数调用时先看参数前有没有 &，再看类型是否实现 Copy，最后判断所有权是否还在原变量手里。",
            sort_order=2,
            created_at=now,
            updated_at=now,
        ),
        MistakeRecord(
            topic="Vue 3",
            mode="general",
            question="watch 和 watchEffect 应该怎么区分",
            user_answer="经常只记住 watchEffect 会立即执行，但忽略它们的依赖收集方式不同。",
            reference_answer="watch 更适合监听明确的数据源，watchEffect 会在执行过程中自动收集依赖，适合快速建立响应副作用。",
            mistake_type="concept",
            mistake_reason="如果只记行为差异，不理解依赖来源和清理时机，写副作用代码时很容易选错工具。",
            improvement_suggestion="拿同一个表单联动例子分别写一版 watch 和 watchEffect，对比依赖声明、触发时机和清理逻辑。",
            sort_order=3,
            created_at=now,
            updated_at=now,
        ),
    ]

    db.session.add_all(samples)
    db.session.commit()
