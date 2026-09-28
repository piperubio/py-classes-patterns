import pydantic


class IntValueVO(pydantic.BaseModel):
    value: int = pydantic.Field(gt=0)


class BaseVO(pydantic.BaseModel):
    a: int
    """
    b: IntValueVO = IntValueVO(value=0)
    raise ERROR pydantic.ValidationError: 1 validation error for IntValueVO
    """
    b: IntValueVO = IntValueVO(value=1)


class ChildVO(BaseVO):
    c: int
    d: int = 2
