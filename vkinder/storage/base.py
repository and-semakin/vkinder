import abc
import uuid
from typing import Any, Dict


class StorageItem(abc.ABC):
    type: str
    _data: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self._data = kwargs

    @property
    @abc.abstractmethod
    def id(self) -> uuid.UUID:
        raise NotImplementedError()

    def __getattr__(self, item: str) -> Any:
        return self._data[item]


class ItemNotFoundInStorageError(Exception):
    """Item not found in storage."""


class ItemAlreadyExistsInStorageError(Exception):
    """Item already exists in storage."""


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def get(self, type: str, id: uuid.UUID) -> StorageItem:
        raise NotImplementedError()

    @abc.abstractmethod
    def save(self, item: StorageItem, overwrite: bool = True) -> None:
        raise NotImplementedError()
