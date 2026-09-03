"""Quiz keyboards"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_quiz_keyboard(topic_id: int, question_index: int, options: list) -> InlineKeyboardMarkup:
    """Create keyboard for quiz question"""
    builder = InlineKeyboardBuilder()

    for i, option in enumerate(options):
        letter = chr(65 + i)  # A, B, C, D
        builder.button(
            text=f"{letter}) {option}",
            callback_data=f"quiz_answer:{topic_id}:{question_index}:{letter}"
        )

    builder.adjust(2)
    return builder.as_markup()


def get_quiz_navigation_keyboard(topic_id: int, current_index: int, total: int, show_result: bool = False) -> InlineKeyboardMarkup:
    """Create navigation keyboard for quiz"""
    builder = InlineKeyboardBuilder()

    if not show_result:
        if current_index > 0:
            builder.button(
                text="⬅️ Oldingi",
                callback_data=f"quiz_nav:{topic_id}:{current_index - 1}"
            )
        if current_index < total - 1:
            builder.button(
                text="Keyingi ➡️",
                callback_data=f"quiz_nav:{topic_id}:{current_index + 1}"
            )
    else:
        builder.button(text="🔄 Qayta urinish", callback_data=f"quiz_start:{topic_id}:0")
        builder.button(text="📖 Mavzuga qaytish", callback_data=f"topic:{topic_id}")

    builder.button(text="🏠 Bosh menyu", callback_data="main_menu")
    builder.adjust(2, 1)
    return builder.as_markup()


def get_quiz_result_keyboard(topic_id: int, score: int, total: int) -> InlineKeyboardMarkup:
    """Create keyboard for quiz results"""
    builder = InlineKeyboardBuilder()

    percentage = int((score / total) * 100) if total > 0 else 0

    if percentage >= 80:
        builder.button(text="🎉 Ajoyib! Keyingi mavzu", callback_data=f"grade_back:{topic_id}")
    elif percentage >= 60:
        builder.button(text="👍 Yaxshi! Takrorlash", callback_data=f"quiz_start:{topic_id}:0")
    else:
        builder.button(text="📚 Darsni qayta o'qish", callback_data=f"topic:{topic_id}")
        builder.button(text="🔄 Qayta urinish", callback_data=f"quiz_start:{topic_id}:0")

    builder.button(text="🏠 Bosh menyu", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()