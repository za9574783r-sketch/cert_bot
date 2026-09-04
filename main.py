"""Main entry point for Milliy Sertifikat Telegram Bot + Mini App."""
import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, WEBAPP_HOST, WEBAPP_PORT
from database.models import init_db
from handlers import (
    main_menu_router,
    subject_router,
    grade_router,
    topic_router,
    quiz_router,
    webapp_router,
    essay_router,
    exam_router,
    stats_router,
    help_router,
)
from webapp.server import build_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the bot polling and the Mini App HTTP server in parallel."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    dp.include_router(main_menu_router)
    dp.include_router(subject_router)
    dp.include_router(grade_router)
    dp.include_router(topic_router)
    dp.include_router(quiz_router)
    dp.include_router(webapp_router)
    dp.include_router(essay_router)
    dp.include_router(exam_router)
    dp.include_router(stats_router)
    dp.include_router(help_router)

    # Mini App HTTP server
    app = build_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
    await site.start()
    logger.info(
        "Mini App HTTP server started at http://%s:%s",
        WEBAPP_HOST,
        WEBAPP_PORT,
    )

    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down HTTP server...")
        await runner.cleanup()
        await bot.session.close()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise