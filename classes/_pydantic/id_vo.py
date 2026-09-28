from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from nanoid import generate
from nanoid.resources import alphabet, size


class ID(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: Annotated[str, StringConstraints(min_length=1, max_length=36)]

    @staticmethod
    def generate(alphabet=alphabet, size=size) -> ID:
        return ID(value=generate(alphabet=alphabet, size=size))

    def to_primitives(self) -> dict[str, str]:
        return self.model_dump()
