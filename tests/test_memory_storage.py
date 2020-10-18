import uuid

import pytest

from vkinder.storage.base import (
    ItemAlreadyExistsInStorageError,
    ItemNotFoundInStorageError,
    StorageItem,
)
from vkinder.storage.memory_storage import MemoryStorage


class Apple(StorageItem):
    type = "apple"

    _id: uuid.UUID
    color: str
    weight: float

    @property
    def id(self) -> uuid.UUID:
        return self._id


@pytest.fixture()
def storage() -> MemoryStorage:
    return MemoryStorage()


class TestGet:
    def test_returns_item_if_found(self, storage: MemoryStorage) -> None:
        storage._data[Apple.type] = {}
        item = Apple(_id=uuid.uuid4(), color="red", weight=0.2)
        storage._data[Apple.type][item.id] = item

        found_item = storage.get(Apple.type, item.id)

        assert item.id == found_item.id

    def test_raises_if_item_not_found(self, storage: MemoryStorage) -> None:
        with pytest.raises(ItemNotFoundInStorageError):
            storage.get(Apple.type, uuid.uuid4())


class TestSave:
    def test_saves_new_item(self, storage: MemoryStorage) -> None:
        item = Apple(_id=uuid.uuid4(), color="red", weight=0.2)
        assert not storage._data

        storage.save(item)

        assert storage._data
        assert Apple.type in storage._data
        assert item.id in storage._data[Apple.type]
        saved_item = storage._data[Apple.type][item.id]
        assert item.id == saved_item.id

    def test_overwrites_existing_item(self, storage: MemoryStorage) -> None:
        item = Apple(_id=uuid.uuid4(), color="red", weight=0.2)
        assert not storage._data

        storage.save(item)

        another_item = Apple(_id=item.id, color="green", weight=0.3)
        storage.save(another_item)

        found_item = storage.get(Apple.type, item.id)
        assert another_item.id == found_item.id
        assert another_item.color == found_item.color
        assert another_item.weight == found_item.weight

    def test_raises_if_restricted_to_overwrite_existing_item(
        self, storage: MemoryStorage
    ) -> None:
        item = Apple(_id=uuid.uuid4(), color="red", weight=0.2)
        assert not storage._data

        storage.save(item)

        another_item = Apple(_id=item.id, color="green", weight=0.3)
        with pytest.raises(ItemAlreadyExistsInStorageError):
            storage.save(another_item, overwrite=False)

        found_item = storage.get(Apple.type, item.id)
        assert found_item.id == item.id
        assert found_item.color == item.color
        assert found_item.weight == item.weight
