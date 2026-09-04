"""Main menu handlers"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from config import WEBAPP_URL
from database.crud import get_subjects, touch_user
from keyboards import get_main_menu_keyboard
from keyboards.webapp_menu import get_webapp_keyboard
from services import essay_service

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start_deeplink(message: Message, command: CommandObject, state: FSMContext):
    """Handle /start with deep link payload (e.g. /start essay_1)."""
    payload = (command.args or "").strip()
    if payload.startswith("essay_"):
        # Open a specific essay topic directly
        try:
            tid = int(payload.split("_", 1)[1])
        except (ValueError, IndexError):
            tid = None
        if tid:
            topic = essay_service.get_topic(tid)
            if topic:
                await state.clear()
                user = message.from_user
                if user:
                    await touch_user(user.id, user.username or "", user.full_name or "")
                text = (
                    f"✍️ <b>Esse mavzusi #{tid}</b>\n\n"
                    f"<b>{topic['title']}</b>\n\n"
                    f"<b>📋 Vaziyat:</b>\n{topic['situation']}\n\n"
                    f"<b>Qarash A:</b> {topic['viewpoint_a']}\n\n"
                    f"<b>Qarash B:</b> {topic['viewpoint_b']}\n\n"
                    f"📝 Esse yozish uchun Mini App ga kiring — AI sizning matningizni "
                    f"12 mezon bo'yicha tekshiradi."
                )
                await message.answer(text, parse_mode="HTML")
                return
    # Fall through to regular start
    await cmd_start(message, state)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    user = message.from_user
    if user:
        await touch_user(user.id, user.username or "", user.full_name or "")
    subjects = await get_subjects()

    text = (
        "🎓 <b>Milliy Sertifikat Tayyorgarlik Botiga Xush Kelibsiz!</b>\n\n"
        "Bu bot sizga quyidagi fanlardan birini tanlab, "
        "sinf va mavzu bo'yicha dars o'rganish va test yechish imkonini beradi:\n\n"
        "🇺🇿 <b>Ona tili</b>\n"
        "📖 <b>Adabiyot</b>\n"
        "🏛️ <b>Tarix</b>\n\n"
        "🆕 Yangi imkoniyatlar:\n"
        "⏱️ <b>/exam</b> — to'liq imtihon simulyatori (45 savol, 180 daqiqa)\n"
        "✍️ <b>/essay</b> — esse mashqi (12 mezon bo'yicha AI tekshirish)\n"
        "📊 <b>/stats</b> — shaxsiy statistikangiz\n"
        "🏆 <b>/top</b> — eng yaxshi natijalar\n"
        "🌐 <b>/webapp</b> — Mini App ni ochish\n\n"
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