import json
import re
from datetime import datetime, timezone

from sqlalchemy import func

from ..extensions import db
from ..models import MistakeRecord
from .llm_service import generate_reply

_ALLOWED_TYPES = {"concept", "logic", "boundary", "syntax", "expression", "debugging"}
_TYPE_ALIASES = {
    "概念": "concept",
    "概念理解": "concept",
    "逻辑": "logic",
    "思路": "logic",
    "边界": "boundary",
    "边界条件": "boundary",
    "语法": "syntax",
    "表达": "expression",
    "表述": "expression",
    "调试": "debugging",
    "排查": "debugging",
}
_PROGRAMMING_KEYWORDS = {
    "c",
    "java",
    "go",
    "rust",
    "vue",
    "python",
    "sql",
    "js",
    "javascript",
    "html",
    "css",
    "接口",
    "函数",
    "数组",
    "指针",
    "对象",
    "线程",
    "协程",
    "响应式",
    "组件",
    "数据库",
    "算法",
    "报错",
    "调试",
    "编程",
}
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
    value = mistake_type.strip().lower()
    value = _TYPE_ALIASES.get(value, value)

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
        "你是一个编程教学助手，任务是从一次问答中提取用户可能还不清楚的知识点。"
        "只返回 JSON，不要 Markdown，不要代码块，不要解释。"
        "JSON 格式必须是："
        '{"items":[{"topic":"","question":"","summary":"","mistakeType":"","mistakeReason":"","improvementSuggestion":""}]}。'
        "最多返回 2 条。"
        "question 字段必须是知识点标题，不要直接照抄用户原问题。"
        "summary 必须给出具体结论，不能写“需要继续梳理”“本轮提问暴露”等空泛话。"
        "mistakeReason 必须指出具体混淆点。"
        "improvementSuggestion 必须给出一个可执行的小练习。"
        "mistakeType 只能使用英文值：concept、logic、boundary、syntax、expression、debugging。"
        "如果只是寒暄、问题过于宽泛或无法提取出具体知识点，返回 {\"items\":[]}。"
    )
    user_prompt = (
        "请从下面问答中提取薄弱知识点，并严格返回 JSON。\n"
        f"用户问题：{question}\n"
        f"助手回答：{reply}\n"
    )
    return system_prompt, user_prompt


def _infer_topic(question: str, reply: str) -> str:
    text = f"{question} {reply}".lower()
    topic_rules = [
        ("Vue 3", ["vue", "watch", "ref", "reactive", "组件", "响应式"]),
        ("Java", ["java", "jvm", "spring"]),
        ("Go", ["go", "goroutine", "channel", "协程"]),
        ("Rust", ["rust", "borrow", "ownership", "所有权"]),
        ("C语言", ["c语言", "指针", "malloc", "printf"]),
        ("Python", ["python", "flask", "django"]),
        ("数据库", ["sql", "mysql", "sqlite", "数据库"]),
        ("算法", ["算法", "复杂度", "链表", "数组", "排序"]),
    ]

    for topic, keywords in topic_rules:
        if any(keyword in text for keyword in keywords):
            return topic

    return "编程基础"


def _looks_like_learning_question(question: str, reply: str) -> bool:
    text = f"{question} {reply}".lower()

    if len(question.strip()) < 8:
        return False

    return any(keyword in text for keyword in _PROGRAMMING_KEYWORDS)


def _compact_text(text: str, max_length: int) -> str:
    normalized = _strip_markdown(text)
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 1] + "…"


def _strip_markdown(text: str) -> str:
    normalized = re.sub(r"```[\s\S]*?```", " ", text)
    normalized = re.sub(r"`([^`]*)`", r"\1", normalized)
    normalized = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", normalized)
    normalized = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", normalized)
    normalized = re.sub(r"#{1,6}\s*", " ", normalized)
    normalized = re.sub(r"[*_~>-]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _build_fallback_summary(question: str, reply: str) -> str:
    topic = _infer_topic(question, reply)
    cleaned_question = _compact_text(question, 36)

    if topic == "编程基础":
        return f"需要继续梳理“{cleaned_question}”这个知识点的概念、写法和最小示例。"

    return f"需要继续梳理 {topic} 中“{cleaned_question}”这个知识点的核心概念、常见写法和使用场景。"


def _build_rule_based_gap_item(question: str, reply: str) -> dict | None:
    text = f"{question} {reply}".lower()

    if "结构体" in text or "struct" in text:
        return {
            "topic": "C语言",
            "question": "结构体定义与成员访问",
            "summary": "结构体用于把多个字段组织成一个自定义类型；普通结构体变量用 . 访问成员，结构体指针用 -> 访问成员。",
            "mistakeType": "concept",
            "mistakeReason": "容易只记住 struct 的写法，却没有区分结构体变量和结构体指针这两种访问场景。",
            "improvementSuggestion": "写一个 Student 结构体，分别用变量 s 和指针 p 访问 name、age，对比 . 和 ->。",
        }

    if "指针" in text or "int *" in text or "int*" in text or "解引用" in text or "地址" in text:
        return {
            "topic": "C语言",
            "question": "指针变量、地址与解引用",
            "summary": "指针变量保存的是地址，不是普通整数值；通过 *p 解引用时，才是在访问这个地址指向的数据。",
            "mistakeType": "concept",
            "mistakeReason": "容易把指针变量本身、变量地址、地址里的值混成同一个概念。",
            "improvementSuggestion": "画出 int a = 10; int *p = &a; 的内存关系，并标注 a、&a、p、*p 分别表示什么。",
        }

    if "ref" in text or "reactive" in text or "响应式" in text:
        return {
            "topic": "Vue 3",
            "question": "ref 与 reactive 的使用边界",
            "summary": "ref 更适合基本类型或需要整体替换的值，reactive 更适合对象状态；解构 reactive 对象时要注意响应式丢失。",
            "mistakeType": "boundary",
            "mistakeReason": "容易把响应式 API 当成等价写法，没有先判断数据形态和后续更新方式。",
            "improvementSuggestion": "分别用 ref 和 reactive 写一个计数器与表单对象，再尝试解构 reactive 观察变化。",
        }

    if "props" in text or "emit" in text or "组件通信" in text or "v-model" in text:
        return {
            "topic": "Vue 3",
            "question": "组件通信的数据流",
            "summary": "Vue 组件通信通常是父组件通过 props 下发数据，子组件通过 emit 触发事件通知父组件更新。",
            "mistakeType": "logic",
            "mistakeReason": "容易在子组件里直接改父组件数据，忽略单向数据流和事件通知的边界。",
            "improvementSuggestion": "写一个父子组件示例：父组件传 title，子组件点击按钮 emit update 事件。",
        }

    if "goroutine" in text:
        return {
            "topic": "Go",
            "question": "goroutine 的执行与等待",
            "summary": "goroutine 是 Go 运行时调度的轻量任务；主函数结束后，未等待的 goroutine 也会随程序退出。",
            "mistakeType": "debugging",
            "mistakeReason": "容易只知道 go 关键字能启动并发，却忽略主流程需要等待并发任务完成。",
            "improvementSuggestion": "写两个 goroutine 打印内容，并用 sync.WaitGroup 等待它们结束。",
        }

    if "channel" in text:
        return {
            "topic": "Go",
            "question": "channel 的发送、接收与阻塞",
            "summary": "channel 用于 goroutine 之间通信；无缓冲 channel 的发送和接收需要同时准备好，否则会阻塞。",
            "mistakeType": "boundary",
            "mistakeReason": "容易把 channel 当成普通队列，忽略阻塞、关闭和消费方数量这些边界。",
            "improvementSuggestion": "写一个 producer/consumer 示例，分别观察无缓冲和有缓冲 channel 的行为。",
        }

    if "ownership" in text or "所有权" in text or "borrow" in text or "借用" in text:
        return {
            "topic": "Rust",
            "question": "所有权转移与借用",
            "summary": "Rust 通过所有权、借用和生命周期限制数据访问，避免悬垂引用和数据竞争。",
            "mistakeType": "concept",
            "mistakeReason": "容易只看变量是否还能使用，却没有先判断函数参数接收的是值、不可变引用还是可变引用。",
            "improvementSuggestion": "写三个函数参数示例：String、&String、&mut String，观察调用后原变量是否还能使用。",
        }

    return None


def _build_fallback_gap_item(question: str, reply: str) -> dict | None:
    if not _looks_like_learning_question(question, reply):
        return None

    rule_based_item = _build_rule_based_gap_item(question, reply)
    if rule_based_item:
        return rule_based_item

    topic = _infer_topic(question, reply)
    title = _compact_text(question, 48)
    summary = _build_fallback_summary(question, reply)

    return {
        "topic": topic,
        "question": title,
        "summary": summary,
        "mistakeType": "concept",
        "mistakeReason": "本轮提问暴露出该知识点还需要进一步梳理。",
        "improvementSuggestion": "回看本轮回答，补一个最小示例，并尝试用自己的话复述关键结论。",
    }


def _is_low_quality_gap_item(item: dict) -> bool:
    text = " ".join(
        str(item.get(key, ""))
        for key in ["question", "summary", "mistakeReason", "improvementSuggestion"]
    )
    generic_patterns = [
        "需要继续梳理",
        "本轮提问暴露",
        "回看本轮回答",
        "核心概念、常见写法和使用场景",
        "尝试用自己的话复述",
    ]
    return any(pattern in text for pattern in generic_patterns)


def _normalize_analysis(payload: dict) -> dict:
    summary = str(payload.get("summary", "")).strip()
    mistake_reason = str(payload.get("mistakeReason", "")).strip()
    improvement_suggestion = str(payload.get("improvementSuggestion", "")).strip()

    return {
        "summary": _compact_text(summary, 90) or "这个知识点还需要继续巩固。",
        "mistakeType": _normalize_type(str(payload.get("mistakeType", ""))),
        "mistakeReason": _compact_text(mistake_reason, 70) or "当前理解还不够稳定，需要进一步梳理。",
        "improvementSuggestion": _compact_text(improvement_suggestion, 70)
        or "回看概念、常见用法和一个最小示例。",
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


def list_mistakes(user_id: int | None = None) -> list[dict]:
    records = (
        MistakeRecord.query.filter(MistakeRecord.user_id == user_id)
        .order_by(MistakeRecord.sort_order.asc(), MistakeRecord.created_at.desc())
        .all()
    )
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

    user_id = entry.get("userId")
    max_sort_order = (
        db.session.query(func.max(MistakeRecord.sort_order)).filter(MistakeRecord.user_id == user_id).scalar() or 0
    )
    now = datetime.now(timezone.utc)

    record = MistakeRecord(
        user_id=entry.get("userId"),
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


def create_mistakes_from_assistant(question: str, reply: str, user_id: int | None = None) -> list[dict]:
    system_prompt, user_prompt = _build_gap_extraction_prompts(question=question, reply=reply)
    raw_reply = ""

    try:
        raw_reply = generate_reply(system_prompt=system_prompt, user_prompt=user_prompt)
        payload = _extract_json(raw_reply)
        raw_items = payload.get("items")
    except Exception as error:
        print(
            "[mistake-extraction] model json extraction failed",
            {
                "question": question,
                "detail": str(error),
                "rawReply": _compact_text(raw_reply, 500),
            },
        )
        fallback_item = _build_fallback_gap_item(question=question, reply=reply)
        raw_items = [fallback_item] if fallback_item else []

    if not isinstance(raw_items, list) or not raw_items:
        fallback_item = _build_fallback_gap_item(question=question, reply=reply)
        raw_items = [fallback_item] if fallback_item else []

    if not raw_items:
        return []

    max_sort_order = (
        db.session.query(func.max(MistakeRecord.sort_order)).filter(MistakeRecord.user_id == user_id).scalar() or 0
    )
    now = datetime.now(timezone.utc)
    records: list[MistakeRecord] = []

    for index, item in enumerate(raw_items[:2], start=1):
        if not isinstance(item, dict):
            continue

        if _is_low_quality_gap_item(item):
            replacement = _build_rule_based_gap_item(question=question, reply=reply)
            if not replacement:
                continue
            item = replacement

        try:
            normalized = _normalize_analysis(item)
        except ValueError:
            continue

        title = str(item.get("question", "")).strip()
        topic = str(item.get("topic", "")).strip() or "General"

        if not title:
            continue

        existing_record = MistakeRecord.query.filter_by(user_id=user_id, topic=topic, question=title).first()
        if existing_record:
            continue

        records.append(
            MistakeRecord(
                user_id=user_id,
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


def delete_mistake_record(record_id: int, user_id: int | None = None) -> None:
    record = MistakeRecord.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        raise ValueError("知识点记录不存在")

    db.session.delete(record)
    db.session.commit()
    _normalize_sort_order(user_id=user_id)


def update_mistake_record(record_id: int, entry: dict, user_id: int | None = None) -> dict:
    record = MistakeRecord.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        raise ValueError("知识点记录不存在")

    topic = (entry.get("topic") or "").strip()
    question = (entry.get("question") or "").strip()
    reference_answer = (entry.get("referenceAnswer") or "").strip()
    user_answer = (entry.get("userAnswer") or "").strip()
    mistake_type = (entry.get("mistakeType") or record.mistake_type).strip()

    if not topic or not question or not reference_answer:
        raise ValueError("topic、question、referenceAnswer 字段不能为空")

    record.topic = topic
    record.question = question
    record.user_answer = user_answer
    record.reference_answer = reference_answer
    record.mistake_type = _normalize_type(mistake_type)
    record.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    return record.to_dict()


def move_mistake_record(record_id: int, direction: str, user_id: int | None = None) -> list[dict]:
    record = MistakeRecord.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        raise ValueError("知识点记录不存在")

    if direction not in {"up", "down"}:
        raise ValueError("direction 只能是 up 或 down")

    if direction == "up":
        neighbor = (
            MistakeRecord.query.filter(MistakeRecord.sort_order < record.sort_order)
            .filter(MistakeRecord.user_id == user_id)
            .order_by(MistakeRecord.sort_order.desc())
            .first()
        )
    else:
        neighbor = (
            MistakeRecord.query.filter(MistakeRecord.sort_order > record.sort_order)
            .filter(MistakeRecord.user_id == user_id)
            .order_by(MistakeRecord.sort_order.asc())
            .first()
        )

    if not neighbor:
        return list_mistakes(user_id=user_id)

    record.sort_order, neighbor.sort_order = neighbor.sort_order, record.sort_order
    now = datetime.now(timezone.utc)
    record.updated_at = now
    neighbor.updated_at = now
    db.session.commit()
    return list_mistakes(user_id=user_id)


def reorder_mistake_records(ordered_ids: list[int], user_id: int | None = None) -> list[dict]:
    if not ordered_ids:
        raise ValueError("orderedIds 不能为空")

    records = MistakeRecord.query.filter(MistakeRecord.id.in_(ordered_ids), MistakeRecord.user_id == user_id).all()

    if len(records) != len(set(ordered_ids)):
        raise ValueError("orderedIds 中包含无效记录")

    record_map = {record.id: record for record in records}
    now = datetime.now(timezone.utc)

    for index, record_id in enumerate(ordered_ids, start=1):
        record = record_map[record_id]
        record.sort_order = index
        record.updated_at = now

    db.session.commit()
    return list_mistakes(user_id=user_id)


def _normalize_sort_order(user_id: int | None = None) -> None:
    records = (
        MistakeRecord.query.filter(MistakeRecord.user_id == user_id)
        .order_by(MistakeRecord.sort_order.asc(), MistakeRecord.id.asc())
        .all()
    )

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
