import logging
from itertools import cycle
from typing import NoReturn

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from vkinder.config import Config
from vkinder.helpers import write_msg
from vkinder.models import User
from vkinder.state import StateName, states
from vkinder.storage.base import BaseStorage, ItemNotFoundInStorageError

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, config: Config, storage: BaseStorage) -> None:
        self.storage = storage

        tokens = config.vk_user_tokens.split(",")
        logger.debug("Found %s access tokens!", len(tokens))
        self._sessions = [vk_api.VkApi(token=token) for token in tokens]
        # будем использовать все сессии по очереди, чтобы обойти ограничение
        # на 3 запроса в секунду. а вдруг случится хайлоад?
        self.sessions = cycle(self._sessions)

        self.group_session = vk_api.VkApi(token=config.vk_group_token)
        self.longpoll = VkLongPoll(self.group_session, config.vk_group_id)

    @property
    def session(self) -> vk_api.VkApi:
        return next(self.sessions)

    def run(self) -> NoReturn:
        for event in self.longpoll.listen():
            if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
                continue

            # проверим, новый ли этот пользователь или нет
            try:
                user = self.storage.get(User, event.user_id)
            except ItemNotFoundInStorageError:
                # если новый, то создадим пустого с состоянием для инициализации
                user = User(
                    vk_id=event.user_id,
                    state=StateName.INITIAL,
                )
                self.storage.save(user)

            if event.text == "/state":
                write_msg(
                    self.group_session,
                    event.user_id,
                    (
                        f"Пользователь находится в состоянии {user.state}. "
                        f"Ассоциированные данные: {user.__dict__}"
                    ),
                )
                states[user.state].enter(self, event)
                continue

            new_state = states[user.state].leave(self, event).value.key
            user.state = new_state
            states[new_state].enter(self, event)
            self.storage.persist()

        raise Exception("The previous loop should never exit!")
