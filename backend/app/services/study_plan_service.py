import json
from datetime import datetime, timezone

from ..extensions import db
from ..models import StudyPlan
from .knowledge_service import get_knowledge_item
from .llm_service import generate_reply
from .profile_service import build_profile_insights, get_profile_for_prompt


def list_study_plans(user_id: int | None = None) -> list[dict]:
    records = (
        StudyPlan.query.filter(StudyPlan.user_id == user_id)
        .order_by(StudyPlan.created_at.desc())
        .limit(20)
        .all()
    )
    return [_study_plan_to_dict(record) for record in records]


def delete_study_plan(plan_id: int, user_id: int | None = None) -> None:
    record = StudyPlan.query.filter_by(id=plan_id, user_id=user_id).first()

    if not record:
        raise ValueError("学习计划不存在")

    db.session.delete(record)
    db.session.commit()


def update_study_plan_step(plan_id: int, step_index: int, completed: bool, user_id: int | None = None) -> dict:
    record = StudyPlan.query.filter_by(id=plan_id, user_id=user_id).first()

    if not record:
        raise ValueError("学习计划不存在")

    plan = _load_plan_json(record)
    steps = plan.get("steps")

    if not isinstance(steps, list) or step_index < 0 or step_index >= len(steps):
        raise ValueError("学习任务不存在")

    for step in steps:
        if isinstance(step, dict):
            step["completed"] = bool(step.get("completed", False))

    steps[step_index]["completed"] = bool(completed)
    record.plan_json = json.dumps(plan, ensure_ascii=False)
    record.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    return _study_plan_to_dict(record)


def generate_study_plan(resource_files: list[str], user_id: int | None = None) -> dict:
    if not resource_files:
        raise ValueError("请至少选择 1 项学习资料")

    unique_files = list(dict.fromkeys(str(item).strip() for item in resource_files if str(item).strip()))[:6]
    resources = [get_knowledge_item(file_name, user_id=user_id) for file_name in unique_files]
    profile = get_profile_for_prompt(user_id=user_id)
    insights = build_profile_insights(user_id=user_id)

    try:
        plan = _generate_plan_with_model(resources=resources, profile=profile, insights=insights)
        plan["generationMode"] = "model"
    except Exception as error:
        print("[study-plan] model generation fallback", {"detail": str(error)})
        plan = _build_fallback_plan(resources=resources, profile=profile)
        plan["generationMode"] = "fallback"

    now = datetime.now(timezone.utc)
    record = StudyPlan(
        user_id=user_id,
        title=plan["title"],
        goal=plan["goal"],
        duration=plan["duration"],
        resource_files=json.dumps(unique_files, ensure_ascii=False),
        plan_json=json.dumps(plan, ensure_ascii=False),
        created_at=now,
        updated_at=now,
    )
    db.session.add(record)
    db.session.commit()
    return _study_plan_to_dict(record)


def _load_plan_json(record: StudyPlan) -> dict:
    try:
        plan = json.loads(record.plan_json)
    except json.JSONDecodeError:
        plan = {}

    return plan if isinstance(plan, dict) else {}


def _study_plan_to_dict(record: StudyPlan) -> dict:
    data = record.to_dict()
    plan = data.get("plan") if isinstance(data.get("plan"), dict) else {}
    steps = plan.get("steps")

    if not isinstance(steps, list):
        steps = []

    normalized_steps = []
    completed_count = 0

    for step in steps:
        if not isinstance(step, dict):
            continue

        normalized_step = {
            **step,
            "completed": bool(step.get("completed", False)),
        }
        completed_count += 1 if normalized_step["completed"] else 0
        normalized_steps.append(normalized_step)

    plan["steps"] = normalized_steps
    plan["progress"] = {
        "total": len(normalized_steps),
        "completed": completed_count,
        "percent": round((completed_count / len(normalized_steps)) * 100) if normalized_steps else 0,
    }
    data["plan"] = plan
    return data


def _generate_plan_with_model(resources: list[dict], profile: dict, insights: dict) -> dict:
    system_prompt = (
        "你是一个编程学习规划助手。"
        "请根据用户画像、近期薄弱点和所选资料生成简洁学习计划。"
        "不要写空泛任务，例如“阅读资料并整理核心概念”。"
        "每个 task 必须包含具体动作、练习产物和验收标准。"
        "例如 Vue 响应式要具体到 ref/reactive/computed/watch，组件通信要具体到 props/emit/v-model。"
        "只返回 JSON，不要 Markdown，不要解释。"
        "JSON 字段必须是 title, goal, duration, steps, reviewTips。"
        "steps 每项必须包含 title, resource, task, checkpoints。"
        "steps 最多 5 项，每项 checkpoints 最多 3 条。"
    )
    user_prompt = json.dumps(
        {
            "profile": profile,
            "recentWeakPoints": insights.get("recentWeakPoints", []),
            "resources": [
                {
                    "file": item["file"],
                    "title": item["title"],
                    "topic": item["topic"],
                    "level": item["level"],
                    "tags": item["tags"],
                    "summary": item["summary"],
                }
                for item in resources
            ],
        },
        ensure_ascii=False,
    )
    raw_reply = generate_reply(system_prompt=system_prompt, user_prompt=user_prompt)
    plan = _extract_json(raw_reply)
    return _normalize_plan(plan, resources)


def _extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("模型没有返回合法 JSON")

    return json.loads(text[start : end + 1])


def _normalize_plan(plan: dict, resources: list[dict]) -> dict:
    fallback = _build_fallback_plan(resources, {})
    steps = plan.get("steps")

    if not isinstance(steps, list) or not steps:
        steps = fallback["steps"]

    normalized_steps = []
    for index, step in enumerate(steps[:5]):
        resource = str(step.get("resource") or resources[min(index, len(resources) - 1)]["file"])
        checkpoints = step.get("checkpoints") if isinstance(step.get("checkpoints"), list) else []
        normalized_steps.append(
            {
                "title": str(step.get("title") or resources[min(index, len(resources) - 1)]["title"])[:80],
                "resource": resource,
                "task": str(step.get("task") or "阅读资料并整理 3 条关键结论。")[:160],
                "checkpoints": [str(item)[:80] for item in checkpoints[:3]] or ["能复述核心概念"],
            }
        )

    review_tips = plan.get("reviewTips") if isinstance(plan.get("reviewTips"), list) else fallback["reviewTips"]
    return {
        "title": str(plan.get("title") or fallback["title"])[:120],
        "goal": str(plan.get("goal") or fallback["goal"])[:240],
        "duration": str(plan.get("duration") or fallback["duration"])[:40],
        "steps": normalized_steps,
        "reviewTips": [str(item)[:100] for item in review_tips[:4]],
        "generationMode": str(plan.get("generationMode") or "model"),
    }


def _build_fallback_plan(resources: list[dict], profile: dict) -> dict:
    focus = profile.get("focus") or resources[0]["topic"]
    steps = [_build_resource_step(resource, index) for index, resource in enumerate(resources[:5], start=1)]
    return {
        "title": f"{focus} 学习补强计划",
        "goal": _build_goal(resources=resources, focus=focus),
        "duration": f"{max(1, len(steps))} 天",
        "steps": steps,
        "reviewTips": [
            "每完成一步，用 3 句话记录：学会了什么、卡在哪里、下一步验证什么。",
            "把不能独立复述的概念加入薄弱点卡片。",
            "完成计划后回到智能答疑，用自己的例子提一个追问。",
        ],
        "generationMode": "fallback",
    }


def _build_goal(resources: list[dict], focus: str) -> str:
    titles = "、".join(resource["title"] for resource in resources[:3])
    return f"围绕 {titles} 建立 {focus} 的可操作知识链：先理解关键概念，再完成最小练习，最后整理易错点。"


def _build_resource_step(resource: dict, index: int) -> dict:
    title = resource["title"]
    text = f"{title} {' '.join(resource.get('tags', []))} {resource.get('summary', '')}".lower()

    if "vue" in text and ("响应式" in text or "reactive" in text or "ref" in text):
        return {
            "title": f"拆清 {title} 的响应式边界",
            "resource": resource["file"],
            "task": "写一个小例子分别使用 ref、reactive、computed、watch，并记录它们各自适合的场景。",
            "checkpoints": [
                "能解释 ref 和 reactive 的区别",
                "能说明 computed 与 watch 的使用场景",
                "能说出 reactive 解构失效的原因",
            ],
        }

    if "vue" in text and ("组件" in text or "props" in text or "emit" in text):
        return {
            "title": f"完成 {title} 的通信练习",
            "resource": resource["file"],
            "task": "做一个父子组件小练习：父组件传入标题，子组件点击按钮后 emit 通知父组件更新状态。",
            "checkpoints": [
                "能写出 props 接收数据",
                "能用 emit 向父组件传事件",
                "能说明 v-model 组件封装的本质",
            ],
        }

    if "指针" in text or "pointer" in text:
        return {
            "title": f"用最小程序验证 {title}",
            "resource": resource["file"],
            "task": "写一个变量、一个指针和一次函数传参，分别标注 &、*、地址和值的含义。",
            "checkpoints": [
                "能区分地址和值",
                "能解释 & 和 *",
                "能说明为什么指针能修改外部变量",
            ],
        }

    if "结构体" in text or "struct" in text:
        return {
            "title": f"用结构化数据练习 {title}",
            "resource": resource["file"],
            "task": "定义一个 Student 结构体，完成初始化、成员访问和一个结构体指针访问示例。",
            "checkpoints": [
                "能写出 struct 定义",
                "能区分 . 和 ->",
                "能说明 typedef 的作用",
            ],
        }

    if "goroutine" in text:
        return {
            "title": f"跑通 {title} 的并发例子",
            "resource": resource["file"],
            "task": "写两个 goroutine 打印不同内容，用 WaitGroup 等待它们结束。",
            "checkpoints": [
                "能说明 goroutine 和线程的区别",
                "能解释主函数提前结束的问题",
                "能使用 WaitGroup 等待任务",
            ],
        }

    if "channel" in text:
        return {
            "title": f"验证 {title} 的通信模型",
            "resource": resource["file"],
            "task": "写一个 producer/consumer 示例，用 channel 发送数据，并尝试关闭 channel。",
            "checkpoints": [
                "能区分发送和接收",
                "能解释无缓冲 channel 的阻塞",
                "能说明 close 的作用",
            ],
        }

    if "所有权" in text or "ownership" in text:
        return {
            "title": f"画出 {title} 的所有权流向",
            "resource": resource["file"],
            "task": "写一个 move、一个不可变借用和一个可变借用示例，并标注变量什么时候还能继续使用。",
            "checkpoints": [
                "能说明 move 发生的时机",
                "能区分借用和所有权转移",
                "能复述可变借用限制",
            ],
        }

    if "复杂度" in text or "算法" in text:
        return {
            "title": f"用代码判断 {title}",
            "resource": resource["file"],
            "task": "找 3 段简单循环代码，分别判断 O(1)、O(n)、O(n^2)，并写出判断依据。",
            "checkpoints": [
                "能看出循环次数和 n 的关系",
                "能区分时间复杂度和空间复杂度",
                "能解释双层循环为什么常见是 O(n^2)",
            ],
        }

    return {
        "title": f"完成 {title} 的小任务",
        "resource": resource["file"],
        "task": f"围绕《{title}》写一个最小示例，并整理 2 个使用场景和 1 个易错点。",
        "checkpoints": [
            "能复述核心概念",
            "能写出一个最小示例",
            "能说明一个常见误区",
        ],
    }
