from typing import TYPE_CHECKING

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import Event

from vkinder.helpers import write_msg
from vkinder.models import Match, User
from vkinder.state._base import State

if TYPE_CHECKING:
    from vkinder.bot import Bot
    from vkinder.state import StateName


class ListMatchesState(State):
    key = "list_matches"

    @classmethod
    def enter(cls, bot: "Bot", event: Event) -> None:
        user = bot.storage.get(User, event.user_id)

        assert user.current_search
        assert user.current_search_item is not None

        search_id = user.current_search

        matches = bot.storage.find(Match, lambda match: match.search_id == search_id)

        item_index = user.current_search_item
        assert 0 <= item_index < len(matches)

        match = matches[item_index]

        photos = bot.session.method(
            "photos.get",
            values={
                "owner_id": match.vk_id,
                "album_id": "profile",
                "count": 1000,
                "extended": 1,
                "photo_sizes": 1,
                "type": "m",
            },
        )["items"]
        photos = sorted(photos, key=lambda p: p["likes"]["count"], reverse=True)[:3]
        photos = ",".join(f"photo{p['owner_id']}_{p['id']}" for p in photos)

        write_msg(
            bot.group_session,
            event.user_id,
            (
                f"{item_index+1}. {match.first_name} {match.last_name}: "
                f"https://vk.com/id{match.vk_id}"
            ),
            attachment=photos,
        )

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Да", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button("Нет", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)

        write_msg(
            bot.group_session,
            event.user_id,
            "Нравится?",
            keyboard=keyboard.get_keyboard(),
        )

    @classmethod
    def leave(cls, bot: "Bot", event: Event) -> "StateName":
        from vkinder.state import StateName

        user = bot.storage.get(User, event.user_id)

        if event.text == "Отмена":
            user.current_search = None
            user.current_search_item = None
            bot.storage.save(user)
            return StateName.HELLO_AGAIN

        assert user.current_search
        assert user.current_search_item is not None

        search_id = user.current_search

        matches = bot.storage.find(Match, lambda match: match.search_id == search_id)

        item_index = user.current_search_item
        assert 0 <= item_index < len(matches)

        match = matches[item_index]

        match.seen = True

        if event.text == "Да":
            match.liked = True
        else:
            match.liked = False

        user.current_search_item += 1

        bot.storage.save(user)
        return StateName.LIST_MATCHES
