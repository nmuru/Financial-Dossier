"""Deterministic SEC Company Facts evidence extraction for the financial prototype."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

CONCEPT_GROUPS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "diluted_eps": ["EarningsPerShareDiluted"],
    "diluted_shares": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "assets": ["Assets", "AssetsCurrent"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "liabilities": ["Liabilities", "LiabilitiesCurrent"],
    "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
}

def _find(root: Path) -> Path | None:
    for p in root.rglob("companyfacts.json"):
        if p.is_file():
            return p
    return None

def _candidates(facts: dict[str, Any], name: str):
    for taxonomy, concepts in facts.get("facts", {}).items():
        payload = concepts.get(name) if isinstance(concepts, dict) else None
        if payload:
            yield f"{taxonomy}.{name}", payload

def _select(rows: list[dict[str, Any]], years: set[int]) -> list[dict[str, Any]]:
    filtered=[]
    for row in rows:
        if row.get("form") != "10-K" or row.get("fp") not in (None, "FY"):
            continue
        try: fy=int(row.get("fy"))
        except (TypeError,ValueError): continue
        if years and fy not in years: continue
        filtered.append(row)
    by_key={}
    for row in filtered:
        key=(row.get("fy"), row.get("frame") or row.get("end"))
        old=by_key.get(key)
        if old is None or str(row.get("filed","")) > str(old.get("filed","")):
            by_key[key]=row
    return sorted(by_key.values(), key=lambda r:(int(r.get("fy",0)), str(r.get("end",""))))

def collect_financial_intelligence(root: Path, years: int = 5) -> str:
    path=_find(root)
    if not path:
        return ""
    data=json.loads(path.read_text(encoding="utf-8", errors="replace"))
    facts=data.get("facts", {})
    end_year=None
    all_years=[]
    for concepts in facts.values():
        if not isinstance(concepts,dict): continue
        for payload in concepts.values():
            for rows in payload.get("units",{}).values():
                for row in rows if isinstance(rows,list) else []:
                    try: all_years.append(int(row.get("fy")))
                    except (TypeError,ValueError): pass
    if all_years: end_year=max(all_years)
    selected_years=set(range((end_year or 0)-years+1, (end_year or 0)+1)) if end_year else set()

    lines=[
        "FINANCIAL SOURCE INTELLIGENCE",
        f"- source: {path.relative_to(root).as_posix()}",
        f"- company: {data.get('entityName','unknown')}",
        f"- CIK: {data.get('cik','unknown')}",
        f"- taxonomies: {', '.join(data.get('facts',{}).keys())}",
        f"- fiscal-year range detected: {min(all_years) if all_years else 'unknown'}–{max(all_years) if all_years else 'unknown'}",
        f"- preferred annual window: {min(selected_years) if selected_years else 'unknown'}–{max(selected_years) if selected_years else 'unknown'}",
        "",
        "ANNUAL FACT EVIDENCE",
    ]
    for group,names in CONCEPT_GROUPS.items():
        found=False
        for name in names:
            for canonical,payload in _candidates(facts,name):
                rows=[]
                for unit, observations in payload.get("units",{}).items():
                    selected=_select(observations,selected_years)
                    if selected:
                        found=True
                        lines.append(f"\n{group}: {canonical} [{unit}]")
                        for row in selected:
                            lines.append("  - "+json.dumps({
                                "fy":row.get("fy"),"end":row.get("end"),"frame":row.get("frame"),
                                "form":row.get("form"),"filed":row.get("filed"),"value":row.get("val"),
                                "accn":row.get("accn")
                            },ensure_ascii=False))
        if not found:
            lines.append(f"\n{group}: no usable annual 10-K observation found in preferred window")
    lines += [
        "",
        "COLLECTOR RULES",
        "- Values above are source observations, not analyst conclusions.",
        "- Annual selection requires form=10-K and fp=FY or absent.",
        "- Duplicate frame/end observations prefer the latest filed observation.",
        "- Concept presence alone is not treated as evidence of a reported value.",
        "- Use targeted financial retrieval tools only for ambiguity, missing evidence, or a needed supporting fact.",
    ]
    return "\n".join(lines)
