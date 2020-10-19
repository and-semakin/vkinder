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


class SelectCountryState(State):
    key = "select_country"

    text = (
        "Шаг 1 из %s. Отлично! Для начала нужно указать страну, в которой ты хочешь "
        "найти себе пару. Если нужной страны нет на клавиатуре ниже, "
        "то просто отправь мне её название."
    ) % (TOTAL_STEPS,)

    @classmethod
    def enter(cls, bot: "Bot", event: Event) -> None:
        user = bot.storage.get(User, event.user_id)

        country_id = user.country_id

        keyboard = VkKeyboard(one_time=True)

        country_title = None
        if country_id:
            country_title = bot.session.method(
                "database.getCountriesById", {"country_ids": country_id}
            )[0]["title"]
            keyboard.add_button(country_title, color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()

        country_titles = [
            country["title"]
            for country in bot.session.method("database.getCountries", {"count": 6})[
                "items"
            ]
            if country["title"] != country_title
        ]
        for countries_row in chunked(country_titles, 2):
            for title in countries_row:
                keyboard.add_button(title, color=VkKeyboardColor.SECONDARY)
            keyboard.add_line()

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

        user = bot.storage.get(User, event.user_id)

        country_title_query = event.text.lower()

        countries = bot.session.method(
            "database.getCountries", {"need_all": 1, "count": 1000}
        )["items"]

        country_id: int
        country_title: str
        for country in countries:
            if country["title"].lower() == country_title_query:
                country_id = country["id"]
                country_title = country["title"]
                break
        else:
            return StateName.SELECT_COUNTRY_ERROR

        user.country_id = country_id
        write_msg(bot.group_session, event.user_id, f"Выбрана страна: {country_title}")
        bot.storage.save(user)
        return StateName.SELECT_CITY


class SelectCountryErrorState(SelectCountryState):
    key = "select_country_error"

    text = (
        "Хм, я не знаю такой страны. Убедись, пожалуйста, что название "
        "набрано без ошибок и попробуй снова."
    )
