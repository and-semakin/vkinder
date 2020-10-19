import abc
from typing import TYPE_CHECKING

from vk_api.longpoll import Event

if TYPE_CHECKING:
    from vkinder.bot import Bot
    from vkinder.state import StateName

TOTAL_STEPS = 4


class State(abc.ABC):
    key: str

    @classmethod
    @abc.abstractmethod
    def enter(cls, bot: "Bot", event: Event) -> None:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def leave(cls, bot: "Bot", event: Event) -> "StateName":
        raise NotImplementedError()
