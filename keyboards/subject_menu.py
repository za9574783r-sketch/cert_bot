"""Subject menu keyboard (grades for a subject)"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subject_menu_keyboard(subject_name: str, grades: list) -> InlineKeyboardMarkup:
    """Create menu with grades for selected subject"""
    builder = InlineKeyboardBuilder()

    for grade in grades:
        builder.button(
            text=f"📚 {grade['display_name']}",
            callback_data=f"grade:{grade['id']}"
        )

    builder.button(text="🔙 Orqaga", callback_data="main_menu")
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup()