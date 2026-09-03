"""aiohttp request handlers for the Telegram Mini App.

Thin JSON wrappers over the existing CRUD layer in `database.crud` and the
existing AI service in `services.ai_service`. No new business logic — just
shapes rows as JSON and dispatches.
"""
import json
from typing import Any, Dict

from aiohttp import web

from database import crud
from services import ai_service, curriculum


def _json(data: Any, status: int = 200) -> web.Response:
    """JSON response with Uzbek-friendly UTF-8 encoding."""
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return web.Response(
        body=body,
        status=status,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )


async def subjects(request: web.Request) -> web.Response:
    """GET /api/subjects — list all subjects."""
    rows = await crud.get_subjects()
    return _json(
        [
            {
                "id": r["id"],
                "name": r["name"],
                "display_name": r["display_name"],
                "icon": r["icon"],
                "order_num": r["order_num"],
            }
            for r in rows
        ]
    )


async def grades(request: web.Request) -> web.Response:
    """GET /api/grades?subject=<name> — list grades for a subject."""
    name = request.query.get("subject", "").strip()
    if not name:
        return _json({"error": "missing_subject"}, 400)

    subj = await crud.get_subject_by_name(name)
    if not subj:
        return _json({"error": "subject_not_found"}, 404)

    rows = await crud.get_grades_by_subject(subj["id"])
    return _json(
        [
            {
                "id": r["id"],
                "subject_id": r["subject_id"],
                "grade_num": r["grade_num"],
                "display_name": r["display_name"],
            }
            for r in rows
        ]
    )


async def topics(request: web.Request) -> web.Response:
    """GET /api/topics?grade_id=<id> — list topics; auto-seed from curriculum."""
    grade_id_str = request.query.get("grade_id", "").strip()
    if not grade_id_str.isdigit():
        return _json({"error": "invalid_grade_id"}, 400)
    grade_id = int(grade_id_str)

    grade = await crud.get_grade_by_id(grade_id)
    if not grade:
        return _json({"error": "grade_not_found"}, 404)

    rows = await crud.get_topics_by_grade(grade_id)

    # Lazy-seed: if empty, populate from curriculum with empty content.
    # AI content + quizzes will be generated on demand when the user opens the topic.
    if not rows:
        subject = await crud.get_subject_by_id(grade["subject_id"])
        titles = curriculum.get_titles(subject["name"], grade["grade_num"])
        for i, title in enumerate(titles, start=1):
            await crud.create_topic(
                grade_id=grade_id,
                title=title,
                content="",
                order_num=i,
                is_ai_generated=False,
            )
        rows = await crud.get_topics_by_grade(grade_id)

    out = []
    for r in rows:
        out.append(
            {
                "id": r["id"],
                "title": r["title"],
                "is_ai_generated": bool(r["is_ai_generated"]),
                "has_quizzes": await crud.topic_has_quizzes(r["id"]),
                "order_num": r["order_num"],
            }
        )
    return _json(out)


async def topic_detail(request: web.Request) -> web.Response:
    """GET /api/topic/<id> — full lesson content."""
    tid = int(request.match_info["id"])
    t = await crud.get_topic_by_id(tid)
    if not t:
        return _json({"error": "topic_not_found"}, 404)
    return _json(
        {
            "id": t["id"],
            "title": t["title"],
            "content": t["content"],
            "is_ai_generated": bool(t["is_ai_generated"]),
            "grade_id": t["grade_id"],
            "has_quizzes": await crud.topic_has_quizzes(tid),
        }
    )


async def topic_generate(request: web.Request) -> web.Response:
    """POST /api/topic/<id>/generate — force AI generation via OpenRouter."""
    tid = int(request.match_info["id"])
    t = await crud.get_topic_by_id(tid)
    if not t:
        return _json({"error": "topic_not_found"}, 404)

    grade = await crud.get_grade_by_id(t["grade_id"])
    subject = await crud.get_subject_by_id(grade["subject_id"])

    result = await ai_service.get_or_generate_lesson(
        grade_id=t["grade_id"],
        topic_title=t["title"],
        subject_name=subject["name"],
        grade_num=grade["grade_num"],
    )

    quizzes = await crud.get_quizzes_by_topic(tid)
    return _json(
        {
            "topic": result["topic"],
            "generated": result["generated"],
            "quizzes_created": len(quizzes),
        }
    )


async def quiz_list(request: web.Request) -> web.Response:
    """GET /api/quiz/<topic_id> — fetch quiz questions."""
    tid = int(request.match_info["topic_id"])
    qs = await crud.get_quizzes_by_topic(tid)
    out = []
    for q in qs:
        out.append(
            {
                "id": q["id"],
                "question": q["question"],
                "options": [
                    q["option_a"],
                    q["option_b"],
                    q["option_c"],
                    q["option_d"],
                ],
                "correct_option": q["correct_option"],
                "explanation": q.get("explanation", "") or "",
            }
        )
    return _json(out)


async def quiz_submit(request: web.Request) -> web.Response:
    """POST /api/quiz/<topic_id>/submit — score a submission."""
    tid = int(request.match_info["topic_id"])
    try:
        body = await request.json()
    except Exception:
        body = {}

    answers_in = body.get("answers", []) or []
    answers: Dict[int, str] = {}
    for a in answers_in:
        try:
            answers[int(a["index"])] = str(a["selected"])
        except (KeyError, ValueError, TypeError):
            continue

    qs = await crud.get_quizzes_by_topic(tid)
    score = 0
    per = []
    for i, q in enumerate(qs):
        sel = answers.get(i, "")
        ok = sel == q["correct_option"]
        score += int(ok)
        per.append(
            {
                "index": i,
                "is_correct": ok,
                "selected": sel,
                "correct": q["correct_option"],
                "explanation": q.get("explanation", "") or "",
            }
        )
    total = len(qs)
    return _json(
        {
            "score": score,
            "total": total,
            "percentage": int((score / total) * 100) if total else 0,
            "per_question": per,
        }
    )


async def healthcheck(request: web.Request) -> web.Response:
    """GET /api/health — health probe."""
    return _json({"ok": True, "service": "cert_bot_webapp"})