_mode_catalog = [
    {
        "key": "debug",
        "label": "调试模式",
        "description": "先追问信息，再输出排查步骤和验证方法。",
        "placeholder": "例如：Vue 页面空白，控制台报错 Cannot read properties of undefined",
        "tone": "结构化、谨慎、强调复现与定位",
    },
    {
        "key": "learning",
        "label": "学习模式",
        "description": "更注重概念解释、示例拆解和练习建议。",
        "placeholder": "例如：帮我理解 Vue 3 的 ref 和 reactive 区别",
        "tone": "耐心、循序渐进、强调原理",
    },
    {
        "key": "interview",
        "label": "面试模式",
        "description": "只给思路提示，默认不直接给完整代码。",
        "placeholder": "例如：手写一个 LRU 缓存怎么设计",
        "tone": "克制、面试导向、强调思路表达",
    },
]


def _build_debug_fallback(question: str) -> str:
    return "\n".join(
        [
            "先补齐上下文，再动手排查：",
            f"1. 现象描述：{question or '未提供具体问题'}",
            "2. 需要补充：完整报错、复现步骤、最近改动、运行环境。",
            "",
            "建议排查顺序：",
            "1. 先定位第一条报错出现的文件和行号。",
            "2. 再检查输入数据、异步返回值、props 和状态初始化。",
            "3. 用最小复现代码缩小范围，确认是否为单点改动导致。",
            "4. 修复后补一条验证路径，避免回归。",
        ]
    )


def _build_learning_fallback(question: str) -> str:
    return "\n".join(
        [
            f"问题主题：{question or '未提供具体问题'}",
            "",
            "先讲核心原理：",
            "把问题拆成“概念是什么、为什么这样设计、实际怎么用”三层理解。",
            "",
            "再看一个最小示例：",
            "先实现最基础版本，再观察数据流、状态变化和边界条件。",
            "",
            "练习建议：",
            "1. 自己复写一个最小例子。",
            "2. 改动一个关键条件，观察结果变化。",
            "3. 用自己的话总结适用场景和常见误区。",
        ]
    )


def _build_interview_fallback(question: str) -> str:
    return "\n".join(
        [
            f"面试题方向：{question or '未提供具体问题'}",
            "",
            "回答提示：",
            "1. 先说目标复杂度和设计约束。",
            "2. 再给核心数据结构或模块拆分。",
            "3. 最后补边界条件、异常情况和优化点。",
            "",
            "这里先不给完整代码。你可以先写思路或伪代码，我再继续追问和纠正。",
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
