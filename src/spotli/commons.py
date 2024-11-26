from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Type, TypeVar, get_args, get_origin

TOKEN_PATH = Path.home() / ".spotli" / "tokens.json"

T = TypeVar('T')

class FromDictMixin:
    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        """Creates class instance unpacking given dictionary"""

        field_names = {f.name for f in fields(cls)}
        init_kwargs = {}

        for key, value in data.items():
            if key in field_names:
                field = next(f for f in fields(cls) if f.name == key)
                field_type = field.type

                # Handle nested dataclass
                if is_dataclass(field_type) and isinstance(value, dict):
                    init_kwargs[key] = field_type.from_dict(value)

                # Handle list of dataclasses
                elif get_origin(field_type) is list:
                    inner_type = get_args(field_type)[0]
                    if is_dataclass(inner_type) and isinstance(value, list):
                        init_kwargs[key] = [inner_type.from_dict(item) for item in value]
                    else:
                        init_kwargs[key] = value  # List of primitives

                # Handle other fields (primitives or non-dataclass objects)
                else:
                    init_kwargs[key] = value

        return cls(**init_kwargs)