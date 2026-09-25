"""Financial-specific bounded retrieval over SEC Company Facts.

These tools are intentionally thin. They select and normalize reported facts;
they do not calculate financial conclusions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agents import function_tool


def _find_companyfacts(root: Path) -> Path | None:
    candidates = []
    for path in root.rglob("*.json"):
        if any(part in {".git", "node_modules", ".venv", "venv"} for part in path.parts):
            continue
        if path.name.lower() == "companyfacts.json":
            candidates.append(path)
    return candidates[0] if candidates else None


def _load(root: Path) -> tuple[Path, dict[str, Any]]:
    path = _find_companyfacts(root)
    if path is None:
        raise ValueError("No companyfacts.json resource was found in the repository.")
    return path, json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _concept_candidates(facts: dict[str, Any], concept: str) -> list[tuple[str, dict[str, Any]]]:
    normalized = concept.split(".", 1)[-1]
    result = []
    for taxonomy, concepts in facts.get("facts", {}).items():
        if not isinstance(concepts, dict):
            continue
        for name, payload in concepts.items():
            if name == normalized or f"{taxonomy}.{name}" == concept or name.lower() == normalized.lower():
                result.append((f"{taxonomy}.{name}", payload))
    return result


def _annual(observations: list[dict[str, Any]], years: set[int] | None, form: str, annual: bool) -> list[dict[str, Any]]:
    rows = []
    for row in observations:
        if not isinstance(row, dict) or row.get("form") != form:
            continue
        fy = row.get("fy")
        try:
            fy_int = int(fy) if fy is not None else None
        except (TypeError, ValueError):
            fy_int = None
        if years and fy_int not in years:
            continue
        if annual and row.get("fp") not in (None, "FY"):
            continue
        rows.append(row)
    # Prefer framed calendar-year annual observations. Then latest filed duplicate.
    rows.sort(key=lambda row: (bool(row.get("frame")), str(row.get("filed", ""))), reverse=True)
    selected: dict[tuple[Any, Any], dict[str, Any]] = {}
    for row in rows:
        key = (row.get("fy"), row.get("frame") or row.get("end"))
        if key not in selected or str(row.get("filed", "")) > str(selected[key].get("filed", "")):
            selected[key] = row
    return sorted(selected.values(), key=lambda row: (str(row.get("fy", "")), str(row.get("end", ""))))


def build_financial_tools(root: Path):
    @function_tool
    def query_financial_facts(
        concepts: list[str],
        years: list[int] | None = None,
        form: str = "10-K",
        annual: bool = True,
    ) -> str:
        """Return normalized reported observations for requested concepts and years."""
        try:
            _, data = _load(root)
            facts = data.get("facts", {})
            requested_years = set(years or [])
            output = []
            for concept in concepts:
                candidates = _concept_candidates(facts, concept)
                if not candidates:
                    output.append({"concept": concept, "status": "not_found"})
                    continue
                for canonical, payload in candidates:
                    units = payload.get("units", {})
                    for unit, observations in units.items():
                        if not isinstance(observations, list):
                            continue
                        selected = _annual(observations, requested_years or None, form, annual)
                        output.append({
                            "concept": canonical,
                            "label": payload.get("label"),
                            "unit": unit,
                            "observations": selected,
                        })
            return json.dumps({"source": "companyfacts.json", "facts": output}, ensure_ascii=False)
        except Exception as exc:
            return str(exc)

    @function_tool
    def query_financial_statement(
        statement: str,
        years: list[int] | None = None,
        form: str = "10-K",
        annual: bool = True,
    ) -> str:
        """Return a bounded coherent financial statement block assembled from common SEC concepts."""
        mappings = {
            "income_statement": [
                "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "GrossProfit", "CostOfRevenue", "OperatingIncomeLoss", "NetIncomeLoss",
                "EarningsPerShareDiluted", "WeightedAverageNumberOfDilutedSharesOutstanding",
            ],
            "balance_sheet": [
                "Assets", "AssetsCurrent", "CashAndCashEquivalentsAtCarryingValue",
                "AccountsReceivableNetCurrent", "InventoryNet", "Liabilities",
                "LiabilitiesCurrent", "LongTermDebtNoncurrent", "StockholdersEquity",
            ],
            "cash_flow": [
                "NetCashProvidedByUsedInOperatingActivities",
                "PaymentsToAcquirePropertyPlantAndEquipment",
                "NetCashProvidedByUsedInInvestingActivities",
                "NetCashProvidedByUsedInFinancingActivities",
                "CashAndCashEquivalentsPeriodIncreaseDecrease",
            ],
        }
        concepts = mappings.get(statement.lower())
        if not concepts:
            return f"Unsupported statement '{statement}'. Supported: {', '.join(mappings)}"
        # Reuse the exact fact-selection implementation without calculating anything.
        try:
            _, data = _load(root)
            facts = data.get("facts", {})
            requested_years = set(years or [])
            output = []
            for concept in concepts:
                candidates = _concept_candidates(facts, concept)
                for canonical, payload in candidates:
                    for unit, observations in payload.get("units", {}).items():
                        if isinstance(observations, list):
                            selected = _annual(observations, requested_years or None, form, annual)
                            if selected:
                                output.append({"concept": canonical, "unit": unit, "observations": selected})
            return json.dumps({"statement": statement, "source": "companyfacts.json", "facts": output}, ensure_ascii=False)
        except Exception as exc:
            return str(exc)

    return [query_financial_facts, query_financial_statement]
