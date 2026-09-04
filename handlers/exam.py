"""/exam command — show the official exam format and a Mini App link."""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from services import simulator
from config import WEBAPP_URL

router = Router()


@router.message(Command("exam"))
async def cmd_exam(message: Message) -> None:
    """Reply with exam structure and link to the Mini App simulator."""
    meta = simulator.get_exam_meta()
    sections = "\n".join(
        f"  • {s['name']}: {s['question_count']} ta × {s['points_per_question']} b."
        for s in meta["sections"]
    )

    text = (
        f"⏱️ <b>Milliy sertifikat imtihoni simulyatori</b>\n\n"
        f"<b>Fan:</b> {meta['subject']}\n"
        f"<b>Savollar:</b> {meta['total_questions']} ta\n"
        f"<b>Vaqt:</b> {meta['duration_minutes']} daqiqa\n"
        f"<b>Umumiy ball:</b> {meta['total_score']}\n\n"
        f"<b>📚 Bo'limlar:</b>\n{sections}\n\n"
        f"📲 Imtihonni boshlash uchun Mini App ni oching:\n<code>{WEBAPP_URL}</code>"
    )
    await message.answer(text, parse_mode="HTML")
