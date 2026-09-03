"""Grade selection handlers"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.crud import (
    get_topics_by_grade,
    get_grade_by_id,
    get_grades_by_subject,
    get_subject_by_id,
)
from keyboards import get_grade_menu_keyboard, get_subject_menu_keyboard

router = Router()


@router.callback_query(F.data.startswith("grade:"))
async def cb_grade(callback: CallbackQuery):
    """Handle grade selection"""
    grade_id = int(callback.data.split(":")[1])

    grade = await get_grade_by_id(grade_id)
    if not grade:
        await callback.answer("Sinf topilmadi!", show_alert=True)
        return

    topics = await get_topics_by_grade(grade_id)

    text = (
        f"📚 <b>{grade['display_name']}</b>\n\n"
        f"Quyidagilardan mavzu tanlang:"
    )

    if not topics:
        text += "\n\n⚠️ Bu sinf uchun hali mavzular yo'q. Tez orada qo'shiladi."

    await callback.message.edit_text(text, reply_markup=get_grade_menu_keyboard(grade_id, topics), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("subject_back:"))
async def cb_subject_back(callback: CallbackQuery):
    """Back to subject menu from grade"""
    grade_id = int(callback.data.split(":")[1])

    grade = await get_grade_by_id(grade_id)
    if not grade:
        await callback.answer("Sinf topilmadi!", show_alert=True)
        return

    subject = await get_subject_by_id(grade["subject_id"])
    if not subject:
        await callback.answer("Fan topilmadi!", show_alert=True)
        return

    grades = await get_grades_by_subject(subject["id"])

    text = (
        f"{subject['icon']} <b>{subject['display_name']}</b>\n\n"
        f"Quyidagilardan sinfni tanlang:"
    )

    await callback.message.edit_text(text, reply_markup=get_subject_menu_keyboard(subject["name"], grades), parse_mode="HTML")
    await callback.answer()