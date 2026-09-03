"""Topic menu keyboard"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_topic_menu_keyboard(topic_id: int, has_quizzes: bool = False) -> InlineKeyboardMarkup:
    """Create menu for topic view"""
    builder = InlineKeyboardBuilder()

    if has_quizzes:
        builder.button(text="🧪 Test yechish", callback_data=f"quiz_start:{topic_id}:0")
    else:
        builder.button(text="🤖 Test yaratish", callback_data=f"quiz_generate:{topic_id}")

    builder.button(text="🔙 Mavzularga qaytish", callback_data=f"grade_back:{topic_id}")
    builder.adjust(1)
    return builder.as_markup()