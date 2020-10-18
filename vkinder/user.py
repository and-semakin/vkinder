from dataclasses import dataclass
from typing import Any, MutableMapping


@dataclass
class User:
    id: str
    state: str
    data: MutableMapping[str, Any]
