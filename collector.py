import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch


load_dotenv()


class TelegramCollector:
    def __init__(self) -> None:
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        phone = os.getenv("TELEGRAM_PHONE")

        if not api_id or not api_hash or not phone:
            raise ValueError(
                "Не заданы TELEGRAM_API_ID, TELEGRAM_API_HASH или TELEGRAM_PHONE в .env"
            )

        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.phone = phone

        self.client = TelegramClient(
            "telegram_bot_detector_session",
            self.api_id,
            self.api_hash,
        )

    async def connect(self) -> None:
        await self.client.start(phone=self.phone)

    async def disconnect(self) -> None:
        await self.client.disconnect()

    async def fetch_subscribers(
        self,
        channel_username: str,
        limit: int = 10000,
        batch_size: int = 200,
    ) -> list[dict[str, Any]]:
        subscribers: list[dict[str, Any]] = []

        channel = await self.client.get_entity(channel_username)

        offset = 0

        while len(subscribers) < limit:
            try:
                result = await self.client(
                    GetParticipantsRequest(
                        channel=channel,
                        filter=ChannelParticipantsSearch(""),
                        offset=offset,
                        limit=batch_size,
                        hash=0,
                    )
                )

                if not result.users:
                    break

                for user in result.users:
                    if len(subscribers) >= limit:
                        break

                    if getattr(user, "bot", False):
                        continue

                    full_user = await self._safe_get_full_user(user)

                    subscribers.append(
                        {
                            "id": user.id,
                            "username": self._normalize(user.username),
                            "first_name": self._normalize(user.first_name),
                            "last_name": self._normalize(user.last_name),
                            "bio": self._normalize(full_user.get("bio")),
                            "has_photo": user.photo is not None,
                            "status": str(user.status) if user.status else "",
                            "hidden_status": user.status is None,
                            "is_bot": bool(getattr(user, "bot", False)),
                        }
                    )

                offset += len(result.users)

                if len(result.users) < batch_size:
                    break

            except FloodWaitError as error:
                print(f"Telegram ограничил частоту запросов. Ожидание {error.seconds} сек.")
                await asyncio.sleep(error.seconds)

        return subscribers

    async def _safe_get_full_user(self, user: Any) -> dict[str, Any]:
        """
        Пытается получить расширенную информацию о пользователе.
        Если Telegram не отдаёт bio, возвращается пустое значение.
        """

        try:
            full_user = await self.client.get_entity(user.id)

            bio = getattr(full_user, "about", None)

            return {
                "bio": bio or "",
            }

        except Exception:
            return {
                "bio": "",
            }

    @staticmethod
    def _normalize(value: Any) -> str:
        if value is None:
            return ""

        return str(value).strip()
