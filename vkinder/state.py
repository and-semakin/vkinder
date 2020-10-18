import abc
from random import randrange

from more_itertools import chunked
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import Event

from vkinder.user import User


def write_msg(session: VkApi, user_id, message, attachment=None, keyboard=None) -> None:
    """Отправка сообщения пользователю"""
    values = {"user_id": user_id, "message": message, "random_id": randrange(10 ** 7)}
    if attachment:
        values["attachment"] = attachment
    if keyboard:
        values["keyboard"] = keyboard

    session.method("messages.send", values)


class State(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def enter(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> None:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def leave(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> str:
        raise NotImplementedError()


class HelloState(State):
    text = (
        "Привет, {first_name}! "
        "Я бот-сваха, прямо как Роза Сябитова, только со мной не страшно. "
        "Я помогу тебе найти идеальную пару! "
        "Ну, или хотя бы какую-нибудь. Приступим? "
        "Жми на кнопку!"
    )

    @classmethod
    def enter(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> None:
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

        # update data if user changed his info
        user.data = {
            "first_name": first_name,
            "last_name": last_name,
            "country_id": country_id,
            "city_id": city_id,
            **user.data,
        }

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Новый поиск", color=VkKeyboardColor.PRIMARY)

        write_msg(
            group_session,
            event.user_id,
            cls.text.format(first_name=first_name),
            keyboard=keyboard.get_keyboard(),
        )

    @classmethod
    def leave(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> str:
        if event.text == "Новый поиск":
            return "select_country"
        else:
            return "hello_error"


class HelloErrorState(HelloState):
    text = (
        "Извини, {first_name}, я не знаю такой команды. "
        "Используй, пожалуйста, кнопки, чтобы мне было проще тебя понимать. "
        "Нажми на кнопку ниже, чтобы начать новый поиск."
    )


class SelectCountryState(State):
    text = (
        "Отлично! Для начала нужно указать страну, в которой ты хочешь "
        "найти себе пару. Если нужной страны нет на клавиатуре ниже, "
        "то просто отправь мне её название."
    )

    @classmethod
    def enter(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> None:
        country_id = user.data["country_id"]

        keyboard = VkKeyboard(one_time=True)

        country_title = None
        if country_id:
            country_title = session.method(
                "database.getCountriesById", {"country_ids": country_id}
            )[0]["title"]
            keyboard.add_button(country_title, color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()

        country_titles = [
            country["title"]
            for country in session.method("database.getCountries", {"count": 6})[
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
            group_session,
            event.user_id,
            cls.text,
            keyboard=keyboard.get_keyboard(),
        )

    @classmethod
    def leave(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> str:
        if event.text == "Отмена":
            return "hello"

        country_title_query = event.text.lower()

        countries = session.method(
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
            return "select_country_error"

        user.data["country_id"] = country_id
        write_msg(group_session, event.user_id, f"Выбрана страна: {country_title}")
        return "select_city"


class SelectCountryErrorState(SelectCountryState):
    text = (
        "Хм, я не знаю такой страны. Убедись, пожалуйста, что название "
        "набрано без ошибок и попробуй снова."
    )


class SelectCityState(State):
    text = (
        "Введи название города, в котором ты хочешь производить поиск. "
        "Если для твоего города нет кнопки, то введи название текстом."
    )

    @classmethod
    def enter(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> None:
        assert "country_id" in user.data
        assert "city_id" in user.data

        country_id = user.data["country_id"]
        city_id = user.data["city_id"]

        keyboard = VkKeyboard(one_time=True)

        city_title = None
        if city_id:
            city_title = session.method(
                "database.getCitiesById", {"city_ids": city_id}
            )[0]["title"]
            keyboard.add_button(city_title, color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()

        city_titles = [
            city["title"]
            for city in session.method(
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
            group_session,
            event.user_id,
            cls.text,
            keyboard=keyboard.get_keyboard(),
        )

    @classmethod
    def leave(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> str:
        if event.text == "Отмена":
            return "hello"
        if event.text == "Назад":
            return "select_country"

        assert "country_id" in user.data
        country_id = user.data["country_id"]

        found_cities = session.method(
            "database.getCities",
            {"country_id": country_id, "q": event.text.lower(), "count": 1},
        )["items"]

        if not found_cities:
            return "select_city_error"

        city = found_cities[0]
        city_title = city["title"]
        city_id = city["id"]

        user.data["city_id"] = city_id
        write_msg(group_session, event.user_id, f"Выбран город: {city_title}")
        return "select_sex"


class SelectCityErrorState(SelectCityState):
    text = (
        "Не могу найти такой город в выбранной стране. "
        "Убедись, что в твоём сообщении нет очпяток, "
        "и давай попробуем ещё раз. "
        "Введи название города или выбери его на клавиатуре ниже."
    )


class SelectSexState(State):
    text = "Отлично! Теперь выбери пол второй половинки, которую ты ищешь."

    @classmethod
    def enter(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> None:
        keyboard = VkKeyboard(one_time=True)

        keyboard.add_button("Мужской", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Женский", color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("Любой", color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()

        keyboard.add_button("Назад", color=VkKeyboardColor.SECONDARY)
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)

        write_msg(
            group_session, event.user_id, cls.text, keyboard=keyboard.get_keyboard()
        )

    @classmethod
    def leave(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> str:
        if event.text == "Отмена":
            return "hello"
        if event.text == "Назад":
            return "select_city"

        selected_sex: str
        if event.text == "Мужской":
            user.data["sex"] = 1
            selected_sex = "мужчин"
        elif event.text == "Женский":
            user.data["sex"] = 2
            selected_sex = "женщин"
        elif event.text == "Любой":
            user.data["sex"] = 0
            selected_sex = "партнёров любого пола"
        else:
            return "select_sex_error"

        write_msg(
            group_session, event.user_id, f"Отлично! Будем искать {selected_sex}!"
        )
        return "select_age"


class SelectSexErrorState(SelectSexState):
    text = (
        "Хм, не уверен, что в ВК найдутся люди такого пола. "
        "Лучше используй кнопки, чтобы выбрать пол искомого партнёра."
    )


class SelectAgeState(State):
    @classmethod
    def enter(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> None:
        write_msg(group_session, event.user_id, "Здесь ничего нет! Это конец!")

    @classmethod
    def leave(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> str:
        return "hello"


class ListMatchesState(State):
    @classmethod
    def enter(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> None:
        pass

    @classmethod
    def leave(
        cls, user: User, session: VkApi, group_session: VkApi, event: Event
    ) -> str:
        pass


states = {
    # приветствие
    "hello": HelloState,
    "hello_error": HelloErrorState,
    # выбор страны
    "select_country": SelectCountryState,
    "select_country_error": SelectCountryErrorState,
    # выбор города
    "select_city": SelectCityState,
    "select_city_error": SelectCityErrorState,
    # выбор пола
    "select_sex": SelectSexState,
    "select_sex_error": SelectSexErrorState,
    # выбор возраста
    "select_age": SelectAgeState,
    # просмотр результатов поиска
    "list_matches": ListMatchesState,
}
