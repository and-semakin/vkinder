import os
import pickle
from pathlib import Path
from typing import Any, Callable, Dict, List, Type, TypeVar, Union, cast

from vkinder.storage.base import (
    BaseStorage,
    ItemAlreadyExistsInStorageError,
    ItemNotFoundInStorageError,
    StorageItem,
)

T = TypeVar("T", bound=StorageItem)


class MemoryStorage(BaseStorage):
    _data: Dict[str, Dict[Any, StorageItem]]

    def __init__(self) -> None:
        self._data = {}

    def get(self, type: Type[T], id: Any) -> T:
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

    def persist(self) -> None:
        pass


class PersistentStorage(MemoryStorage):
    def __init__(self, file: Union[os.PathLike, str]) -> None:
        super().__init__()
        self.file = Path(file)
        self._load()

    def _load(self) -> None:
        if not self.file.exists():
            self.persist()

        with self.file.open("rb") as f:
            self._data = pickle.load(f)

    def persist(self) -> None:
        with self.file.open("wb") as f:
            pickle.dump(self._data, f)
