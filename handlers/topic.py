"""Topic view handlers"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.crud import (
    get_topic_by_id,
    topic_has_quizzes,
    get_grade_by_id,
    get_topics_by_grade,
    get_subject_by_id,
)
from services.ai_service import get_or_generate_lesson
from keyboards import get_topic_menu_keyboard, get_grade_menu_keyboard

router = Router()


@router.callback_query(F.data.startswith("topic:"))
async def cb_topic(callback: CallbackQuery):
    """Handle topic selection - show lesson"""
    topic_id = int(callback.data.split(":")[1])

    topic = await get_topic_by_id(topic_id)
    if not topic:
        await callback.answer("Mavzu topilmadi!", show_alert=True)
        return

    has_quizzes = await topic_has_quizzes(topic_id)

    # Show lesson content
    text = (
        f"📖 <b>{topic['title']}</b>\n\n"
        f"{topic['content']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_topic_menu_keyboard(topic_id, has_quizzes),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("quiz_generate:"))
async def cb_quiz_generate(callback: CallbackQuery):
    """Generate quizzes for topic via AI"""
    topic_id = int(callback.data.split(":")[1])

    topic = await get_topic_by_id(topic_id)
    if not topic:
        await callback.answer("Mavzu topilmadi!", show_alert=True)
        return

    # Get grade and subject info
    grade = await get_grade_by_id(topic["grade_id"])
    if not grade:
        await callback.answer("Sinf topilmadi!", show_alert=True)
        return

    subject = await get_subject_by_id(grade["subject_id"])
    if not subject:
        await callback.answer("Fan topilmadi!", show_alert=True)
        return

    # Show loading
    await callback.message.edit_text(
        f"🤖 <b>AI yordamida testlar yaratilmoqda...</b>\n\n"
        f"Mavzu: <b>{topic['title']}</b>\n"
        f"Iltimos, kuting...",
        parse_mode="HTML"
    )
    await callback.answer()

    # Generate lesson/quizzes via AI
    result = await get_or_generate_lesson(
        topic["grade_id"],
        topic["title"],
        subject["name"],
        grade["grade_num"]
    )

    # Refresh topic from DB in case it was just generated
    topic = await get_topic_by_id(topic_id)
    has_quizzes = await topic_has_quizzes(topic_id)

    if topic and has_quizzes:
        text = (
            f"📖 <b>{topic['title']}</b>\n\n"
            f"{topic['content']}"
        )
        await callback.message.edit_text(
            text,
            reply_markup=get_topic_menu_keyboard(topic_id, has_quizzes),
            parse_mode="HTML"
        )
        if result["generated"]:
            await callback.message.answer("✅ Yangi dars va testlar yaratildi!")
        else:
            await callback.message.answer("✅ Testlar yaratildi!")
    else:
        await callback.message.edit_text(
            "❌ <b>Xatolik yuz berdi</b>\n\n"
            "AI xizmati hozircha mavjud emas. "
            "OPENROUTER_API_KEY ni .env faylida sozlang.",
            reply_markup=get_topic_menu_keyboard(topic_id, False),
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("grade_back:"))
async def cb_grade_back(callback: CallbackQuery):
    """Back to grade menu from topic.
    Note: callback data passes topic_id (because topic_menu uses topic_id).
    """
    topic_id = int(callback.data.split(":")[1])

    topic = await get_topic_by_id(topic_id)
    if not topic:
        await callback.answer("Mavzu topilmadi!", show_alert=True)
        return

    grade = await get_grade_by_id(topic["grade_id"])
    if not grade:
        await callback.answer("Sinf topilmadi!", show_alert=True)
        return

    topics = await get_topics_by_grade(grade["id"])

    text = (
        f"📚 <b>{grade['display_name']}</b>\n\n"
        f"Quyidagilardan mavzu tanlang:"
    )

    if not topics:
        text += "\n\n⚠️ Bu sinf uchun hali mavzular yo'q. Tez orada qo'shiladi."

    await callback.message.edit_text(text, reply_markup=get_grade_menu_keyboard(grade["id"], topics), parse_mode="HTML")
    await callback.answer()