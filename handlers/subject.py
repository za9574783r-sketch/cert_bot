"""Subject selection handlers"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database.crud import (
    get_grades_by_subject,
    get_subject_by_name,
    get_subjects,
)
from keyboards import get_main_menu_keyboard, get_subject_menu_keyboard

router = Router()


@router.callback_query(F.data.startswith("subject:"))
async def cb_subject(callback: CallbackQuery):
    """Handle subject selection"""
    subject_name = callback.data.split(":")[1]

    subject = await get_subject_by_name(subject_name)
    if not subject:
        await callback.answer("Fan topilmadi!", show_alert=True)
        return

    grades = await get_grades_by_subject(subject["id"])

    text = (
        f"{subject['icon']} <b>{subject['display_name']}</b>\n\n"
        f"Quyidagilardan sinfni tanlang:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_subject_menu_keyboard(subject_name, grades),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def cb_back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Back to main menu from any subject/grade context"""
    await state.clear()
    subjects = await get_subjects()

    text = (
        "🎓 <b>Milliy Sertifikat Tayyorgarlik Botiga Xush Kelibsiz!</b>\n\n"
        "Quyidagi menyudan fan tanlang:"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu_keyboard(subjects),
            parse_mode="HTML",
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=get_main_menu_keyboard(subjects),
            parse_mode="HTML",
        )
    await callback.answer()