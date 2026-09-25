"""Deterministic SEC financial-statement collection using EdgarTools.

This module deliberately contains no LLM logic and performs no financial
interpretation. It retrieves SEC-reported statements and exposes them in a
stable JSON-serializable structure for later agent consumption.
"""

from __future__ import annotations

import os
import json
import math
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


def _safe_scalar(value: Any) -> Any:
    value = _json_value(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _rows_from_dataframe(statement: Any, view: str) -> list[dict[str, Any]]:
    if statement is None:
        return []
    dataframe = statement.to_dataframe(view=view).reset_index(drop=True)
    rows = []
    for record in dataframe.to_dict(orient="records"):
        rows.append({str(key): _safe_scalar(value) for key, value in record.items()})
    return rows


def _find_column(columns: list[str], *needles: str) -> str | None:
    lowered = [(column, column.lower()) for column in columns]
    for needle in needles:
        for column, low in lowered:
            if needle.lower() in low:
                return column
    return None


def _normalize_period_label(row: dict[str, Any]) -> str | None:
    for key in ("Fiscal Year", "fiscal_year", "FiscalYear", "fy", "Year", "year"):
        value = row.get(key)
        if value is not None:
            return str(value)
    for key in ("Period", "period", "End", "end", "Date", "date"):
        value = row.get(key)
        if value is not None:
            return str(value)
    return None


def _extract_metric_series(statement: Any, view: str, periods: int) -> dict[str, Any]:
    """Convert EdgarTools statement output into compact metric-oriented series."""
    rows = _rows_from_dataframe(statement, view)
    if not rows:
        return {"available": False, "periods": [], "metrics": {}}

    columns = list(rows[0].keys())
    label_col = "label" if "label" in columns else _find_column(columns, "concept", "line item", "name", "description")
    metadata_columns = {
        label_col, "concept", "standard_concept", "level", "abstract",
        "parent_concept", "parent_abstract_concept", "dimension",
        "dimension_axis", "dimension_member", "dimension_member_label",
        "unit", "point_in_time",
    }
    period_columns = [column for column in columns if column not in metadata_columns]
    period_columns = period_columns[-max(1, min(periods, 5)):]
    metrics: dict[str, dict[str, Any]] = {}

    aliases = {
        "revenue": ("revenue", "revenues", "sales"),
        "cost_of_revenue": ("cost of revenue", "cost of goods", "cost of sales"),
        "gross_profit": ("gross profit",),
        "operating_income": ("operating income",),
        "net_income": ("net income", "net earnings"),
        "basic_eps": ("earnings per share", "basic"),
        "diluted_eps": ("earnings per share", "diluted"),
        "assets": ("assets",),
        "current_assets": ("current assets",),
        "liabilities": ("liabilities",),
        "current_liabilities": ("current liabilities",),
        "equity": ("stockholders equity", "shareholders equity", "total equity"),
        "cash": ("cash and cash equivalents", "cash equivalents"),
        "operating_cash_flow": ("operating activities", "net cash provided by operating"),
        "capital_expenditure": ("property plant", "capital expenditures", "payments to acquire property"),
        "long_term_debt": ("long-term debt",),
        "short_term_debt": ("short-term borrowings", "short term debt"),
    }

    for row in rows:
        label = str(row.get(label_col, "")).lower() if label_col else ""
        if not label:
            continue
        metric_name = next((name for name, needles in aliases.items() if any(needle in label for needle in needles)), None)
        if not metric_name:
            continue
        series = metrics.setdefault(metric_name, {})
        for period in period_columns:
            series[str(period)] = _safe_scalar(row.get(period))

    if not metrics:
        return {"available": True, "periods": period_columns, "metrics": {}, "rows": rows}

    return {"available": True, "periods": period_columns, "metrics": metrics}


def _derived_metrics(income: dict[str, Any], balance: dict[str, Any], cashflow: dict[str, Any]) -> dict[str, Any]:
    def aligned(name: str, source: dict[str, Any]) -> dict[str, Any]:
        return source.get("metrics", {}).get(name, {}) or {}

    revenue = aligned("revenue", income)
    gross = aligned("gross_profit", income)
    operating = aligned("operating_income", income)
    net = aligned("net_income", income)
    eps = aligned("diluted_eps", income)
    ocf = aligned("operating_cash_flow", cashflow)
    cash = aligned("cash", balance)
    ltd = aligned("long_term_debt", balance)
    std = aligned("short_term_debt", balance)
    metrics: dict[str, Any] = {}

    for label, series in (("gross_margin", gross), ("operating_margin", operating), ("net_margin", net)):
        numerator = series
        denominator = revenue
        result = {}
        for period, value in numerator.items():
            denom = denominator.get(period)
            if isinstance(value, (int, float)) and isinstance(denom, (int, float)) and denom:
                result[period] = value / denom
        metrics[label] = result

    net_debt = {}
    for period in set(cash) | set(ltd) | set(std):
        debt = sum(x for x in (ltd.get(period), std.get(period)) if isinstance(x, (int, float)))
        cash_value = cash.get(period)
        if isinstance(cash_value, (int, float)):
            net_debt[period] = debt - cash_value
    metrics["net_debt"] = net_debt

    def growth(series: dict[str, Any]) -> dict[str, Any]:
        vals = [(p, v) for p, v in series.items() if isinstance(v, (int, float))]
        out = {}
        for i in range(1, len(vals)):
            prior = vals[i-1][1]
            current = vals[i][1]
            if prior not in (0, None):
                out[vals[i][0]] = current / prior - 1
        return out

    metrics["revenue_growth"] = growth(revenue)
    metrics["net_income_growth"] = growth(net)
    metrics["eps_growth"] = growth(eps)
    metrics["operating_cash_flow_growth"] = growth(ocf)
    return metrics


def build_financial_intelligence(identifier: str, *, historical_periods: int = 5, view: str = "standard") -> str:
    """Build phase-ready, structured SEC financial intelligence using EdgarTools."""
    payload = collect_financial_statements(identifier, historical_periods=historical_periods, view=view)
    company = Company(identifier)
    financials = company.get_financials()
    income = _extract_metric_series(financials.income_statement(view=view), view, historical_periods)
    balance = _extract_metric_series(financials.balance_sheet(view=view), view, historical_periods)
    cashflow = _extract_metric_series(financials.cash_flow_statement(view=view), view, historical_periods)
    derived = _derived_metrics(income, balance, cashflow)
    payload["metrics"] = {
        "income_statement": income,
        "balance_sheet": balance,
        "cash_flow_statement": cashflow,
        "derived": derived,
    }
    payload["phase_data"] = {
        "revenue_earnings": {
            "income_statement": income,
            "derived": {key: derived[key] for key in (
                "gross_margin", "operating_margin", "net_margin",
                "revenue_growth", "net_income_growth", "eps_growth",
            ) if key in derived},
        },
        "financial_resilience": {
            "balance_sheet": balance,
            "cash_flow_statement": cashflow,
            "derived": {key: derived[key] for key in (
                "net_debt", "operating_cash_flow_growth",
            ) if key in derived},
        },
        "capital_cash_deployment": {
            "balance_sheet": balance,
            "cash_flow_statement": cashflow,
            "derived": {key: derived[key] for key in ("net_debt",) if key in derived},
        },
        "accounting_signals_anomalies": {
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow_statement": cashflow,
            "derived": derived,
        },
    }
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
