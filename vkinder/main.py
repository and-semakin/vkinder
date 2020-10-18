import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from vkinder.config import config
from vkinder.models import User
from vkinder.state import INITIAL_STATE, states, write_msg
from vkinder.storage.base import ItemNotFoundInStorageError
from vkinder.storage.memory_storage import MemoryStorage

storage = MemoryStorage()


def main():
    session = vk_api.VkApi(token=config.vk_user_token)
    group_session = vk_api.VkApi(token=config.vk_group_token)

    longpoll = VkLongPoll(group_session, config.vk_group_id)

    for event in longpoll.listen():
        if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
            continue

        try:
            user = storage.get(User.type, event.user_id)
        except ItemNotFoundInStorageError:
            user_info = session.method(
                "users.get", {"user_ids": event.user_id, "fields": "country,city"}
            )[0]
            first_name = user_info["first_name"]
            last_name = user_info["last_name"]

            try:
                country_id = user_info["country"]["id"]
            except KeyError:
                country_id = None

            try:
                city_id = user_info["city"]["id"]
            except KeyError:
                city_id = None

            user = User(
                vk_id=event.user_id,
                state=INITIAL_STATE,
                first_name=first_name,
                last_name=last_name,
                country_id=country_id,
                city_id=city_id,
            )
            storage.save(user)

            states[user.state].enter(storage, user, session, group_session, event)
            continue

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


if __name__ == "__main__":
    main()
