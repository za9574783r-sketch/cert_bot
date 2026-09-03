"""Main menu keyboard"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard(subjects: list) -> InlineKeyboardMarkup:
    """Create main menu with subjects"""
    builder = InlineKeyboardBuilder()

    for subject in subjects:
        builder.button(
            text=f"{subject['icon']} {subject['display_name']}",
            callback_data=f"subject:{subject['name']}"
        )

    builder.adjust(1)
    return builder.as_markup()


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with back to main menu button"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Bosh menyu", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()