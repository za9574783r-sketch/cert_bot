"""/help command — list all available commands with descriptions."""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import WEBAPP_URL

router = Router()


HELP_TEXT = """📚 <b>Milliy Sertifikat Bot — buyruqlar ro'yxati</b>

<b>Asosiy:</b>
/start — Asosiy menyu
/help — Ushbu yordam
/webapp — Mini App ni ochish

<b>O'qish va test:</b>
/essay — Esse mavzularini ko'rsatish
/exam — Imtihon simulyatori haqida

<b>Statistika:</b>
/stats — Shaxsiy statistikangiz
/top — Eng yaxshi natijalar (liderlar)

<b>Mavzular:</b>
Ona tili, Adabiyot, Tarix — 5–11 sinflar
AI yordamida dars va test generatsiyasi

<b>Yangi imkoniyatlar:</b>
⏱️ To'liq imtihon simulyatori — 45 savol, 180 daqiqa
✍️ Esse mashqi — 12 mezon bo'yicha AI tekshirish
📊 Barcha natijalaringiz saqlanadi
🏆 Boshqa foydalanuvchilar bilan bellashuv

🌐 <b>Mini App:</b> {webapp_url}
"""


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        HELP_TEXT.format(webapp_url=WEBAPP_URL),
        parse_mode="HTML",
    )
