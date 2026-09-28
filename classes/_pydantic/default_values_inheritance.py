from typing import Annotated

import pydantic

IntValueInheritance = Annotated[int, pydantic.Field(gt=0)]


class BaseInheritance(pydantic.BaseModel):
    a: int
    """
    b: IntValueInheritance = 0
    pydantic does not validate default values, so an invalid default is accepted
    """
    b: IntValueInheritance = pydantic.Field(default=0, validate_default=True)


class ChildInheritance(BaseInheritance):
    c: int
    d: int = 2
