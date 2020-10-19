from typing import TYPE_CHECKING

from vk_api.longpoll import Event

from vkinder.models import User
from vkinder.state._base import State

if TYPE_CHECKING:
    from vkinder.bot import Bot
    from vkinder.state import StateName


class InitialState(State):
    key = "initial"

    @classmethod
    def enter(cls, bot: "Bot", event: Event) -> None:
        pass

    @classmethod
    def leave(cls, bot: "Bot", event: Event) -> "StateName":
        from vkinder.state import StateName

        user = bot.storage.get(User, event.user_id)

        user_info = bot.session.method(
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

        user.first_name = first_name
        user.last_name = last_name
        user.country_id = country_id
        user.city_id = city_id

        bot.storage.save(user)
        return StateName.HELLO
