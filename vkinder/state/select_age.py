import datetime
import uuid
from typing import TYPE_CHECKING

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import Event

from vkinder.helpers import write_msg
from vkinder.models import Match, Search, User
from vkinder.state._base import TOTAL_STEPS, State

if TYPE_CHECKING:
    from vkinder.bot import Bot
    from vkinder.state import StateName


class SelectAgeState(State):
    key = "select_age"

    text = (
        "Шаг 4 из %s. Давай выберем диапазон возрастов, который тебя интересует. "
        "Можешь выбрать из предложенных на клавиатуре вариантов, либо "
        "отправить свой диапазон возрастов в виде двух чисел, разделённых "
        "минусом, например: 20-21. Если интересует конкретный возраст, то "
        "можно отправить одно число, например: 42."
    ) % (TOTAL_STEPS,)

    @classmethod
    def enter(cls, bot: "Bot", event: Event) -> None:
        keyboard = VkKeyboard(one_time=True)

        keyboard.add_button("16-20")
        keyboard.add_button("20-25")
        keyboard.add_line()
        keyboard.add_button("25-30")
        keyboard.add_button("30-35")
        keyboard.add_line()
        keyboard.add_button("35-40")
        keyboard.add_button("40-50")
        keyboard.add_line()

        keyboard.add_button("Назад", color=VkKeyboardColor.SECONDARY)
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)

        write_msg(
            bot.group_session, event.user_id, cls.text, keyboard=keyboard.get_keyboard()
        )

    @classmethod
    def leave(cls, bot: "Bot", event: Event) -> "StateName":
        from vkinder.state import StateName

        if event.text == "Отмена":
            return StateName.HELLO_AGAIN
        if event.text == "Назад":
            return StateName.SELECT_SEX

        user = bot.storage.get(User, event.user_id)

        msg: str = event.text.lower().strip()

        age_from: int
        age_to: int

        if "-" in msg:
            try:
                from_, to = msg.split("-")
                age_from = int(from_.strip())
                age_to = int(to.strip())
            except ValueError:
                return StateName.SELECT_AGE_ERROR
        else:
            try:
                age_from = age_to = int(msg)
            except ValueError:
                return StateName.SELECT_AGE_ERROR

        user.age_from = age_from
        user.age_to = age_to
        write_msg(
            bot.group_session,
            event.user_id,
            (
                f"Выбран возрастной диапазон: {age_from}-{age_to} лет. "
                "Начинаем поиск!"
            ),
        )

        assert user.country_id
        assert user.city_id
        assert user.sex is not None
        assert user.age_from
        assert user.age_to

        search_params = {
            "country": user.country_id,
            "city": user.city_id,
            "sex": user.sex,
            "age_from": user.age_from,
            "age_to": user.age_to,
        }

        search_results = bot.session.method(
            "users.search",
            {
                "sort": 0,
                "count": 1000,
                "has_photo": 1,
                "status": "6",
                "fields": "id,verified,domain",
                "can_access_closed": 1,
                "is_closed": 0,
                **search_params,
            },
        )["items"]
        search_results = [
            person for person in search_results if not person["is_closed"]
        ]

        search_id = uuid.uuid4()
        search = Search(
            uuid=search_id,
            user_id=event.user_id,
            datetime=datetime.datetime.utcnow().isoformat(),
            **search_params,
        )
        bot.storage.save(search)

        for person in search_results:
            match = Match(
                uuid=uuid.uuid4(),
                search_id=search_id,
                vk_id=person["id"],
                first_name=person["first_name"],
                last_name=person["last_name"],
            )
            bot.storage.save(match)

        user.current_search = search_id
        user.current_search_item = 0
        bot.storage.save(user)
        return StateName.LIST_MATCHES


class SelectAgeErrorState(SelectAgeState):
    key = "select_age_error"

    text = (
        "Не могу распарсить присланный тобой диапазон возрастов. "
        "Примеры валидных диапазонов: 18-30, 18-18, 18. Попробуй ещё раз!"
    )
