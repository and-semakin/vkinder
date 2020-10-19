from typing import TYPE_CHECKING

from more_itertools import chunked
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import Event

from vkinder.helpers import write_msg
from vkinder.models import User
from vkinder.state._base import TOTAL_STEPS, State

if TYPE_CHECKING:
    from vkinder.bot import Bot
    from vkinder.state import StateName


class SelectCityState(State):
    key = "select_city"

    text = (
        "Шаг 2 из %s. Введи название города, в котором ты хочешь производить поиск. "
        "Если для твоего города нет кнопки, то введи название текстом."
    ) % (TOTAL_STEPS,)

    @classmethod
    def enter(cls, bot: "Bot", event: Event) -> None:
        user = bot.storage.get(User, event.user_id)

        assert user.country_id

        country_id = user.country_id
        city_id = user.city_id

        keyboard = VkKeyboard(one_time=True)

        city_title = None
        if city_id:
            city_title = bot.session.method(
                "database.getCitiesById", {"city_ids": city_id}
            )[0]["title"]
            keyboard.add_button(city_title, color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()

        city_titles = [
            city["title"]
            for city in bot.session.method(
                "database.getCities", {"country_id": country_id, "count": 6}
            )["items"]
            if city["title"] != city_title
        ]
        for cities_row in chunked(city_titles, 2):
            for title in cities_row:
                keyboard.add_button(title, color=VkKeyboardColor.SECONDARY)
            keyboard.add_line()

        keyboard.add_button("Назад", color=VkKeyboardColor.SECONDARY)
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)

        write_msg(
            bot.group_session,
            event.user_id,
            cls.text,
            keyboard=keyboard.get_keyboard(),
        )

    @classmethod
    def leave(cls, bot: "Bot", event: Event) -> "StateName":
        from vkinder.state import StateName

        if event.text == "Отмена":
            return StateName.HELLO_AGAIN
        if event.text == "Назад":
            return StateName.SELECT_COUNTRY

        user = bot.storage.get(User, event.user_id)

        country_id = user.country_id

        found_cities = bot.session.method(
            "database.getCities",
            {"country_id": country_id, "q": event.text.lower(), "count": 1},
        )["items"]

        if not found_cities:
            return StateName.SELECT_CITY_ERROR

        city = found_cities[0]
        city_title = city["title"]
        city_id = city["id"]

        user.city_id = city_id
        write_msg(bot.group_session, event.user_id, f"Выбран город: {city_title}")
        bot.storage.save(user)
        return StateName.SELECT_SEX


class SelectCityErrorState(SelectCityState):
    key = "select_city_error"

    text = (
        "Не могу найти такой город в выбранной стране. "
        "Убедись, что в твоём сообщении нет очпяток, "
        "и давай попробуем ещё раз. "
        "Введи название города или выбери его на клавиатуре ниже."
    )
