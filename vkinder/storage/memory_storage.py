import uuid
from typing import Dict

from vkinder.storage.base import (
    BaseStorage,
    ItemAlreadyExistsInStorageError,
    ItemNotFoundInStorageError,
    StorageItem,
)


class MemoryStorage(BaseStorage):
    _data: Dict[str, Dict[uuid.UUID, StorageItem]]

    def __init__(self) -> None:
        self._data = {}

    def get(self, type: str, id: uuid.UUID) -> StorageItem:
        table = self._data.setdefault(type, {})
        if id not in table:
            raise ItemNotFoundInStorageError()
        return table[id]

    def save(self, item: StorageItem, overwrite: bool = True) -> None:
        table = self._data.setdefault(item.type, {})
        if item.id in table and not overwrite:
            raise ItemAlreadyExistsInStorageError()
        table[item.id] = item
