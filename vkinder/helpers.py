from random import randrange
from typing import Any, Dict, Optional

from vk_api import VkApi


def write_msg(
    session: VkApi,
    user_id: int,
    message: str,
    attachment: Optional[str] = None,
    keyboard: Optional[Dict[str, Any]] = None,
) -> None:
    """Отправка сообщения пользователю"""
    values = {"user_id": user_id, "message": message, "random_id": randrange(10 ** 7)}
    if attachment:
        values["attachment"] = attachment
    if keyboard:
        values["keyboard"] = keyboard

    session.method("messages.send", values)
