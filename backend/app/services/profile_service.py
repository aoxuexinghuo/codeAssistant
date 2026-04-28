from collections import Counter
from datetime import datetime, timezone

from sqlalchemy import func

from ..extensions import db
from ..models import ConversationHistory, MistakeRecord, UserProfile

DEFAULT_PROFILE = {
    "nickname": "学习者",
    "level": "初级",
    "focus": "C语言",
    "goal": "课程学习",
    "answerStyle": "简洁直接",
    "weakPreference": "自动记录",
}

_TOPIC_KEYWORDS = {
    "C语言": ["c语言", "指针", "结构体", "malloc", "printf", "数组"],
    "Java": ["java", "jvm", "spring", "集合", "面向对象"],
    "Python": ["python", "flask", "django", "列表", "字典"],
    "Go": ["go", "goroutine", "channel", "协程"],
    "Rust": ["rust", "所有权", "借用", "result"],
    "Vue 3": ["vue", "ref", "reactive", "组件", "响应式", "watch"],
    "算法": ["算法", "复杂度", "链表", "排序", "二分"],
}


def get_or_create_profile(user_id: int | None = None) -> dict:
    profile = UserProfile.query.filter(UserProfile.user_id == user_id).order_by(UserProfile.id.asc()).first()

    if profile:
        return profile.to_dict()

    now = datetime.now(timezone.utc)
    profile = UserProfile(
        nickname=DEFAULT_PROFILE["nickname"],
        user_id=user_id,
        level=DEFAULT_PROFILE["level"],
        focus=DEFAULT_PROFILE["focus"],
        goal=DEFAULT_PROFILE["goal"],
        answer_style=DEFAULT_PROFILE["answerStyle"],
        weak_preference=DEFAULT_PROFILE["weakPreference"],
        created_at=now,
        updated_at=now,
    )
    db.session.add(profile)
    db.session.commit()
    return profile.to_dict()


def update_profile(payload: dict, user_id: int | None = None) -> dict:
    get_or_create_profile(user_id=user_id)
    profile = UserProfile.query.filter(UserProfile.user_id == user_id).order_by(UserProfile.id.asc()).first()
    assert profile is not None

    field_map = {
        "nickname": "nickname",
        "level": "level",
        "focus": "focus",
        "goal": "goal",
        "answerStyle": "answer_style",
        "weakPreference": "weak_preference",
    }

    for source, target in field_map.items():
        value = str(payload.get(source, "")).strip()
        if value:
            setattr(profile, target, value[:80])

    profile.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return profile.to_dict()


def reset_profile(user_id: int | None = None) -> dict:
    get_or_create_profile(user_id=user_id)
    profile = UserProfile.query.filter(UserProfile.user_id == user_id).order_by(UserProfile.id.asc()).first()
    assert profile is not None

    profile.nickname = DEFAULT_PROFILE["nickname"]
    profile.level = DEFAULT_PROFILE["level"]
    profile.focus = DEFAULT_PROFILE["focus"]
    profile.goal = DEFAULT_PROFILE["goal"]
    profile.answer_style = DEFAULT_PROFILE["answerStyle"]
    profile.weak_preference = DEFAULT_PROFILE["weakPreference"]
    profile.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return profile.to_dict()


def get_profile_for_prompt(user_id: int | None = None) -> dict:
    return get_or_create_profile(user_id=user_id)


def build_profile_insights(user_id: int | None = None) -> dict:
    profile = get_or_create_profile(user_id=user_id)
    question_count = ConversationHistory.query.filter(ConversationHistory.user_id == user_id).count()
    mistake_count = MistakeRecord.query.filter(MistakeRecord.user_id == user_id).count()

    topic_distribution = _build_topic_distribution(user_id=user_id)
    mode_distribution = _build_mode_distribution(user_id=user_id)
    recent_weak_points = [
        {
            "id": record.id,
            "title": record.question,
            "topic": record.topic,
            "type": record.mistake_type,
        }
        for record in MistakeRecord.query.filter(MistakeRecord.user_id == user_id)
        .order_by(MistakeRecord.created_at.desc())
        .limit(5)
        .all()
    ]

    return {
        "questionCount": question_count,
        "mistakeCount": mistake_count,
        "topicDistribution": topic_distribution,
        "modeDistribution": mode_distribution,
        "recentWeakPoints": recent_weak_points,
        "abilityScores": _build_ability_scores(topic_distribution, mode_distribution, mistake_count),
        "strategyTips": _build_strategy_tips(profile, topic_distribution, recent_weak_points),
    }


def _build_topic_distribution(user_id: int | None = None) -> list[dict]:
    counter: Counter[str] = Counter()

    for topic, count in (
        db.session.query(MistakeRecord.topic, func.count(MistakeRecord.id))
        .filter(MistakeRecord.user_id == user_id)
        .group_by(MistakeRecord.topic)
    ):
        counter[topic or "编程基础"] += count * 2

    for record in (
        ConversationHistory.query.filter(ConversationHistory.user_id == user_id)
        .order_by(ConversationHistory.created_at.desc())
        .limit(80)
        .all()
    ):
        counter[_infer_topic(record.question)] += 1

    total = sum(counter.values())
    if not total:
        return []

    return [
        {"name": name, "value": round(count / total * 100)}
        for name, count in counter.most_common(6)
    ]


def _build_mode_distribution(user_id: int | None = None) -> list[dict]:
    rows = (
        db.session.query(ConversationHistory.mode_label, func.count(ConversationHistory.id))
        .filter(ConversationHistory.user_id == user_id)
        .group_by(ConversationHistory.mode_label)
        .all()
    )
    total = sum(count for _, count in rows)

    if not total:
        return []

    return [
        {"name": mode_label or "未知模式", "value": round(count / total * 100)}
        for mode_label, count in rows
    ]


def _infer_topic(text: str) -> str:
    lowered = (text or "").lower()

    for topic, keywords in _TOPIC_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return topic

    return "编程基础"


def _build_ability_scores(topic_distribution: list[dict], mode_distribution: list[dict], mistake_count: int) -> list[dict]:
    topic_map = {item["name"]: item["value"] for item in topic_distribution}
    mode_map = {item["name"]: item["value"] for item in mode_distribution}
    penalty = min(24, mistake_count * 3)

    scores = {
        "基础语法": 72 - penalty // 2,
        "调试能力": 52 + mode_map.get("调试模式", 0) // 2 - penalty // 4,
        "算法思维": 50 + topic_map.get("算法", 0) // 3,
        "框架使用": 48 + topic_map.get("Vue 3", 0) // 2,
        "代码表达": 58 + mode_map.get("面试模式", 0) // 3,
    }

    return [
        {"name": name, "value": max(30, min(95, value))}
        for name, value in scores.items()
    ]


def _build_strategy_tips(profile: dict, topic_distribution: list[dict], recent_weak_points: list[dict]) -> list[str]:
    focus = profile.get("focus") or "当前方向"
    tips = [
        f"回答时优先结合 {focus} 的知识背景。",
        _answer_style_tip(profile.get("answerStyle", "")),
    ]

    if recent_weak_points:
        topics = "、".join(dict.fromkeys(item["topic"] for item in recent_weak_points[:3]))
        tips.append(f"最近薄弱点集中在 {topics}，答疑时会更注意相关概念。")
    elif topic_distribution:
        tips.append(f"最近关注较多的是 {topic_distribution[0]['name']}，学习资料会优先贴近该方向。")
    else:
        tips.append("暂无足够行为数据，先按照基础偏好调整回答。")

    return tips[:3]


def _answer_style_tip(answer_style: str) -> str:
    if "举例" in answer_style:
        return "回答会尽量给一个最小示例。"
    if "引导" in answer_style:
        return "回答会多用提示和追问引导你自己推理。"
    if "代码" in answer_style:
        return "回答会减少完整代码，更强调思路。"
    return "回答会保持简洁，先给结论再补说明。"
