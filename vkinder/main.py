from pathlib import Path

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from vkinder.config import config
from vkinder.models import User
from vkinder.state import INITIAL_STATE, states, write_msg
from vkinder.storage.base import ItemNotFoundInStorageError
from vkinder.storage.memory_storage import PersistentStorage

storage = PersistentStorage(Path(__file__).parent.resolve() / "data.pickle")


def main():
    session = vk_api.VkApi(token=config.vk_user_token)
    group_session = vk_api.VkApi(token=config.vk_group_token)

    longpoll = VkLongPoll(group_session, config.vk_group_id)

    for event in longpoll.listen():
        if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
            continue

        # проверим, новый ли этот пользователь или нет
        try:
            user = storage.get(User, event.user_id)
        except ItemNotFoundInStorageError:
            # если новый, то создадим пустого с состоянием для инициализации
            user = User(
                vk_id=event.user_id,
                state=INITIAL_STATE,
            )
            storage.save(user)

        if event.text == "/state":
            write_msg(
                group_session,
                event.user_id,
                (
                    f"Пользователь находится в состоянии {user.state}. "
                    f"Ассоциированные данные: {user.__dict__}",
                ),
            )
            states[user.state].enter(storage, user, session, group_session, event)
            continue

        new_state = states[user.state].leave(
            storage, user, session, group_session, event
        )
        user.state = new_state
        states[new_state].enter(storage, user, session, group_session, event)
        storage.persist()


if __name__ == "__main__":
    main()
