_mode_catalog = [
    {
        "key": "debug",
        "label": "调试模式",
        "description": "先确认上下文，再给排查步骤和验证方法。",
        "placeholder": "例如：Vue 页面空白，控制台报 Cannot read properties of undefined",
        "tone": "先追问关键信息，再给最短排查路径",
    },
    {
        "key": "learning",
        "label": "学习模式",
        "description": "解释核心概念，配一个短例子或练习建议。",
        "placeholder": "例如：帮我理解 Vue 3 的 ref 和 reactive 区别",
        "tone": "先讲结论，再补一个简短例子",
    },
    {
        "key": "interview",
        "label": "面试模式",
        "description": "给思路、关键词和答题顺序，默认不直接给完整代码。",
        "placeholder": "例如：手写一个 LRU 缓存怎么设计",
        "tone": "提示为主，控制答案完整度",
    },
]


def _build_debug_fallback(question: str) -> str:
    return "\n".join(
        [
            "需要确认：",
            "1. 完整报错",
            "2. 复现步骤",
            "3. 相关代码片段",
        ]
    )


def _build_learning_fallback(question: str) -> str:
    return "\n".join(
        [
            "一句话理解：",
            "先抓核心概念，再看最小例子。",
            "",
            "你可以继续补充具体代码，我再按代码拆解。",
        ]
    )


def _build_interview_fallback(question: str) -> str:
    return "\n".join(
        [
            "答题提示：",
            "1. 先说目标和约束",
            "2. 再说核心思路",
            "3. 最后补边界和复杂度",
        ]
    )


_reply_builders = {
    "debug": _build_debug_fallback,
    "learning": _build_learning_fallback,
    "interview": _build_interview_fallback,
}


def list_modes() -> list[dict]:
    return _mode_catalog


def get_mode_by_key(mode: str) -> dict | None:
    return next((item for item in _mode_catalog if item["key"] == mode), None)


def build_fallback_reply(mode: str, question: str) -> str | None:
    builder = _reply_builders.get(mode)
    return builder(question.strip()) if builder else None
