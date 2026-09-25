from pathlib import Path
import json

from .structured_json_tools import _resolve, _preview_structure


def test_json_pointer_resolves_nested_taxonomy():
    value = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [1, 2]}}}}}
    assert _resolve(value, "/facts/us-gaap/Revenues/units/USD") == [1, 2]


def test_structure_inspection_is_bounded():
    value = {"a": 1, "b": 2, "c": 3}
    result = _preview_structure(value, 2)
    assert result["key_count"] == 3
    assert result["truncated"] is True
