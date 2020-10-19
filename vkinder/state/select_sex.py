from typing import TYPE_CHECKING

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import Event

from vkinder.helpers import write_msg
from vkinder.models import User
from vkinder.state._base import TOTAL_STEPS, State

if TYPE_CHECKING:
    from vkinder.bot import Bot
    from vkinder.state import StateName


class SelectSexState(State):
    key = "select_sex"

    text = (
        "Шаг 3 из %s. Отлично! Теперь выбери пол второй половинки, которую ты ищешь."
    ) % (TOTAL_STEPS,)

    @classmethod
    def enter(cls, bot: "Bot", event: Event) -> None:
        keyboard = VkKeyboard(one_time=True)

        keyboard.add_button("Мужской", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Женский", color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button("Любой", color=VkKeyboardColor.SECONDARY)
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
            return StateName.SELECT_CITY

        user = bot.storage.get(User, event.user_id)

        selected_sex: str
        if event.text == "Мужской":
            user.sex = 2
            selected_sex = "мужчин"
        elif event.text == "Женский":
            user.sex = 1
            selected_sex = "женщин"
        elif event.text == "Любой":
            user.sex = 0
            selected_sex = "партнёров любого пола"
        else:
            return StateName.SELECT_SEX_ERROR

        write_msg(
            bot.group_session, event.user_id, f"Отлично! Будем искать {selected_sex}!"
        )
        bot.storage.save(user)
        return StateName.SELECT_AGE


class SelectSexErrorState(SelectSexState):
    key = "select_sex_error"

    text = (
        "Хм, не уверен, что в ВК найдутся люди такого пола. "
        "Лучше используй кнопки, чтобы выбрать пол искомого партнёра."
    )
