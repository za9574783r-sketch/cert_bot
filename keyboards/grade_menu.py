"""Grade menu keyboard (topics for a grade)"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_grade_menu_keyboard(grade_id: int, topics: list) -> InlineKeyboardMarkup:
    """Create menu with topics for selected grade"""
    builder = InlineKeyboardBuilder()

    for topic in topics:
        ai_badge = " 🤖" if topic.get("is_ai_generated") else ""
        builder.button(
            text=f"📖 {topic['title']}{ai_badge}",
            callback_data=f"topic:{topic['id']}"
        )

    builder.button(text="🔙 Orqaga", callback_data=f"subject_back:{grade_id}")
    builder.adjust(1)
    return builder.as_markup()