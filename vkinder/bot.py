from typing import NoReturn

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from vkinder.config import Config
from vkinder.models import User
from vkinder.state import INITIAL_STATE, states, write_msg
from vkinder.storage.base import BaseStorage, ItemNotFoundInStorageError


class Bot:
    def __init__(self, config: Config, storage: BaseStorage) -> None:
        self.storage = storage

        self.session = vk_api.VkApi(token=config.vk_user_token)

        self.group_session = vk_api.VkApi(token=config.vk_group_token)
        self.longpoll = VkLongPoll(self.group_session, config.vk_group_id)

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
                    state=INITIAL_STATE,
                )
                self.storage.save(user)

            if event.text == "/state":
                write_msg(
                    self.group_session,
                    event.user_id,
                    (
                        f"Пользователь находится в состоянии {user.state}. "
                        f"Ассоциированные данные: {user.__dict__}",
                    ),
                )
                states[user.state].enter(
                    self.storage, user, self.session, self.group_session, event
                )
                continue

            new_state = states[user.state].leave(
                self.storage, user, self.session, self.group_session, event
            )
            user.state = new_state
            states[new_state].enter(
                self.storage, user, self.session, self.group_session, event
            )
            self.storage.persist()

        raise Exception("The previous loop should never exit!")
