"""Deterministic SEC financial-statement collection using EdgarTools.

This module deliberately contains no LLM logic and performs no financial
interpretation. It retrieves SEC-reported statements and exposes them in a
stable JSON-serializable structure for later agent consumption.
"""

from __future__ import annotations

import os
import json
from typing import Any

from edgar import Company, set_identity


class EdgarFinancialsError(RuntimeError):
    """Raised when deterministic SEC financial collection cannot be completed."""


def _configure_identity() -> None:
    identity = os.getenv("EDGAR_IDENTITY", "").strip()
    if not identity:
        raise EdgarFinancialsError(
            "EDGAR_IDENTITY is required for SEC access. "
            "Set it to your name and email, for example 'Jane Doe jane@example.com'."
        )
    set_identity(identity)


def _json_value(value: Any) -> Any:
    """Convert common pandas/EdgarTools scalar values to JSON-safe values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        try:
            return _json_value(value.item())
        except Exception:
            pass
    return str(value)


def _statement_records(statement: Any, view: str = "standard") -> dict[str, Any]:
    if statement is None:
        return {"available": False, "rows": [], "columns": []}

    dataframe = statement.to_dataframe(view=view)
    dataframe = dataframe.reset_index(drop=True)

    rows: list[dict[str, Any]] = []
    for record in dataframe.to_dict(orient="records"):
        rows.append({str(key): _json_value(value) for key, value in record.items()})

    return {
        "available": True,
        "view": view,
        "columns": [str(column) for column in dataframe.columns],
        "rows": rows,
    }


def _select_recent_annual_rows(statement_data: dict[str, Any], periods: int) -> dict[str, Any]:
    """Return a bounded deterministic statement payload."""
    rows = statement_data.get("rows") or []
    max_rows = max(1, min(int(periods), 5)) * 80
    if len(rows) <= max_rows:
        return statement_data
    return {**statement_data, "rows": rows[-max_rows:], "truncated": True}

def build_financial_intelligence(identifier: str, *, historical_periods: int = 5, view: str = "standard") -> str:
    """Build compact upfront financial intelligence for downstream phase agents."""
    payload = collect_financial_statements(
        identifier,
        historical_periods=historical_periods,
        view=view,
    )
    return json.dumps(payload, ensure_ascii=False)

def collect_financial_statements(
    identifier: str,
    *,
    view: str = "standard",
    historical_periods: int = 5,
) -> dict[str, Any]:
    """Collect annual income, balance-sheet, and cash-flow statements.

    get_financials() is used for the normal annual statement set.
    get_facts() is additionally used when more historical annual periods are
    requested. No ratios or conclusions are calculated here.
    """
    identifier = identifier.strip()
    if not identifier:
        raise EdgarFinancialsError("A company ticker or CIK is required.")

    if view not in {"summary", "standard", "detailed"}:
        raise EdgarFinancialsError("view must be summary, standard, or detailed.")

    historical_periods = max(1, min(int(historical_periods), 20))

    _configure_identity()

    try:
        company = Company(identifier)
        financials = company.get_financials()

        result: dict[str, Any] = {
            "source": "SEC via EdgarTools",
            "identifier": identifier,
            "company": {
                "name": getattr(company, "name", None),
                "cik": _json_value(getattr(company, "cik", None)),
                "ticker": _json_value(getattr(company, "ticker", None)),
            },
            "annual": {
                "income_statement": _select_recent_annual_rows(
                    _statement_records(financials.income_statement(view=view), view),
                    historical_periods,
                ),
                "balance_sheet": _select_recent_annual_rows(
                    _statement_records(financials.balance_sheet(view=view), view),
                    historical_periods,
                ),
                "cash_flow_statement": _select_recent_annual_rows(
                    _statement_records(financials.cash_flow_statement(view=view), view),
                    historical_periods,
                ),
            },
            "historical": None,
        }

        if historical_periods > 3:
            facts = company.get_facts()
            result["historical"] = {
                "periods_requested": historical_periods,
                "income_statement": _statement_records(
                    facts.income_statement(periods=historical_periods, annual=True),
                    view,
                ),
                "balance_sheet": _statement_records(
                    facts.balance_sheet(periods=historical_periods, annual=True),
                    view,
                ),
                "cash_flow_statement": _statement_records(
                    facts.cash_flow(periods=historical_periods, annual=True),
                    view,
                ),
            }

        return result
    except EdgarFinancialsError:
        raise
    except Exception as exc:
        raise EdgarFinancialsError(
            f"EdgarTools financial collection failed for '{identifier}': "
            f"{type(exc).__name__}: {exc}"
        ) from exc
