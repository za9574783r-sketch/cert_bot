"""Handler that opens the Telegram Mini App."""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Router
from aiogram.filters import Command
from aiogram.types import Message, TelegramObject

from aiogram.types import MenuButtonWebApp, WebAppInfo
from keyboards.webapp_menu import get_webapp_keyboard
from config import WEBAPP_URL, WEBAPP_BUTTON_TEXT

router = Router()


class MenuButtonMiddleware(BaseMiddleware):
    """Installs a per-chat Web App menu button on the user's first interaction.

    Telegram shows this button as the blue "Mini App" icon at the bottom-left
    of every chat with the bot. After installing once, we cache the user id so
    the API call is only made the first time per process lifetime.
    """

    def __init__(self) -> None:
        self._installed: set[int] = set()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = data.get("event_from_user")
        if (
            user_id is not None
            and user_id not in self._installed
            and WEBAPP_URL.startswith("https://")
        ):
            bot = data.get("bot")
            if bot is not None:
                try:
                    await bot.set_chat_menu_button(
                        chat_id=user_id,
                        menu_button=MenuButtonWebApp(
                            text=WEBAPP_BUTTON_TEXT,
                            web_app=WebAppInfo(url=WEBAPP_URL),
                        ),
                    )
                    self._installed.add(user_id)
                except Exception:
                    # Non-fatal: the button can still be installed via /start.
                    pass
        return await handler(event, data)


router.message.middleware.register(MenuButtonMiddleware())
router.callback_query.middleware.register(MenuButtonMiddleware())


@router.message(Command("webapp"))
async def cmd_webapp(message: Message) -> None:
    """Reply with a reply-keyboard button that opens the Mini App."""
    text = (
        "🌐 <b>Mini App</b>\n\n"
        "Quyidagi tugma orqali chiroyli interfeysda ishlashingiz mumkin:\n\n"
        "✅ Fanlar bo'limi\n"
        "✅ 5 — 11 sinflar\n"
        "✅ AI yordamida dars va quizlar\n"
        "✅ Natijalaringiz statistikasi\n\n"
        "Quyidagi tugmani bosing 👇"
    )
    await message.answer(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")