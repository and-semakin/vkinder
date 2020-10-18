from typing import MutableMapping

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from vkinder.config import config
from vkinder.state import states, write_msg
from vkinder.user import User

users: MutableMapping[str, User] = {}


def main():
    session = vk_api.VkApi(token=config.vk_user_token)
    group_session = vk_api.VkApi(token=config.vk_group_token)

    longpoll = VkLongPoll(group_session, config.vk_group_id)

    for event in longpoll.listen():
        if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
            continue

        if event.user_id not in users:
            user = User(event.user_id, "hello", {})
            users[event.user_id] = user
            states[user.state].enter(user, session, group_session, event)
            continue

        user = users[event.user_id]

        if event.text == "/state":
            write_msg(
                group_session,
                event.user_id,
                (
                    f"Пользователь находится в состоянии {user.state}. "
                    f"Ассоциированные данные: {user.data}",
                ),
            )
            continue

        new_state = states[user.state].leave(user, session, group_session, event)
        user.state = new_state
        states[new_state].enter(user, session, group_session, event)


if __name__ == "__main__":
    main()
