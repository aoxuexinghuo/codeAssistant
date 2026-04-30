import json

from flask import Blueprint, Response, jsonify, request, stream_with_context

from .services.auth_service import get_user_by_token, login_user, register_user
from .services.history_service import add_history_entry, clear_history, delete_history_entry, list_history
from .services.knowledge_service import create_user_knowledge_item, get_knowledge_item, list_knowledge_items
from .services.llm_service import generate_reply, stream_reply
from .services.mistake_service import (
    create_mistake_record,
    create_mistakes_from_assistant,
    delete_mistake_record,
    list_mistakes,
    move_mistake_record,
    reorder_mistake_records,
    update_mistake_record,
)
from .services.mode_service import build_fallback_reply, get_mode_by_key, list_modes
from .services.prompt_service import build_prompts
from .services.profile_service import build_profile_insights, get_or_create_profile, get_profile_for_prompt, reset_profile, update_profile
from .services.rag_service import generate_rag_reply, rebuild_rag_index, search_rag_documents, stream_rag_reply
from .services.study_plan_service import (
    delete_study_plan,
    generate_study_plan,
    generate_study_plan_summary,
    list_study_plans,
    update_study_plan_step,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _current_user():
    return get_user_by_token(request.headers.get("X-User-Token"))


def _current_user_id() -> int | None:
    user = _current_user()
    return user.id if user else None


@api_bp.route("/auth/register", methods=["POST"])
def register():
    body = request.get_json(silent=True) or {}

    try:
        user = register_user(body.get("username", ""), body.get("password", ""))
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 400

    return jsonify({"ok": True, "data": user}), 201


@api_bp.route("/auth/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}

    try:
        user = login_user(body.get("username", ""), body.get("password", ""))
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 400

    return jsonify({"ok": True, "data": user})


@api_bp.route("/modes", methods=["GET"])
def get_modes():
    return jsonify({"ok": True, "data": list_modes()})


@api_bp.route("/profile", methods=["GET"])
def get_profile():
    return jsonify({"ok": True, "data": get_or_create_profile(user_id=_current_user_id())})


@api_bp.route("/profile", methods=["PUT"])
def save_profile():
    body = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "data": update_profile(body, user_id=_current_user_id())})


@api_bp.route("/profile/reset", methods=["POST"])
def restore_profile():
    return jsonify({"ok": True, "data": reset_profile(user_id=_current_user_id())})


@api_bp.route("/profile/insights", methods=["GET"])
def get_profile_insights():
    return jsonify({"ok": True, "data": build_profile_insights(user_id=_current_user_id())})


@api_bp.route("/knowledge", methods=["GET"])
def get_knowledge():
    return jsonify({"ok": True, "data": list_knowledge_items(user_id=_current_user_id())})


@api_bp.route("/knowledge", methods=["POST"])
def upload_knowledge():
    user = _current_user()
    if not user:
        return jsonify({"ok": False, "message": "请先登录后再上传资料"}), 401

    body = request.get_json(silent=True) or {}

    try:
        item = create_user_knowledge_item(user.id, body)
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 400

    return jsonify({"ok": True, "data": item}), 201


@api_bp.route("/knowledge/<path:file_name>", methods=["GET"])
def get_knowledge_detail(file_name: str):
    try:
        item = get_knowledge_item(file_name, user_id=_current_user_id())
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 404

    return jsonify({"ok": True, "data": item})


@api_bp.route("/study-plans", methods=["GET"])
def get_study_plans():
    return jsonify({"ok": True, "data": list_study_plans(user_id=_current_user_id())})


@api_bp.route("/study-plans/generate", methods=["POST"])
def create_study_plan():
    body = request.get_json(silent=True) or {}
    resource_files = body.get("resourceFiles")

    if not isinstance(resource_files, list):
        return jsonify({"ok": False, "message": "resourceFiles 必须是数组"}), 400

    try:
        plan = generate_study_plan(resource_files=resource_files, user_id=_current_user_id())
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 400
    except Exception as error:
        return jsonify({"ok": False, "message": "学习计划生成失败", "detail": str(error)}), 502

    return jsonify({"ok": True, "data": plan}), 201


@api_bp.route("/study-plans/<int:plan_id>", methods=["DELETE"])
def remove_study_plan(plan_id: int):
    try:
        delete_study_plan(plan_id=plan_id, user_id=_current_user_id())
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 404

    return jsonify({"ok": True, "data": []})


@api_bp.route("/study-plans/<int:plan_id>/steps/<int:step_index>", methods=["PUT"])
def save_study_plan_step(plan_id: int, step_index: int):
    body = request.get_json(silent=True) or {}

    try:
        result = update_study_plan_step(
            plan_id=plan_id,
            step_index=step_index,
            completed=bool(body.get("completed", False)),
            user_id=_current_user_id(),
        )
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 404

    return jsonify({"ok": True, "data": result})


@api_bp.route("/study-plans/<int:plan_id>/summary", methods=["POST"])
def create_study_plan_summary(plan_id: int):
    try:
        plan = generate_study_plan_summary(plan_id=plan_id, user_id=_current_user_id())
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 400
    except Exception as error:
        return jsonify({"ok": False, "message": "阶段总结生成失败", "detail": str(error)}), 502

    return jsonify({"ok": True, "data": plan})


@api_bp.route("/history", methods=["GET"])
def get_history():
    keyword = request.args.get("q", "").strip()
    mode = request.args.get("mode", "").strip()
    limit = request.args.get("limit", default=50, type=int)
    return jsonify({"ok": True, "data": list_history(keyword=keyword, mode=mode, limit=limit, user_id=_current_user_id())})


@api_bp.route("/history", methods=["POST"])
def create_history():
    body = request.get_json(silent=True) or {}
    mode = body.get("mode")
    mode_label = body.get("modeLabel") or mode
    question = body.get("question")
    reply = body.get("reply")

    if not mode or not question or not reply:
        return jsonify({"ok": False, "message": "mode、question、reply 字段不能为空"}), 400

    record = add_history_entry(
        {
            "mode": mode,
            "modeLabel": mode_label,
            "question": question,
            "reply": reply,
            "userId": _current_user_id(),
        }
    )
    return jsonify({"ok": True, "data": record}), 201


@api_bp.route("/history", methods=["DELETE"])
def remove_history():
    clear_history(user_id=_current_user_id())
    return jsonify({"ok": True, "data": []})


@api_bp.route("/history/<int:record_id>", methods=["DELETE"])
def remove_history_entry(record_id: int):
    try:
        delete_history_entry(record_id, user_id=_current_user_id())
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 404

    return jsonify({"ok": True, "data": []})


@api_bp.route("/mistakes", methods=["GET"])
def get_mistakes():
    return jsonify({"ok": True, "data": list_mistakes(user_id=_current_user_id())})


@api_bp.route("/mistakes", methods=["POST"])
def create_mistake():
    body = request.get_json(silent=True) or {}
    topic = (body.get("topic") or "").strip()
    question = (body.get("question") or "").strip()
    user_answer = (body.get("userAnswer") or "").strip()
    reference_answer = (body.get("referenceAnswer") or "").strip()
    note = (body.get("note") or "").strip()

    has_manual_card_payload = topic and question and not user_answer and not reference_answer
    has_full_payload = topic and question and user_answer and reference_answer

    if not has_manual_card_payload and not has_full_payload:
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "请提供 topic、question，以及可选的 note；或提供 userAnswer 与 referenceAnswer。",
                }
            ),
            400,
        )

    try:
        record = create_mistake_record(
            {
                "topic": topic,
                "question": question,
                "userAnswer": user_answer,
                "referenceAnswer": reference_answer,
                "note": note,
                "userId": _current_user_id(),
            }
        )
    except Exception as error:
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "知识点卡片自动整理失败",
                    "detail": str(error),
                }
            ),
            502,
        )

    return jsonify({"ok": True, "data": record}), 201


@api_bp.route("/mistakes/from-assistant", methods=["POST"])
def create_mistakes_from_chat():
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()
    reply = (body.get("reply") or "").strip()

    if not question or not reply:
        return jsonify({"ok": False, "message": "question、reply 字段不能为空"}), 400

    try:
        records = create_mistakes_from_assistant(question=question, reply=reply, user_id=_current_user_id())
    except Exception as error:
        detail = str(error)
        print("[mistake-extraction] failed", {"question": question, "detail": detail})
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "从答疑结果提炼知识点失败",
                    "detail": detail,
                }
            ),
            502,
        )

    return jsonify({"ok": True, "data": records}), 201


@api_bp.route("/mistakes/<int:record_id>", methods=["DELETE"])
def remove_mistake(record_id: int):
    try:
        delete_mistake_record(record_id, user_id=_current_user_id())
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 404

    return jsonify({"ok": True, "data": []})


@api_bp.route("/mistakes/<int:record_id>", methods=["PUT"])
def update_mistake(record_id: int):
    body = request.get_json(silent=True) or {}

    try:
        record = update_mistake_record(record_id=record_id, entry=body, user_id=_current_user_id())
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 400

    return jsonify({"ok": True, "data": record})


@api_bp.route("/mistakes/<int:record_id>/move", methods=["POST"])
def move_mistake(record_id: int):
    body = request.get_json(silent=True) or {}
    direction = (body.get("direction") or "").strip()

    try:
        records = move_mistake_record(record_id=record_id, direction=direction, user_id=_current_user_id())
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 400

    return jsonify({"ok": True, "data": records})


@api_bp.route("/mistakes/reorder", methods=["POST"])
def reorder_mistakes():
    body = request.get_json(silent=True) or {}
    ordered_ids = body.get("orderedIds")

    if not isinstance(ordered_ids, list):
        return jsonify({"ok": False, "message": "orderedIds 必须是数组"}), 400

    try:
        records = reorder_mistake_records([int(item) for item in ordered_ids], user_id=_current_user_id())
    except ValueError as error:
        return jsonify({"ok": False, "message": str(error)}), 400

    return jsonify({"ok": True, "data": records})


@api_bp.route("/rag/rebuild", methods=["POST"])
def rebuild_rag():
    try:
        result = rebuild_rag_index()
    except Exception as error:
        return jsonify({"ok": False, "message": "知识库索引重建失败", "detail": str(error)}), 500

    return jsonify({"ok": True, "data": result})


@api_bp.route("/rag/search", methods=["GET"])
def search_rag():
    question = (request.args.get("q") or "").strip()

    if not question:
        return jsonify({"ok": False, "message": "q 参数不能为空"}), 400

    try:
        documents = search_rag_documents(question, user_id=_current_user_id())
    except Exception as error:
        return jsonify({"ok": False, "message": "知识库检索失败", "detail": str(error)}), 500

    return jsonify({"ok": True, "data": documents})


@api_bp.route("/rag/reply", methods=["POST"])
def create_rag_reply():
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()

    if not question:
        return jsonify({"ok": False, "message": "question 字段不能为空"}), 400

    try:
        result = generate_rag_reply(question, user_id=_current_user_id())
    except Exception as error:
        detail = str(error)
        print("[rag] reply failed", {"question": question, "detail": detail})
        return jsonify({"ok": False, "message": "知识库增强回答失败", "detail": detail}), 502

    return jsonify({"ok": True, "data": result})


@api_bp.route("/rag/reply-stream", methods=["POST"])
def create_rag_reply_stream():
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()

    if not question:
        return jsonify({"ok": False, "message": "question 字段不能为空"}), 400

    def event_stream():
        try:
            result = stream_rag_reply(question, user_id=_current_user_id())
            reply = ""

            sources_payload = json.dumps(
                {"type": "sources", "sources": result["sources"]},
                ensure_ascii=False,
            )
            yield f"data: {sources_payload}\n\n"

            for chunk in result["chunks"]:
                reply += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'reply': reply}, ensure_ascii=False)}\n\n"
        except Exception as error:
            detail = str(error)
            print("[rag] stream reply failed", {"question": question, "detail": detail})
            payload = json.dumps(
                {
                    "type": "error",
                    "message": "知识库增强回答失败",
                    "detail": detail,
                },
                ensure_ascii=False,
            )
            yield f"data: {payload}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


def _validate_assistant_request():
    body = request.get_json(silent=True) or {}
    mode = body.get("mode")
    question = body.get("question", "")

    if not mode:
        return None, None, (jsonify({"ok": False, "message": "mode 字段不能为空"}), 400)

    mode_info = get_mode_by_key(mode)

    if not mode_info:
        return None, None, (jsonify({"ok": False, "message": "不支持的模式"}), 400)

    return mode_info, question, None


@api_bp.route("/assistant/reply", methods=["POST"])
def create_reply():
    mode_info, question, error_response = _validate_assistant_request()
    if error_response:
        return error_response

    mode = mode_info["key"]
    system_prompt, user_prompt = build_prompts(mode, question, profile=get_profile_for_prompt(user_id=_current_user_id()))

    try:
        reply = generate_reply(system_prompt=system_prompt, user_prompt=user_prompt)
    except Exception as error:
        detail = str(error)
        fallback_reply = buildFallbackOrNone(mode, question)
        print("[assistant] model call failed", {"mode": mode, "question": question, "detail": detail})
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "模型接口调用失败",
                    "detail": detail,
                    "fallbackReply": fallback_reply,
                }
            ),
            502,
        )

    return jsonify({"ok": True, "data": {"mode": mode, "question": question, "reply": reply}})


def buildFallbackOrNone(mode: str, question: str):
    return build_fallback_reply(mode, question)


@api_bp.route("/assistant/reply-stream", methods=["POST"])
def create_reply_stream():
    mode_info, question, error_response = _validate_assistant_request()
    if error_response:
        return error_response

    mode = mode_info["key"]
    system_prompt, user_prompt = build_prompts(mode, question, profile=get_profile_for_prompt(user_id=_current_user_id()))

    def event_stream():
        try:
            reply = ""

            for chunk in stream_reply(system_prompt=system_prompt, user_prompt=user_prompt):
                reply += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'reply': reply}, ensure_ascii=False)}\n\n"
        except Exception as error:
            detail = str(error)
            fallback_reply = build_fallback_reply(mode, question)

            print("[assistant] stream model call failed", {"mode": mode, "question": question, "detail": detail})

            payload = json.dumps(
                {
                    "type": "error",
                    "message": "模型接口调用失败",
                    "detail": detail,
                    "fallbackReply": fallback_reply,
                },
                ensure_ascii=False,
            )
            yield f"data: {payload}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
