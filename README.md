# Python Classes Patterns

A side-by-side comparison of how to model domain classes in Python. Each pattern is implemented with five approaches:

- plain Python classes
- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- [`attrs`](https://www.attrs.org/)
- [`cattrs`](https://catt.rs/)
- [`pydantic`](https://docs.pydantic.dev/) (v2)

The focus is on **complex class structures**: nested value objects, aggregates made of collections of other objects, inheritance hierarchies and polymorphic (`Union`) fields. The repo also shows how much each library does to **cast primitive data** (dicts, lists, strings, numbers from JSON or a database) into those nested objects and back. Plain Python gives you none of this: type hints are not enforced, and nested dicts are never turned into objects automatically.

Every implementation has a unit test suite that pins down how it behaves. The patterns come from Domain-Driven Design (DDD), such as value objects and aggregates, but the findings apply to any nested data model.

## Casting nested structures at a glance

The same nested `Building` payload, loaded with each library's `from_primitives()`:

| | dataclasses | attrs | cattrs | pydantic |
| --- | --- | --- | --- | --- |
| **dict → nested objects** | Manual, level by level | Manual, level by level | `cattr.structure(data, Building)` | `Building(**data)` |
| **Casts primitives from annotations** (`"1"` → `1` for an `int` field) | No, `"1"` is kept as a `str` | No, only validators can reject it | Yes | Yes |
| **list → `frozenset[Model]`** | Manual | Manual | Automatic | Automatic |
| **Validates constraints while casting** | Only in `__post_init__` | Only with validators | Only with attrs validators | Yes (`conint`, `constr`, …) |
| **objects → primitives** | `asdict()` | `attrs.asdict()` | `cattr.unstructure()` | `model_dump(mode="json")` |
| **`Union` field → correct class** | Manual dispatch on a tag | Manual dispatch on a tag | Automatic if members have unique fields, otherwise a structure hook | Automatic (smart mode) if members have different fields, otherwise a tag or a discriminated union |

In short, dataclasses and attrs describe the *shape* of the classes but leave the conversion from raw data to you. cattrs adds conversion on top of attrs classes. pydantic combines conversion and validation in the class itself.

## Patterns

| Pattern | What it explores | native | dataclasses | attrs | cattrs | pydantic |
| --- | --- | :---: | :---: | :---: | :---: | :---: |
| **ID value object** | Immutable, validated, hashable ID with a `nanoid` generator | ✅ | ✅ | ✅ | – | ✅ |
| **Default values** | Mixing required and defaulted fields across a class hierarchy, and validating defaults | – | ✅ | ✅ | – | ✅ |
| **Inheritance** | Single and multiple inheritance of validated, immutable "tech spec" classes | – | ✅ | ✅ | ✅ | ✅ |
| **Composition** ⭐ | A nested aggregate (`Building` → `Level` → `Unit`) with serialization round-trips | – | ✅ | ✅ | ✅ | ✅ |
| **Union types casting** ⭐ | Serializing and deserializing a field typed as `Union[A, B, C]` to the right concrete class | – | ✅ | ✅ | ✅ | ✅ |

⭐ The patterns that deal most directly with nested structures and casting.

### ID value object

A [value object](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/implement-value-objects) that wraps a string ID. Requirements checked by the tests:

- `value` must be a `str` between 1 and 36 characters.
- Instances are immutable: assigning or deleting `value` raises.
- Equality and hashing are based on `value`.
- `ID.generate(size=...)` creates a new random ID using `nanoid`.
- `to_primitives()` returns `{"value": "..."}`.

### Default values

A `Base` class with a defaulted field `b` (which must be `> 0`) and a `Child` that adds more fields. It tests two things. First, Python forbids a field without a default after one with a default, so the hierarchy has to work around that. Second, it checks whether an invalid default (`b = 0`) is caught.

### Inheritance

Fiber-optic equipment specs built from small value objects:

- `Attenuation` (float, `> 0`) and `NumberOfFilaments` (int, `> 0`)
- `AttenuationTechSpec` and `NumberOfFilamentsTechSpec` as base specs
- `ConnectorTechSpec` (single inheritance) and `CableTechSpec` (multiple inheritance, where the library allows it)

### Composition

An aggregate of nested immutable objects:

```
Building
├── label: Label
└── levels: frozenset[Level]
    ├── label, order, distance_to_lower_link, distance_to_upper_link
    └── units: frozenset[Unit]
        └── label, distance_to_distribution_board, distance_to_main_enclosure_one/two
```

The tests check that the aggregate can be built, converted with `to_primitives()` and rebuilt with `from_primitives()`. Pydantic has two variants. `composition_types.py` wraps each constrained type in a `NewType`, and `composition_strict_types.py` uses plain `Annotated[int, Field(gt=0)]` / `StringConstraints` aliases.

### Union types casting

A wrapper whose `value` is `Union[TypeX1, TypeX2, TypeX3]`, where the member types share field names. Serialized data includes a type tag (`"__type": "TypeA2"`, or a `type` literal for pydantic), and deserialization has to restore the correct concrete class.

## Conventions

All implementations follow the same conventions so they can be compared directly:

- **Immutability**: `frozen=True` (dataclasses, attrs), `model_config = ConfigDict(frozen=True)` (pydantic), or `__slots__` with overridden `__setattr__` and `__delattr__` (native).
- **Serialization**: `to_primitives()` returns plain dicts and lists. `from_primitives()` is a `classmethod` that rebuilds the object from them.
- **Validation**: runs at construction time, in `__post_init__` (dataclasses), `attrs.validators`, pydantic `Annotated` constraints, or `__init__` (native).

## Findings

The code comments and skipped or failing tests record what each approach can and cannot do. In summary:

### Native classes
- Full control, but immutability, equality, hashing and validation all have to be written by hand.

### dataclasses
- No built-in validation. Checks go in `__post_init__`.
- `Fields without default values cannot appear after fields with default values`. Workaround: use multiple inheritance so that the MRO places the non-default base first (`class Child(DefaultBase, Base)`).
- Supports multiple inheritance of frozen dataclasses (`CableTechSpec`).
- Nested objects need a hand-written `from_primitives()`. `asdict()` handles the other direction.

### attrs
- Declarative validators (`instance_of`, `gt`, custom ones) that also run on default values.
- Same field-ordering rule as dataclasses. Subclasses can only add defaulted fields.
- `@attrs.define` produces slotted classes, so multiple inheritance fails with `TypeError: multiple bases have instance lay-out conflict`. `CableTechSpec` is written as a flat class instead.
- An invalid default value object (for example `Attenuation(value=0)`) fails at import time, when the class is defined.

### cattrs
- `cattr.structure` and `cattr.unstructure` remove most of the nested (de)serialization boilerplate that attrs needs.
- Unions whose members each have a unique attribute are resolved automatically (`TypeA`).
- Unions whose members share the same attributes fail with `has no usable unique attributes`. They need a custom structure hook on a `cattr.Converter` that dispatches on the `__type` tag (`TypeB`). A custom unstructure hook adds the tag on the way out.

### pydantic (v2)
- The most concise: parsing, validation and nested model construction are built in, and multiple inheritance works. `Model.model_validate(data)` builds the whole nested aggregate, including `list` → `frozenset[Model]`.
- Coerces types in lax mode (the default): `"1"` → `1` and `1.0` → `1` for an `int` field, so the "reject float" tests are skipped. A float with a fractional part (`1.5`) and an `int` for a `str` field are rejected. Strict mode (`strict=True`) turns coercion off.
- Constraints are declared with `Annotated[int, Field(gt=0)]` or `StringConstraints` (v1's `ConstrainedInt`/`ConstrainedStr` classes were removed, and `conint`/`constr` are discouraged). Wrapping them in a `NewType` gives a named, callable type.
- Default values are **not** validated unless you opt in. `b: PositiveInt = 0` is accepted silently, so `default_values_inheritance.py` uses `Field(default=0, validate_default=True)`. A default that is itself a model (`IntValueVO(value=0)`) fails at import time.
- `ConfigDict(frozen=True)` blocks both assignment and `del`, raising `ValidationError`, and makes models hashable, so they can be stored in a `frozenset`.
- `model_dump()` keeps a `frozenset` of models as a `frozenset` of dicts and fails with `unhashable type: dict`. `model_dump(mode="json")` turns it into a list, so `to_primitives()` is a single call.
- Unions use "smart" mode: the member with the most valid fields wins, so `TypeA` gets the right class from the data alone. When members have the same fields (`TypeB1`/`TypeB2`), the data cannot tell them apart. You can dispatch on a tag by hand (`TypeB`) or use a discriminated union, with a `Literal` field on each member and `Field(discriminator="type")` (`TypeC`). Field names that start with an underscore (`__type`) are treated as private, so the tag is called `type`.

## Results

| | native | dataclasses | attrs | cattrs | pydantic v2 |
| --- | --- | --- | --- | --- | --- |
| **Patterns covered** | ID value object only | All | All | Inheritance, composition, unions | All |
| **Tests** | 13 passed | 38 passed | 38 passed | 26 passed | 76 passed, 3 skipped |
| **Type checks** | Manual | Manual (`__post_init__`) | `instance_of` validators | attrs validators | Built in. Lax by default (`"1"` → `1`, `1.0` → `1`). `strict=True` rejects both |
| **Constraints** (`> 0`, length) | Manual | Manual | Validators | attrs validators | `Field(gt=0)`, `StringConstraints` |
| **Default values validated** | – | Manual | Yes | Yes | Opt-in (`validate_default=True`) |
| **Immutability error** | `AttributeError` | `FrozenInstanceError` (`AttributeError`) | `FrozenInstanceError` (`AttributeError`) | `FrozenInstanceError` (`AttributeError`) | `ValidationError` (`ValueError`) |
| **Multiple inheritance** | – | Yes | No (slots) | No (slots) | Yes |
| **Casts primitives** | No | No | No | Yes | Yes |
| **dict → nested objects** | Manual | Manual | Manual | `cattr.structure()` | `model_validate()` |
| **nested objects → dict** | Manual | `asdict()` | `attrs.asdict()` | `cattr.unstructure()` | `model_dump(mode="json")` |
| **`Union` → correct class** | – | Manual tag dispatch | Manual tag dispatch | Automatic for unique fields, hook otherwise | Smart mode, or a discriminated union |

Test counts leave out the order-dependent composition `to_primitives()` test (see [Known issues](#known-issues)). The pydantic skips mark two deliberate differences. Lax mode accepts `1.0` for an `int` field (2 tests), and an invalid default value object fails at import time (1 test), just as it does in attrs.

## Choosing a library

For loading primitive data into nested structures and serializing it back, **pydantic v2 covers everything attrs + cattrs does in this repo, with less code**. It is a trade-off, though, not a strict upgrade.

**Where pydantic v2 wins**

- **One library instead of two.** Validation, casting and serialization live in the class. With attrs + cattrs, constraints go in attrs validators and conversion in a cattrs `Converter`.
- **Unions take less work.** Smart mode resolves `TypeA` from the data alone, and discriminated unions replace cattrs' hand-written structure hooks.
- **Nested aggregates are simpler.** `model_validate()` and `model_dump(mode="json")` replace hand-written `from_primitives()` / `to_primitives()` methods.
- **Error reports are better.** A single `ValidationError` lists every failing field with its path, for example `levels.0.units.1.label`.

**Where attrs + cattrs still wins**

- **The domain stays separate from serialization.** For DDD-style modeling, this is the strongest argument. attrs classes are plain domain objects, and cattrs converts them from the outside. You can have several converters (API, database, events) without touching the model. With pydantic, the domain class is also the serialization schema. That works well for DTOs and APIs, but it couples the domain to it.
- **Stricter types with no extra setup.** `instance_of(int)` rejects `1.0`. pydantic needs `strict=True` for that, which also turns off the coercion you want at the boundaries.
- **Default values are validated by default.** pydantic only validates them with `validate_default=True`.
- **Lighter objects.** attrs classes use slots and run no validation unless you add validators, while pydantic validates on every construction. Performance has not been benchmarked in this repo.
- **Familiar exceptions.** attrs raises `AttributeError` when you modify a frozen object, and `TypeError`/`ValueError` for invalid data. pydantic raises `ValidationError` for all of these.

**Recommendation**

- Use **pydantic v2 at the boundaries**: APIs, configuration, and parsing external JSON or database rows into nested structures.
- Keep **attrs (or dataclasses) for the domain core** if it should stay free of serialization concerns, and add cattrs only where conversion is needed.
- If you prefer a single tool and don't need that separation, **pydantic v2 alone** handles every pattern in this repo.

## Project structure

```
classes/
├── native/          # plain Python classes
├── _dataclasses/    # standard library dataclasses
├── _attrs/          # attrs
├── _cattr/          # attrs + cattrs (structure/unstructure)
└── _pydantic/       # pydantic v2
```

Each package holds one module per pattern (`id_vo.py`, `default_values*.py`, `inheritance*.py`, `composition*.py`, `union_types_casting.py`) and a `tests/` folder with matching `test_*.py` files.

The package folders have a leading underscore (`_attrs`, `_pydantic`, …) so they do not shadow the libraries they import.

## Getting started

### Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)

Locked dependencies (see `pyproject.toml` / `uv.lock`): `pydantic 2.13`, `attrs 21.4`, `cattrs 1.10`, `nanoid 2.0`.

### Install

```bash
uv sync
```

This creates a `.venv` with the locked dependencies and the `dev` group (`autopep8`).

### Run the tests

`classes/` is not a package, so run test discovery once per implementation from the repository root:

```bash
for pkg in native _dataclasses _attrs _cattr _pydantic; do
  uv run python -m unittest discover -s classes/$pkg -t .
done
```

Or run a single module:

```bash
uv run python -m unittest classes._attrs.tests.test_id_vo
```

## Known issues

Skipped tests document behavior where a library deliberately differs from the rest, such as pydantic accepting `1.0` for an `int` field.

- The composition `to_primitives()` tests convert a `frozenset` into a list and compare it with a list in a fixed order. They can fail intermittently depending on hash ordering.
- `classes/native/tests/` has no `__init__.py`, so `unittest discover` does not find it. Run it directly with `python -m unittest classes.native.tests.test_id_vo`.

## References

- [Implement value objects (Microsoft, DDD)](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/implement-value-objects)
- [attrs: slotted classes](https://www.attrs.org/en/stable/glossary.html)
- [Python data model: notes on using `__slots__`](https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots)
- [cattrs: unions](https://catt.rs/en/stable/unions.html)
- [pydantic: unions (smart mode and discriminated unions)](https://docs.pydantic.dev/latest/concepts/unions/)
- [pydantic: migration guide from v1 to v2](https://docs.pydantic.dev/latest/migration/)
