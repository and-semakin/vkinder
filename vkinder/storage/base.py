import abc
from typing import Any, Callable, List, Type, TypeVar


class StorageItem(abc.ABC):
    type: str

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    @abc.abstractmethod
    def id(self) -> Any:
        raise NotImplementedError()


T = TypeVar("T", bound=StorageItem)


class ItemNotFoundInStorageError(Exception):
    """Item not found in storage."""


class ItemAlreadyExistsInStorageError(Exception):
    """Item already exists in storage."""


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def get(self, type: Type[T], id: Any) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def save(self, item: StorageItem, overwrite: bool = True) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def find(self, type: Type[T], where: Callable[[T], bool]) -> List[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def persist(self) -> None:
        raise NotImplementedError()
