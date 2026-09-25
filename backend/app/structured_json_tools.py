"""Bounded structured-JSON tools used by agents.

The implementation is generic: JSON Pointer navigation, structure inspection,
search, bounded value reads, and simple filtering/projection. No financial
semantics live here.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agents import function_tool

DEFAULT_VALUE_LIMIT_CHARS = 200_000  # roughly 50k tokens for JSON-heavy content
MAX_SEARCH_RESULTS = 200
MAX_QUERY_RESULTS = 500


def _safe_json_path(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError("Path escapes repository root.")
    return candidate


def _load_json(root: Path, path: str) -> Any:
    target = _safe_json_path(root, path)
    if not target.is_file():
        raise ValueError(f"JSON resource not found: {path}")
    try:
        return json.loads(target.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON resource: {path}: {exc}") from exc


def _decode_pointer(pointer: str) -> list[str]:
    if pointer in ("", None):
        return []
    if not pointer.startswith("/"):
        raise ValueError(
            f"Invalid JSON Pointer '{pointer}'. Use standard JSON Pointer syntax, "
            "for example /facts/us-gaap/Revenues."
        )
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def _resolve(value: Any, pointer: str) -> Any:
    current = value
    traversed = ""
    for token in _decode_pointer(pointer):
        parent_pointer = traversed or "/"
        if isinstance(current, dict):
            if token not in current:
                available = list(current.keys())[:40]
                raise KeyError(
                    f"JSON Pointer not found: {pointer}. "
                    f"Traversal failed at {parent_pointer}. Available keys: {available}"
                )
            current = current[token]
        elif isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError) as exc:
                raise KeyError(
                    f"JSON Pointer not found: {pointer}. "
                    f"Traversal failed at {parent_pointer}; array index '{token}' is invalid."
                ) from exc
        else:
            raise KeyError(
                f"JSON Pointer not found: {pointer}. "
                f"Traversal failed at {parent_pointer}; current value is {type(current).__name__}."
            )
        traversed += "/" + token
    return current


def _preview_structure(value: Any, max_items: int) -> dict[str, Any]:
    if isinstance(value, dict):
        keys = list(value.keys())
        return {
            "type": "object",
            "key_count": len(keys),
            "keys": keys[:max_items],
            "truncated": len(keys) > max_items,
        }
    if isinstance(value, list):
        item_shapes = []
        seen = set()
        for item in value[: min(len(value), 10)]:
            shape = _shape(item)
            key = json.dumps(shape, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.add(key)
                item_shapes.append(shape)
        return {
            "type": "array",
            "length": len(value),
            "item_shapes": item_shapes,
            "truncated": len(value) > max_items,
        }
    return {"type": type(value).__name__, "value_preview": str(value)[:1000]}


def _shape(value: Any) -> Any:
    if isinstance(value, dict):
        return {"type": "object", "keys": list(value.keys())[:100]}
    if isinstance(value, list):
        return {"type": "array", "length": len(value), "sample_type": type(value[0]).__name__ if value else None}
    return {"type": type(value).__name__}


def _search(value: Any, query: str, pointer: str, matches: list[str], limit: int) -> None:
    if len(matches) >= limit:
        return
    needle = query.lower()
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}/{str(key).replace('~','~0').replace('/','~1')}"
            if needle in str(key).lower():
                matches.append(child_pointer)
                if len(matches) >= limit:
                    return
            _search(child, query, child_pointer, matches, limit)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _search(child, query, f"{pointer}/{index}", matches, limit)


def _truncate_serialized(value: Any, max_chars: int) -> tuple[str, bool]:
    serialized = json.dumps(value, ensure_ascii=False, indent=2)
    if len(serialized) <= max_chars:
        return serialized, False
    return serialized[:max_chars] + "\n[truncated]", True


def build_structured_json_tools(root: Path):
    @function_tool
    def inspect_json_structure(path: str, json_pointer: str = "", max_items: int = 50) -> str:
        """Inspect JSON structure without returning the full value. Paths use standard JSON Pointer."""
        try:
            value = _load_json(root, path)
            resolved = _resolve(value, json_pointer)
            result = {"path": json_pointer or "/", **_preview_structure(resolved, max(1, min(max_items, 500)))}
            return json.dumps(result, ensure_ascii=False)
        except Exception as exc:
            return str(exc)

    @function_tool
    def search_json(path: str, query: str, max_results: int = 50) -> str:
        """Search JSON keys recursively and return bounded JSON Pointer matches."""
        try:
            value = _load_json(root, path)
            limit = max(1, min(max_results, MAX_SEARCH_RESULTS))
            matches: list[str] = []
            _search(value, query, "", matches, limit)
            return json.dumps(
                {"query": query, "matches": matches, "count": len(matches), "truncated": len(matches) >= limit},
                ensure_ascii=False,
            )
        except Exception as exc:
            return str(exc)

    @function_tool
    def read_json_value(path: str, json_pointer: str = "", max_chars: int = DEFAULT_VALUE_LIMIT_CHARS) -> str:
        """Read a deliberately selected JSON value, allowing coherent blocks up to about 50k tokens."""
        try:
            value = _resolve(_load_json(root, path), json_pointer)
            serialized, truncated = _truncate_serialized(value, max(1000, min(max_chars, DEFAULT_VALUE_LIMIT_CHARS)))
            if truncated:
                return json.dumps(
                    {"path": json_pointer or "/", "message": "Value exceeds the bounded direct-read limit; inspect or query a narrower path.", "serialized_chars": len(json.dumps(value, ensure_ascii=False))},
                    ensure_ascii=False,
                )
            return serialized
        except Exception as exc:
            return str(exc)

    @function_tool
    def query_json(
        path: str,
        json_pointer: str = "",
        filters: dict[str, Any] | None = None,
        fields: list[str] | None = None,
        limit: int = 100,
    ) -> str:
        """Filter/projection over a JSON object or array using exact field matches."""
        try:
            value = _resolve(_load_json(root, path), json_pointer)
            if isinstance(value, dict):
                rows = list(value.values())
            elif isinstance(value, list):
                rows = value
            else:
                return json.dumps({"value": value}, ensure_ascii=False)

            filters = filters or {}
            result = []
            for row in rows:
                if filters and (not isinstance(row, dict) or any(row.get(k) != v for k, v in filters.items())):
                    continue
                if fields and isinstance(row, dict):
                    row = {field: row.get(field) for field in fields}
                result.append(row)
                if len(result) >= max(1, min(limit, MAX_QUERY_RESULTS)):
                    break
            return json.dumps(
                {"path": json_pointer or "/", "count": len(result), "items": result, "truncated": len(result) >= max(1, min(limit, MAX_QUERY_RESULTS))},
                ensure_ascii=False,
            )
        except Exception as exc:
            return str(exc)

    return [inspect_json_structure, search_json, read_json_value, query_json]
