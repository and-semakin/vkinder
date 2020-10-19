from typing import TYPE_CHECKING

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import Event

from vkinder.helpers import write_msg
from vkinder.models import User
from vkinder.state._base import State

if TYPE_CHECKING:
    from vkinder.bot import Bot
    from vkinder.state import StateName


class HelloState(State):
    key = "hello"

    text = (
        "Привет, {first_name}! "
        "Я бот-сваха, прямо как Роза Сябитова, только со мной не страшно. "
        "Я помогу тебе найти идеальную пару! "
        "Ну, или хотя бы какую-нибудь. Приступим? "
        "Жми на кнопку!"
    )

    @classmethod
    def enter(cls, bot: "Bot", event: Event) -> None:
        user = bot.storage.get(User, event.user_id)

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Новый поиск", color=VkKeyboardColor.PRIMARY)

        write_msg(
            bot.group_session,
            event.user_id,
            cls.text.format(first_name=user.first_name),
            keyboard=keyboard.get_keyboard(),
        )

    @classmethod
    def leave(cls, bot: "Bot", event: Event) -> "StateName":
        from vkinder.state import StateName

        if event.text == "Новый поиск":
            return StateName.SELECT_COUNTRY
        else:
            return StateName.HELLO_ERROR


class HelloErrorState(HelloState):
    key = "hello_error"

    text = (
        "Извини, {first_name}, я не знаю такой команды. "
        "Используй, пожалуйста, кнопки, чтобы мне было проще тебя понимать. "
        "Нажми на кнопку ниже, чтобы начать новый поиск."
    )


class HelloAgainState(HelloState):
    key = "hello_again"

    text = (
        "Ты находишься в главном меню, {first_name}. Начнём новый поиск? "
        "Если ты уже искал людей раньше, то можно просмотреть результаты "
        "предыдущих поисков."
    )
