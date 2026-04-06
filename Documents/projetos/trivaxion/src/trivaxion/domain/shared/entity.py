from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from trivaxion.domain.shared.value_objects import EntityId


@dataclass
class Entity(ABC):
    id: EntityId = field(default_factory=EntityId.generate)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
