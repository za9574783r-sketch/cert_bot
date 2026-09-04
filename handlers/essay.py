"""Essay practice command.

Shows the list of available essay topics inline, with a button that
opens the Mini App directly to the essay picker.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from services import essay_service
from config import WEBAPP_URL

router = Router()


@router.message(Command("essay"))
async def cmd_essay(message: Message) -> None:
    """Reply with the essay topic list and a Mini App link."""
    topics = essay_service.list_topics()
    lines = ["✍️ <b>Esse mashqi — mavzular</b>\n"]
    for t in topics:
        lines.append(
            f"<b>{t['id']}.</b> {t['title']}\n"
            f"   <i>{t['situation'][:90]}…</i>\n"
        )
    lines.append(
        "\n📲 To'liq yozish va AI tekshirish uchun Mini App ni oching:\n"
        f"<code>{WEBAPP_URL}</code>\n"
    )

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.callback_query(F.data.startswith("essay_topic:"))
async def cb_essay_topic(callback: CallbackQuery) -> None:
    """Open a specific essay topic in Telegram (read-only preview)."""
    tid = int(callback.data.split(":")[1])
    topic = essay_service.get_topic(tid)
    if not topic:
        await callback.answer("Mavzu topilmadi", show_alert=True)
        return

    text = (
        f"✍️ <b>Esse mavzusi #{tid}</b>\n\n"
        f"<b>{topic['title']}</b>\n\n"
        f"<b>📋 Vaziyat:</b>\n{topic['situation']}\n\n"
        f"<b>Qarash A:</b> {topic['viewpoint_a']}\n\n"
        f"<b>Qarash B:</b> {topic['viewpoint_b']}\n\n"
        "📝 Esse yozish uchun Mini App ga kiring. AI sizning matningizni "
        "12 mezon bo'yicha tekshiradi."
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
