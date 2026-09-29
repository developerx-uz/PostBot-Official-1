import asyncio
import json
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update

from xdata_handlers import config
from xdata_handlers.database import init_db
from xdata_handlers.translator import load_translations

from admin_handlers.admin_handler import admin_router
from admin_handlers.advertisement import ad_router
from admin_handlers.block_handler import block_router, BlockUserMiddleware
from admin_handlers.channel_handler import channel_router
from admin_handlers.database_handler import db_router
from admin_handlers.settings_handler import settings_router as admin_settings_router
from admin_handlers.statsmiddleware import StatsMiddleware
from admin_handlers.statistic_handler import statistics_router

from post_handlers.start_handler import start_router
from post_handlers.lang_handler import lang_router
from post_handlers.post_handler import post_router
from post_handlers.button_handler import button_router
from post_handlers.reply_handler import reply_router, callback_router
from post_handlers.media_handler import media_router
from post_handlers.done_handler import done_router
from post_handlers.editp_handler import edit_post_router
from post_handlers.send_handler import send_router
from post_handlers.mychannels_handler import mychannels_router
from post_handlers.schedule_handler import schedule_router
from post_handlers.assistant_handler import ai_assistant_router
from post_handlers.signature_handler import router as auto_signature_router
from post_handlers.statistic_handler import statistic_router as post_statistic_router
from post_handlers.watermark_handler import watermark_router

from user_handlers.feedback_handler import feedback_router
from user_handlers.settings_handler import settings_router
from user_handlers.donate_handler import donate_router
from user_handlers.errorlog_handler import error_handler

_bot: Bot = None
_dp: Dispatcher = None
_initialized: bool = False


async def get_dispatcher():
    global _bot, _dp, _initialized

    if _initialized:
        return _bot, _dp

    await init_db()
    load_translations()

    _bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode='HTML')
    )

    storage = MemoryStorage()
    _dp = Dispatcher(storage=storage)

    _dp.update.middleware(StatsMiddleware())
    _dp.update.middleware(BlockUserMiddleware())
    _dp.errors.register(error_handler)

    _dp.include_router(admin_router)
    _dp.include_router(admin_settings_router)
    _dp.include_router(ad_router)
    _dp.include_router(block_router)
    _dp.include_router(channel_router)
    _dp.include_router(db_router)
    _dp.include_router(start_router)
    _dp.include_router(post_statistic_router)
    _dp.include_router(statistics_router)
    _dp.include_router(ai_assistant_router)
    _dp.include_router(feedback_router)
    _dp.include_router(settings_router)
    _dp.include_router(donate_router)
    _dp.include_router(lang_router)
    _dp.include_router(post_router)
    _dp.include_router(button_router)
    _dp.include_router(reply_router)
    _dp.include_router(callback_router)
    _dp.include_router(media_router)
    _dp.include_router(done_router)
    _dp.include_router(edit_post_router)
    _dp.include_router(send_router)
    _dp.include_router(mychannels_router)
    _dp.include_router(schedule_router)
    _dp.include_router(auto_signature_router)
    _dp.include_router(watermark_router)

    _initialized = True
    logger.info("Dispatcher muvaffaqiyatli ishga tushdi.")
    return _bot, _dp


async def process_update(body: dict):
    bot, dp = await get_dispatcher()
    update = Update(**body)
    await dp.feed_update(bot, update)


def handler(request, response):
    try:
        if request.method != "POST":
            response.status_code = 200
            response.body = "Bot is running!"
            return response

        body = json.loads(request.body)
        asyncio.run(process_update(body))

        response.status_code = 200
        response.body = "OK"
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        response.status_code = 200
        response.body = "OK"

    return response
