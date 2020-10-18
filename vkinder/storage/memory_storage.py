import uuid
from typing import Any, Callable, Dict, List, Type, TypeVar, cast

from vkinder.storage.base import (
    BaseStorage,
    ItemAlreadyExistsInStorageError,
    ItemNotFoundInStorageError,
    StorageItem,
)

T = TypeVar("T", bound=StorageItem)


class MemoryStorage(BaseStorage):
    _data: Dict[str, Dict[uuid.UUID, StorageItem]]

    def __init__(self) -> None:
        self._data = {}

    def get(self, type: Type[T], id: uuid.UUID) -> T:
        table = self._data.setdefault(type.type, {})
        if id not in table:
            raise ItemNotFoundInStorageError()
        return cast(T, table[id])

    def save(self, item: StorageItem, overwrite: bool = True) -> None:
        table = self._data.setdefault(item.type, {})
        if item.id in table and not overwrite:
            raise ItemAlreadyExistsInStorageError()
        table[item.id] = item

    def find(self, type: Type[T], where: Callable[[T], bool]) -> List[T]:
        table = cast(Dict[Any, T], self._data.setdefault(type.type, {}))
        matching = [item for item in table.values() if where(item)]
        return matching
