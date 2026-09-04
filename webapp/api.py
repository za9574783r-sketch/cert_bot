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
    from database import crud

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
    result = {
        "score": score,
        "total": total,
        "percentage": int((score / total) * 100) if total else 0,
        "per_question": per,
    }

    # Persist for progress tracking
    user = body.get("user") or {}
    user_id = user.get("id")
    if user_id:
        try:
            uid = int(user_id)
            await crud.touch_user(uid, user.get("username", ""), user.get("full_name", ""))
            await crud.record_attempt(
                uid, "quiz", {"answers": answers_in, "topic_id": tid},
                score=float(score), max_score=float(total), ref_id=tid,
            )
            await crud.update_user_aggregates(
                uid, quizzes_taken=1, quizzes_correct=score,
            )
        except Exception as e:
            print(f"quiz_submit persist error: {e}")

    return _json(result)


# ---------------------------------------------------------------------------
# Essay endpoints — list topics, fetch a topic, grade a submission.
# ---------------------------------------------------------------------------

async def essay_topics(request: web.Request) -> web.Response:
    """GET /api/essay/topics — return all essay prompts."""
    from services import essay_service
    return _json(essay_service.list_topics())


async def essay_topic(request: web.Request) -> web.Response:
    """GET /api/essay/topic/<id> — return one essay prompt."""
    from services import essay_service
    tid = int(request.match_info["id"])
    topic = essay_service.get_topic(tid)
    if not topic:
        return _json({"error": "topic_not_found"}, 404)
    return _json(topic)


async def essay_grade(request: web.Request) -> web.Response:
    """POST /api/essay/grade — grade a submitted essay against the rubric.

    Body: {"topic_id": int, "text": str, "user": {id, username?, full_name?}|None}
    """
    from services import essay_service
    from database import crud

    try:
        body = await request.json()
    except Exception:
        body = {}

    topic_id = body.get("topic_id")
    text = (body.get("text") or "").strip()
    user = body.get("user") or {}
    if not topic_id or not text:
        return _json({"error": "missing_fields"}, 400)

    word_count = essay_service.count_words(text)
    if word_count < 100:
        result = {
            "disqualification_reason": "Essening hajmi 100 ta so'zdan kam. (2 ball)",
            "total_score": 2,
            "max_score": 24,
            "word_count": word_count,
        }
        user_id = user.get("id")
        if user_id:
            try:
                uid = int(user_id)
                await crud.touch_user(uid, user.get("username", ""), user.get("full_name", ""))
                await crud.record_attempt(
                    uid, "essay", {"topic_id": int(topic_id), "word_count": word_count},
                    score=2, max_score=24, level="Disqualification", ref_id=int(topic_id),
                )
                await crud.update_user_aggregates(uid, essays_graded=1, essays_total_score=2)
            except Exception as e:
                print(f"essay_grade persist (short) error: {e}")
        return _json(result)

    grade = await essay_service.grade_essay(int(topic_id), text)
    if grade is None:
        return _json(
            {"error": "ai_unavailable",
             "detail": "AI xizmati sozlanmagan. GEMINI_API_KEY yoki OPENROUTER_API_KEY ni .env ga qo'ying."},
            503,
        )
    result = essay_service.grade_to_dict(grade)

    user_id = user.get("id")
    if user_id:
        try:
            uid = int(user_id)
            await crud.touch_user(uid, user.get("username", ""), user.get("full_name", ""))
            await crud.record_attempt(
                uid, "essay",
                {"topic_id": int(topic_id), "word_count": word_count, "text": text[:500]},
                score=grade.total_score, max_score=grade.max_score,
                level=grade.level, ref_id=int(topic_id),
            )
            await crud.update_user_aggregates(
                uid, essays_graded=1, essays_total_score=grade.total_score,
            )
        except Exception as e:
            print(f"essay_grade persist error: {e}")

    return _json(result)


# ---------------------------------------------------------------------------
# Simulator endpoints — full 45-question, 180-minute exam.
# ---------------------------------------------------------------------------

async def exam_meta(request: web.Request) -> web.Response:
    """GET /api/exam/meta — return exam structure (sections, durations, levels)."""
    from services import simulator
    return _json(simulator.get_exam_meta())


async def exam_generate(request: web.Request) -> web.Response:
    """GET /api/exam/generate?seed=... — build a fresh exam attempt."""
    from services import simulator
    seed = request.query.get("seed") or None
    return _json(simulator.generate_exam(seed))


async def exam_grade(request: web.Request) -> web.Response:
    """POST /api/exam/grade — score a full exam attempt.

    Body: {"questions": [...], "closed_answers": {qid: "A"|"B"|"C"|"D"},
           "essay_topic_id": int|None, "essay_text": str|None,
           "user": {id, username?, full_name?}|None}
    """
    from services import simulator
    from database import crud

    try:
        body = await request.json()
    except Exception:
        body = {}

    questions = body.get("questions") or []
    closed_answers = body.get("closed_answers") or {}
    essay_topic_id = body.get("essay_topic_id")
    essay_text = (body.get("essay_text") or "").strip() or None
    user = body.get("user") or {}

    # Coerce keys to int
    closed_answers = {int(k): v for k, v in closed_answers.items()}

    result = await simulator.grade_full_exam(
        questions, closed_answers, essay_topic_id, essay_text
    )


# ---------------------------------------------------------------------------
# Progress endpoints — user stats, attempts history, leaderboard.
# ---------------------------------------------------------------------------

async def user_stats(request: web.Request) -> web.Response:
    """GET /api/user/<id>/stats — accumulated counters for one user."""
    from database import crud
    uid = int(request.match_info["id"])
    stats = await crud.get_user_stats(uid)
    if not stats:
        return _json({"error": "user_not_found"}, 404)

    # Compute simple average essay %
    essay_avg = 0.0
    if stats["essays_graded"] > 0:
        essay_avg = round((stats["essays_total_score"] / (stats["essays_graded"] * 24)) * 100, 1)
    exam_avg = 0.0
    if stats["exams_max_score"] > 0:
        exam_avg = round((stats["exams_total_score"] / stats["exams_max_score"]) * 100, 1)
    quiz_acc = 0.0
    if stats["quizzes_taken"] > 0:
        quiz_acc = round((stats["quizzes_correct"] / stats["quizzes_taken"]) * 100, 1)

    return _json({
        "user_id": stats["user_id"],
        "full_name": stats.get("full_name", ""),
        "username": stats.get("username", ""),
        "first_seen_at": stats["first_seen_at"],
        "last_active_at": stats["last_active_at"],
        "quizzes": {
            "taken": stats["quizzes_taken"],
            "correct": stats["quizzes_correct"],
            "accuracy_percent": quiz_acc,
        },
        "essays": {
            "graded": stats["essays_graded"],
            "average_percent": essay_avg,
        },
        "exams": {
            "taken": stats["exams_taken"],
            "average_percent": exam_avg,
        },
    })


async def user_attempts(request: web.Request) -> web.Response:
    """GET /api/user/<id>/attempts?kind=exam&limit=20 — recent attempts."""
    from database import crud
    uid = int(request.match_info["id"])
    kind = request.query.get("kind")
    limit = int(request.query.get("limit", "20"))
    if kind and kind not in ("quiz", "essay", "exam"):
        return _json({"error": "invalid_kind"}, 400)
    rows = await crud.list_user_attempts(uid, limit)
    if kind:
        rows = [r for r in rows if r["kind"] == kind]
    return _json(rows)


async def leaderboard(request: web.Request) -> web.Response:
    """GET /api/leaderboard?limit=10 — top users by average exam %."""
    from database import crud
    limit = int(request.query.get("limit", "10"))
    rows = await crud.get_top_users(limit)
    return _json([
        {
            "user_id": r["user_id"],
            "full_name": r.get("full_name", "") or r.get("username", "") or f"User {r['user_id']}",
            "exams_taken": r["exams_taken"],
            "avg_percent": r["avg_pct"],
        }
        for r in rows
    ])

    # Persist for progress tracking
    user_id = user.get("id")
    if user_id:
        try:
            uid = int(user_id)
            await crud.touch_user(uid, user.get("username", ""), user.get("full_name", ""))
            level = result.get("level", {}).get("code", "")
            payload = {
                "closed_answers": closed_answers,
                "essay_topic_id": essay_topic_id,
                "essay_score": result.get("essay_score"),
            }
            await crud.record_attempt(
                uid, "exam", payload,
                score=float(result.get("total_earned", 0)),
                max_score=float(result.get("total_max", 0)),
                level=level,
            )
            await crud.update_user_aggregates(
                uid,
                exams_taken=1,
                exams_total_score=float(result.get("total_earned", 0)),
                exams_max_score=float(result.get("total_max", 0)),
            )
        except Exception as e:
            print(f"exam_grade persist error: {e}")

    return _json(result)


async def healthcheck(request: web.Request) -> web.Response:
    """GET /api/health — health probe."""
    return _json({"ok": True, "service": "cert_bot_webapp"})