import asyncio
import json
from pathlib import Path
from uuid import uuid4

from app.models import UserAccount


class UserStorage:
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._lock = asyncio.Lock()

    async def get_by_phone(self, phone: str) -> UserAccount | None:
        users = await asyncio.to_thread(self._read_file)
        return next((user for user in users if user.phone == phone), None)

    async def get_by_id(self, user_id: str) -> UserAccount | None:
        users = await asyncio.to_thread(self._read_file)
        return next((user for user in users if user.id == user_id), None)

    async def create(self, phone: str, password_hash: str) -> tuple[UserAccount | None, bool]:
        async with self._lock:
            users = await asyncio.to_thread(self._read_file)
            if any(user.phone == phone for user in users):
                return None, False
            is_first_user = not users
            user = UserAccount(id=str(uuid4()), phone=phone, password_hash=password_hash)
            users.append(user)
            await asyncio.to_thread(self._write_file, users)
            return user, is_first_user

    def _read_file(self) -> list[UserAccount]:
        if not self._file_path.exists():
            return []
        with self._file_path.open(encoding="utf-8") as file:
            payload = json.load(file)
        if not isinstance(payload, list):
            raise ValueError("Файл пользователей должен содержать JSON-массив")
        return [UserAccount.model_validate(item) for item in payload]

    def _write_file(self, users: list[UserAccount]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(
                [user.model_dump() for user in users],
                file,
                ensure_ascii=False,
                indent=2,
            )
