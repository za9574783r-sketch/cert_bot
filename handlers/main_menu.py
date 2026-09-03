"""Main menu handlers"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from config import WEBAPP_URL
from database.crud import get_subjects
from keyboards import get_main_menu_keyboard
from keyboards.webapp_menu import get_webapp_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    subjects = await get_subjects()

    text = (
        "🎓 <b>Milliy Sertifikat Tayyorgarlik Botiga Xush Kelibsiz!</b>\n\n"
        "Bu bot sizga quyidagi fanlardan birini tanlab, "
        "sinf va mavzu bo'yicha dars o'rganish va test yechish imkonini beradi:\n\n"
        "🇺🇿 <b>Ona tili</b>\n"
        "📖 <b>Adabiyot</b>\n"
        "🏛️ <b>Tarix</b>\n\n"
        "Quyidagi menyudan fan tanlang."
    )

    # Inline subject keyboard (existing flow)
    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(subjects),
        parse_mode="HTML",
    )

    # Persistent reply keyboard with Mini App launcher — only if HTTPS is set.
    # Telegram refuses Web App URLs that are not HTTPS.
    if WEBAPP_URL.startswith("https://"):
        await message.answer(
            "👆 Quyidagi tugma orqali Mini App ni oching:",
            reply_markup=get_webapp_keyboard(),
        )
    else:
        await message.answer(
            "💡 Mini App HTTPS URL talab qiladi. Hozircha quyidagi inline "
            "tugmalar orqali ishlating. Mini App haqida to'liq ma'lumot: "
            "<code>/webapp</code>",
            parse_mode="HTML",
        )