"""Bounded SEC Company Facts retrieval for financial analysis."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agents import function_tool


def _find_companyfacts(root: Path) -> Path | None:
    candidates = [
        p for p in root.rglob("*.json")
        if p.name.lower() == "companyfacts.json"
        and not any(part in {".git", "node_modules", ".venv", "venv"} for part in p.parts)
    ]
    return sorted(candidates)[0] if candidates else None


def _load(root: Path) -> tuple[Path, dict[str, Any]]:
    path = _find_companyfacts(root)
    if path is None:
        raise ValueError("No companyfacts.json resource was found in the financial workspace.")
    return path, json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _normalize_concept(concept: str) -> tuple[str | None, str]:
    raw = str(concept or "").strip()
    if not raw:
        return None, ""
    if "." in raw:
        taxonomy, name = raw.split(".", 1)
        return taxonomy.strip() or None, name.strip()
    return None, raw


def _concept_candidates(facts: dict[str, Any], concept: str) -> list[tuple[str, dict[str, Any]]]:
    taxonomy_hint, normalized = _normalize_concept(concept)
    if not normalized:
        return []
    result: list[tuple[str, dict[str, Any]]] = []
    for taxonomy, concepts in facts.get("facts", {}).items():
        if taxonomy_hint and taxonomy != taxonomy_hint:
            continue
        if not isinstance(concepts, dict):
            continue
        payload = concepts.get(normalized)
        if payload is not None:
            result.append((f"{taxonomy}.{normalized}", payload))
            continue
        lowered = normalized.lower()
        for name, candidate in concepts.items():
            if isinstance(name, str) and name.lower() == lowered:
                result.append((f"{taxonomy}.{name}", candidate))
                break
    return result


def _annual(observations: list[dict[str, Any]], years: set[int] | None, form: str, annual: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in observations:
        if not isinstance(row, dict) or row.get("form") != form:
            continue
        try:
            fy = int(row.get("fy"))
        except (TypeError, ValueError):
            continue
        if years and fy not in years:
            continue
        if annual and row.get("fp") not in (None, "FY"):
            continue
        rows.append(row)
    rows.sort(key=lambda row: (bool(row.get("frame")), str(row.get("filed", ""))), reverse=True)
    selected: dict[tuple[Any, Any], dict[str, Any]] = {}
    for row in rows:
        key = (row.get("fy"), row.get("frame") or row.get("end"))
        old = selected.get(key)
        if old is None or str(row.get("filed", "")) > str(old.get("filed", "")):
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
        """Return bounded annual SEC observations for bare or qualified XBRL concepts."""
        try:
            _, data = _load(root)
            facts = data.get("facts", {})
            requested_years = set(years or [])
            output: list[dict[str, Any]] = []
            for requested in concepts:
                candidates = _concept_candidates(facts, requested)
                if not candidates:
                    output.append({
                        "requested_concept": requested,
                        "status": "not_found",
                        "hint": "Use search_json to discover the exact SEC concept name before retrying.",
                    })
                    continue
                for canonical, payload in candidates:
                    for unit, observations in payload.get("units", {}).items():
                        if not isinstance(observations, list):
                            continue
                        selected = _annual(observations, requested_years or None, form, annual)
                        output.append({
                            "requested_concept": requested,
                            "concept": canonical,
                            "label": payload.get("label"),
                            "unit": unit,
                            "observations": selected,
                            "observation_count": len(selected),
                        })
            return json.dumps({"source": "companyfacts.json", "facts": output}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"source": "companyfacts.json", "error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False)

    @function_tool
    def query_financial_statement(
        statement: str,
        years: list[int] | None = None,
        form: str = "10-K",
        annual: bool = True,
    ) -> str:
        """Return a bounded set of commonly used annual concepts for one financial statement."""
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
        concepts = mappings.get(statement.strip().lower())
        if concepts is None:
            return json.dumps({"error": "unsupported_statement", "statement": statement, "supported": sorted(mappings)}, ensure_ascii=False)
        facts = json.loads(query_financial_facts(concepts, years, form, annual))
        facts["statement"] = statement
        return json.dumps(facts, ensure_ascii=False)

    return [query_financial_facts, query_financial_statement]
