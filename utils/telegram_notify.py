"""
Telegram Notification Utility

Sends project progress updates to your phone.

Setup:
  1. Message @BotFather on Telegram → create a bot → copy the token
  2. Message @userinfobot on Telegram → copy your chat_id
  3. Add both to config.yaml under telegram:

     telegram:
       token: "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"
       chat_id: "123456789"
"""

import asyncio
import logging
from typing import Optional

try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    Bot = None  # type: ignore

logger = logging.getLogger(__name__)


class TelegramNotifier:

    def __init__(self, token: str, chat_id: str):
        if not TELEGRAM_AVAILABLE:
            raise ImportError(
                "python-telegram-bot not installed.\n"
                "  pip install python-telegram-bot"
            )
        self.token = token
        self.chat_id = str(chat_id)
        self.bot = Bot(token=token)
        logger.info("[Telegram] Initialized for chat_id %s", chat_id)

    def send(self, message: str) -> bool:
        """
        Send a Markdown-formatted message.
        Uses asyncio.run() — safe in any context (threads, scripts, etc).
        """
        if len(message) > 4000:
            message = message[:3997] + "..."
        try:
            asyncio.run(self._send_async(message))
            logger.debug("[Telegram] Sent: %s...", message[:60])
            return True
        except Exception as e:
            logger.error("[Telegram] Failed to send: %s", e)
            return False

    async def _send_async(self, message: str) -> None:
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )

    def send_file(self, file_path: str, caption: str = "") -> bool:
        """Send a file (e.g. FINAL_ANSWER.md) to Telegram."""
        try:
            asyncio.run(self._send_file_async(file_path, caption))
            return True
        except Exception as e:
            logger.error("[Telegram] Failed to send file: %s", e)
            return False

    async def _send_file_async(self, file_path: str, caption: str) -> None:
        with open(file_path, "rb") as f:
            await self.bot.send_document(
                chat_id=self.chat_id,
                document=f,
                caption=caption[:1024] if caption else "",
            )
