from typing import Optional
from uuid import UUID

from vkinder.storage.base import StorageItem


class User(StorageItem):
    type = "user"

    vk_id: int
    state: str
    first_name: str
    last_name: str

    country_id: Optional[int]
    city_id: Optional[int]
    sex: Optional[int]
    age_from: Optional[int]
    age_to: Optional[int]
    current_search: Optional[UUID]
    current_search_item: Optional[int]

    @property
    def id(self) -> int:
        return self.vk_id


class Search(StorageItem):
    type = "search"

    uuid: UUID
    user_id: int
    datetime: str
    country_id: int
    city_id: int
    sex: int
    age_from: int
    age_to: int

    @property
    def id(self) -> UUID:
        return self.uuid


class Match(StorageItem):
    type = "match"

    uuid: UUID
    search_id: UUID
    vk_id: int
    first_name: str
    last_name: str
    seen: bool = False
    liked: bool = False

    @property
    def id(self) -> UUID:
        return self.uuid
