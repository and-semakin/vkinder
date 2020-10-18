from uuid import UUID, uuid4

import pytest

from vkinder.storage.base import (
    ItemAlreadyExistsInStorageError,
    ItemNotFoundInStorageError,
    StorageItem,
)
from vkinder.storage.memory_storage import MemoryStorage


class Apple(StorageItem):
    type = "apple"

    uuid: UUID
    color: str
    weight: float

    @property
    def id(self) -> UUID:
        return self.uuid


@pytest.fixture()
def storage() -> MemoryStorage:
    return MemoryStorage()


class TestGet:
    def test_returns_item_if_found(self, storage: MemoryStorage) -> None:
        storage._data[Apple.type] = {}
        item = Apple(uuid=uuid4(), color="red", weight=0.2)
        storage._data[Apple.type][item.id] = item

        found_item = storage.get(Apple, item.id)

        assert item.id == found_item.id

    def test_raises_if_item_not_found(self, storage: MemoryStorage) -> None:
        with pytest.raises(ItemNotFoundInStorageError):
            storage.get(Apple, uuid4())


class TestSave:
    def test_saves_new_item(self, storage: MemoryStorage) -> None:
        item = Apple(uuid=uuid4(), color="red", weight=0.2)
        assert not storage._data

        storage.save(item)

        assert storage._data
        assert Apple.type in storage._data
        assert item.id in storage._data[Apple.type]
        saved_item = storage._data[Apple.type][item.id]
        assert item.id == saved_item.id

    def test_overwrites_existing_item(self, storage: MemoryStorage) -> None:
        item = Apple(uuid=uuid4(), color="red", weight=0.2)
        assert not storage._data

        storage.save(item)

        another_item = Apple(uuid=item.id, color="green", weight=0.3)
        storage.save(another_item)

        found_item = storage.get(Apple, item.id)
        assert another_item.id == found_item.id
        assert another_item.color == found_item.color
        assert another_item.weight == found_item.weight

    def test_raises_if_restricted_to_overwrite_existing_item(
        self, storage: MemoryStorage
    ) -> None:
        item = Apple(uuid=uuid4(), color="red", weight=0.2)
        assert not storage._data

        storage.save(item)

        another_item = Apple(uuid=item.id, color="green", weight=0.3)
        with pytest.raises(ItemAlreadyExistsInStorageError):
            storage.save(another_item, overwrite=False)

        found_item = storage.get(Apple, item.id)
        assert found_item.id == item.id
        assert found_item.color == item.color
        assert found_item.weight == item.weight


class TestFind:
    def test_finds_nothing(self, storage: MemoryStorage) -> None:
        found = storage.find(Apple, lambda _: True)
        assert isinstance(found, list)
        assert not found

    def test_returns_only_suitable(self, storage: MemoryStorage) -> None:
        storage.save(Apple(uuid=uuid4(), color="red", weight=0.2))
        storage.save(Apple(uuid=uuid4(), color="red", weight=0.3))
        storage.save(Apple(uuid=uuid4(), color="green", weight=0.4))

        red_apples = storage.find(Apple, lambda apple: apple.color == "red")
        assert len(red_apples) == 2
        # without duplicates
        assert len(set(apple.uuid for apple in red_apples)) == 2
        assert all(apple.color == "red" for apple in red_apples)
