from typing import Annotated, NewType

import pydantic

DistanceType = NewType(
    "Distance",
    Annotated[float, pydantic.Field(ge=0)]
)
LabelType = NewType(
    "Label",
    Annotated[str, pydantic.StringConstraints(min_length=1, max_length=16)]
)
OrderType = NewType(
    "Order",
    Annotated[int, pydantic.Field(gt=0)]
)


class UnitType(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    label: LabelType
    distance_to_distribution_board: DistanceType
    distance_to_main_enclosure_one: DistanceType
    distance_to_main_enclosure_two: DistanceType


class LevelType(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    label: LabelType
    order: OrderType
    distance_to_lower_link: DistanceType
    distance_to_upper_link: DistanceType
    units: frozenset[UnitType]


class BuildingTypes(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    label: LabelType
    levels: frozenset[LevelType]

    @classmethod
    def from_primitives(cls, primitives: dict):
        return cls.model_validate(primitives)

    def to_primitives(self) -> dict:
        """
        model_dump() keeps frozensets and fails with
        "unhashable type: dict", json mode turns them into lists
        """
        return self.model_dump(mode="json")
