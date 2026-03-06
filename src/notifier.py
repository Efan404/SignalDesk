"""Telegram notification"""
import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from src.config import config

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram"""

    def __init__(self):
        self.token = config.telegram_bot_token
        self.chat_id = config.telegram_chat_id
        self.enabled = bool(self.token and self.chat_id)

    async def send(self, message: str) -> bool:
        """Send message to Telegram"""
        if not self.enabled:
            logger.info(f"[Telegram disabled] {message[:100]}...")
            return False

        try:
            bot = Bot(token=self.token)
            await bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown"
            )
            return True
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False

    def send_sync(self, message: str) -> bool:
        """Synchronous send wrapper"""
        return asyncio.run(self.send(message))
