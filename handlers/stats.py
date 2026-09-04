"""User stats and leaderboard commands.

`/stats` — show the caller's accumulated counters and recent attempts.
`/top` — show the top 10 users by average exam percentage.
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database import crud

router = Router()


def _fmt_dt(s: str) -> str:
    """Trim SQLite datetime string to YYYY-MM-DD HH:MM."""
    return s[:16] if s else "-"


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    user = message.from_user
    if not user:
        return
    await crud.touch_user(user.id, user.username or "", user.full_name or "")

    stats = await crud.get_user_stats(user.id)
    if not stats:
        await message.answer("Hali statistikangiz yo'q. Dars o'rganing yoki test yeching.")
        return

    quiz_acc = 0.0
    if stats["quizzes_taken"] > 0:
        quiz_acc = round((stats["quizzes_correct"] / stats["quizzes_taken"]) * 100, 1)
    essay_avg = 0.0
    if stats["essays_graded"] > 0:
        essay_avg = round((stats["essays_total_score"] / (stats["essays_graded"] * 24)) * 100, 1)
    exam_avg = 0.0
    if stats["exams_max_score"] > 0:
        exam_avg = round((stats["exams_total_score"] / stats["exams_max_score"]) * 100, 1)

    lines = [
        f"📊 <b>Sizning statistikangiz</b>\n",
        f"👤 Ism: <b>{stats.get('full_name') or '-'}</b>",
        f"📅 Birinchi marta: {_fmt_dt(stats['first_seen_at'])}",
        f"⏱ Oxirgi faollik: {_fmt_dt(stats['last_active_at'])}\n",
        f"🧪 <b>Testlar:</b> {stats['quizzes_taken']} ta, "
        f"{stats['quizzes_correct']} ta to'g'ri · aniqlik {quiz_acc}%",
        f"✍️ <b>Esselar:</b> {stats['essays_graded']} ta · o'rtacha {essay_avg}%",
        f"⏱ <b>Imtihonlar:</b> {stats['exams_taken']} ta · o'rtacha {exam_avg}%",
    ]

    # Recent attempts
    attempts = await crud.list_user_attempts(user.id, limit=5)
    if attempts:
        lines.append("\n📜 <b>So'nggi urinishlar:</b>")
        for a in attempts:
            icon = {"quiz": "🧪", "essay": "✍️", "exam": "⏱"}.get(a["kind"], "•")
            level = f" · {a['level']}" if a.get("level") else ""
            lines.append(
                f"  {icon} {_fmt_dt(a['created_at'])} — {a['percentage']}%{level}"
            )

    lines.append("\n💡 To'liq tarix: Mini App → Profil")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("top"))
async def cmd_top(message: Message) -> None:
    """Top 10 by exam average %."""
    rows = await crud.get_top_users(10)
    if not rows:
        await message.answer(
            "🏆 Hali hech kim imtihon topshirmagan. Birinchi bo'lib siz bo'ling!"
        )
        return

    medals = ["🥇", "🥈", "🥉"] + ["•"] * 7
    lines = ["🏆 <b>Imtihon natijalari bo'yicha TOP-10</b>\n"]
    for i, r in enumerate(rows):
        name = r.get("full_name") or r.get("username") or f"User {r['user_id']}"
        lines.append(
            f"{medals[i]} <b>{i + 1}.</b> {name} — "
            f"{r['avg_percent']}% ({r['exams_taken']} ta imtihon)"
        )
    lines.append("\n📊 O'z statistikangiz: /stats")
    await message.answer("\n".join(lines), parse_mode="HTML")
