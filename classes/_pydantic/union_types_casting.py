from typing import Annotated, Union, Literal

import pydantic


class TypeA1(pydantic.BaseModel):
    a1: int


class TypeA2(pydantic.BaseModel):
    a1: float
    a2: bool


class TypeA3(pydantic.BaseModel):
    a1: float
    a2: bool
    a3: int


class TypeA(pydantic.BaseModel):
    """
    pydantic v2 validates unions in "smart" mode by default:
    the member with the most valid fields set wins,
    so the right type is chosen without a tag
    (pydantic v1 cast always to TypeA1)
    """
    value: Union[TypeA1, TypeA2, TypeA3]

    @classmethod
    def from_primitives(cls, primitives: dict):
        return cls.model_validate(primitives)

    def to_primitives(self):
        return {
            "__type": self.value.__class__.__name__,
            **self.value.model_dump()
        }


class TypeB1(pydantic.BaseModel):
    b1: float
    b2: bool


class TypeB2(pydantic.BaseModel):
    b1: float
    b2: int


class TypeB3(pydantic.BaseModel):
    b1: float
    b2: bool
    b3: int


class TypeB(pydantic.BaseModel):
    """
    TypeB1 and TypeB2 have the same fields, smart mode cannot tell them
    apart from the data, so the "__type" tag is used to pick the class
    """
    value: Union[TypeB1, TypeB2, TypeB3]

    @classmethod
    def from_primitives(cls, primitives: dict):
        if primitives["value"]["__type"] == "TypeB1":
            return TypeB(value=TypeB1(**primitives["value"]))
        elif primitives["value"]["__type"] == "TypeB2":
            return TypeB(
                value=TypeB2(
                    **primitives["value"]
                )
            )
        elif primitives["value"]["__type"] == "TypeB3":
            return TypeB(
                value=TypeB3(
                    **primitives["value"]
                )
            )
        else:
            raise ValueError(f"Unknown type {primitives['value']['__type']}")


"""
Type field cannot be __type,
pydantic treats fields starting with an underscore as private attributes
"""


class TypeC1(pydantic.BaseModel):
    type: Literal["TypeC1"] = "TypeC1"
    c1: str


class TypeC2(pydantic.BaseModel):
    type: Literal["TypeC2"] = "TypeC2"
    c1: int
    c2: str


class TypeC3(pydantic.BaseModel):
    type: Literal["TypeC3"] = "TypeC3"
    c1: int
    c2: str
    c3: bool


TypeC = Annotated[
    Union[TypeC1, TypeC2, TypeC3],
    pydantic.Field(discriminator="type")
]


class TypeCBase(pydantic.BaseModel):
    value: TypeC

    @classmethod
    def from_primitives(cls, primitives: dict):
        return cls.model_validate(primitives)
