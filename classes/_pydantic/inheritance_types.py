from __future__ import annotations
from abc import ABC
from typing import Annotated, NewType

import pydantic


NumberOfFilaments = NewType(
    "NumberOfFilaments",
    Annotated[int, pydantic.Field(gt=0)]
)
Attenuation = NewType(
    "Attenuation",
    Annotated[float, pydantic.Field(gt=0)]
)


class TechSpec(pydantic.BaseModel, ABC):
    model_config = pydantic.ConfigDict(frozen=True)


class AttenuationTechSpec(TechSpec):
    attenuation_1310nm: Attenuation
    attenuation_1550nm: Attenuation

    @ classmethod
    def from_primitives(cls, primitives: dict) -> AttenuationTechSpec:
        return cls.model_validate(primitives)

    def to_primitives(self) -> dict:
        return self.model_dump()


class NumberOfFilamentsTechSpec(TechSpec):
    number_of_filaments: NumberOfFilaments


class ConnectorTechSpecType(AttenuationTechSpec):
    """ Connector Tech Spec class """


class CableTechSpecType(AttenuationTechSpec, NumberOfFilamentsTechSpec):
    """  Cables Tech Spec class """
