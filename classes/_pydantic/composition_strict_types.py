from typing import Annotated

import pydantic

"""
pydantic v2 removed ConstrainedFloat, ConstrainedStr and ConstrainedInt,
constraints are declared with Annotated instead
"""

DistanceStrictType = Annotated[float, pydantic.Field(ge=0)]
LabelStrictType = Annotated[
    str,
    pydantic.StringConstraints(min_length=1, max_length=16)
]
OrderStrictType = Annotated[int, pydantic.Field(gt=0)]


class UnitStrictType(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    label: LabelStrictType
    distance_to_distribution_board: DistanceStrictType
    distance_to_main_enclosure_one: DistanceStrictType
    distance_to_main_enclosure_two: DistanceStrictType


class LevelStrictType(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    label: LabelStrictType
    order: OrderStrictType
    distance_to_lower_link: DistanceStrictType
    distance_to_upper_link: DistanceStrictType
    units: frozenset[UnitStrictType]


class BuildingStrictType(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    label: LabelStrictType
    levels: frozenset[LevelStrictType]

    @classmethod
    def from_primitives(cls, primitives: dict):
        return cls.model_validate(primitives)

    def to_primitives(self) -> dict:
        """
        model_dump() keeps frozensets and fails with
        "unhashable type: dict", json mode turns them into lists
        """
        return self.model_dump(mode="json")
