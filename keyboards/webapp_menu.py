"""Reply keyboard with a button that opens the Telegram Mini App."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from config import WEBAPP_URL, WEBAPP_BUTTON_TEXT


def get_webapp_keyboard() -> ReplyKeyboardMarkup:
    """Persistent reply-keyboard with a single button that opens the Mini App."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=WEBAPP_BUTTON_TEXT, web_app=WebAppInfo(url=WEBAPP_URL))],
        ],
        resize_keyboard=True,
        input_field_placeholder="Mini App tugmasini bosing...",
    )