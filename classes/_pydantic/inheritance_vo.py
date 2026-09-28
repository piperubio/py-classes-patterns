from __future__ import annotations
from abc import ABC

import pydantic

"""
Pydantic raise error when VO has invalid default value,
the class definition fails when the module is imported:

    attenuation_1310nm: AttenuationVO = AttenuationVO(value=0)

pydantic.ValidationError: 1 validation error for AttenuationVO
value
  Input should be greater than 0 [type=greater_than, input_value=0, input_type=int]
"""


class NumberOfFilamentsVO(pydantic.BaseModel):
    value: int = pydantic.Field(gt=0)


class AttenuationVO(pydantic.BaseModel):
    value: float = pydantic.Field(gt=0)


class TechSpec(pydantic.BaseModel, ABC):
    model_config = pydantic.ConfigDict(frozen=True)


class AttenuationTechSpec(TechSpec):
    attenuation_1310nm: AttenuationVO = AttenuationVO(value=1)
    attenuation_1550nm: AttenuationVO

    @ classmethod
    def from_primitives(cls, primitives: dict) -> AttenuationTechSpec:
        return cls.model_validate(primitives)

    def to_primitives(self) -> dict:
        return self.model_dump()


class NumberOfFilamentsTechSpec(TechSpec):
    number_of_filaments: NumberOfFilamentsVO = NumberOfFilamentsVO(value=1)


class ConnectorTechSpecVO(AttenuationTechSpec):
    """ Connector Tech Spec class """


class CableTechSpecVO(AttenuationTechSpec, NumberOfFilamentsTechSpec):
    """  Cables Tech Spec class """
