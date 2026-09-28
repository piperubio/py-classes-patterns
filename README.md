# Python Classes Patterns

A side-by-side comparison of how to model domain classes in Python. Each pattern is implemented with five approaches:

- plain Python classes
- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- [`attrs`](https://www.attrs.org/)
- [`cattrs`](https://catt.rs/)
- [`pydantic`](https://docs.pydantic.dev/1.10/) (v1)

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
| **objects → primitives** | `asdict()` | `attrs.asdict()` | `cattr.unstructure()` | `.dict()`, but it fails on a `frozenset` of models |
| **`Union` field → correct class** | Manual dispatch on a tag | Manual dispatch on a tag | Automatic if members have unique fields, otherwise a structure hook | `smart_union` or a `Literal` tag field |

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

The tests check that the aggregate can be built, converted with `to_primitives()` and rebuilt with `from_primitives()`. Pydantic has two variants. `composition_types.py` uses `NewType` with `conint`/`confloat`/`constr`, and `composition_strict_types.py` uses `ConstrainedInt`/`ConstrainedFloat`/`ConstrainedStr` subclasses.

### Union types casting

A wrapper whose `value` is `Union[TypeX1, TypeX2, TypeX3]`, where the member types share field names. Serialized data includes a type tag (`"__type": "TypeA2"`, or a `type` literal for pydantic), and deserialization has to restore the correct concrete class.

## Conventions

All implementations follow the same conventions so they can be compared directly:

- **Immutability**: `frozen=True` (dataclasses, attrs), `Config.frozen = True` (pydantic), or `__slots__` with overridden `__setattr__` and `__delattr__` (native).
- **Serialization**: `to_primitives()` returns plain dicts and lists. `from_primitives()` is a `classmethod` that rebuilds the object from them.
- **Validation**: runs at construction time, in `__post_init__` (dataclasses), `attrs.validators`, pydantic constrained types, or `__init__` (native).

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

### pydantic (v1)
- The most concise: parsing, validation and nested model construction are built in, and multiple inheritance works.
- Coerces types by default. For example, a float is accepted for an `int` field, so the "reject float" tests are skipped.
- Default values are **not** validated unless `validate_all` is set. `b: IntValueInheritance = IntValueInheritance(0)` is accepted silently. A default that is itself a model (`IntValueVO(value=0)`) fails at import time.
- `Config.frozen` blocks assignment (with `TypeError`) but does **not** block `del instance.value`.
- `.dict()` fails on models that hold a `frozenset` of models (`unhashable type: dict`), so `to_primitives()` builds the dict by hand.
- Without `smart_union`, a `Union` field is coerced to the **first** member that validates. `TypeA` always becomes `TypeA1`. `Config.smart_union = True` (`TypeB`) or a `Literal` type field on each member (`TypeC`) fixes this. Field names that start with an underscore (`__type`) are treated as private, so the tag is called `type`.

## Project structure

```
classes/
├── native/          # plain Python classes
├── _dataclasses/    # standard library dataclasses
├── _attrs/          # attrs
├── _cattr/          # attrs + cattrs (structure/unstructure)
└── _pydantic/       # pydantic v1
```

Each package holds one module per pattern (`id_vo.py`, `default_values*.py`, `inheritance*.py`, `composition*.py`, `union_types_casting.py`) and a `tests/` folder with matching `test_*.py` files.

The package folders have a leading underscore (`_attrs`, `_pydantic`, …) so they do not shadow the libraries they import.

## Getting started

### Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)

Locked dependencies (see `pyproject.toml` / `uv.lock`): `pydantic 1.10`, `attrs 21.4`, `cattrs 1.10`, `nanoid 2.0`.

> The pydantic examples use the v1 API (`ConstrainedInt`, `Config`, `smart_union`, `.dict()`) and do not run on pydantic v2.

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

Some tests fail on purpose, because they document a limitation of the library they test, not a bug in this repository:

- `_pydantic` union casting (`TypeA`): pydantic v1 casts to the first union member.
- `_pydantic` ID value object: `del id.value` does not raise.
- `_pydantic` default values: an invalid default is not validated.

Other issues:

- The composition `to_primitives()` tests convert a `frozenset` into a list and compare it with a list in a fixed order. They can fail intermittently depending on hash ordering.
- `classes/native/tests/` has no `__init__.py`, so `unittest discover` does not find it. Run it directly with `python -m unittest classes.native.tests.test_id_vo`.

## References

- [Implement value objects (Microsoft, DDD)](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/implement-value-objects)
- [attrs: slotted classes](https://www.attrs.org/en/stable/glossary.html)
- [Python data model: notes on using `__slots__`](https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots)
- [cattrs: unions](https://catt.rs/en/stable/unions.html)
- [pydantic v1: smart union and discriminated unions](https://docs.pydantic.dev/1.10/usage/model_config/#smart-union)
