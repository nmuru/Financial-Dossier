"""Minimal deterministic financial phase intelligence.

The smoke-test version answers one question before each financial phase:
what company/source is being analyzed, what period is covered, and what financial
data concepts are available. It deliberately avoids software-repository concepts.
"""
from __future__ import annotations

from .repository_intelligence import RepositoryIntelligence, collect_repository_intelligence
from .financial_intelligence import collect_financial_intelligence


def build_phase_intelligence(intelligence: RepositoryIntelligence, phase: str, repository=None) -> str:
    years = intelligence.fiscal_years
    if years:
        year_text = f"{years[0]} through {years[-1]} ({len(years)} fiscal years)"
    else:
        year_text = "no annual fiscal-year coverage detected"

    lines = [
        f"PHASE-SPECIFIC DETERMINISTIC FINANCIAL INTELLIGENCE: {phase}",
        "",
        f"Company: {intelligence.entity_name}",
        f"SEC CIK: {intelligence.cik or 'not supplied'}",
        f"Source: SEC Company Facts JSON (companyfacts.json)",
        f"Annual 10-K coverage: {year_text}",
        f"Latest fiscal year detected: {intelligence.latest_fiscal_year or 'not detected'}",
        f"Available XBRL taxonomies: {', '.join(intelligence.fact_taxonomies) or 'none detected'}",
        f"Available financial concepts: {intelligence.fact_count}",
        "JSON resource structure:",
        f"- {intelligence.json_structure.get('facts_shape', '/facts/<taxonomy>/<concept>/units/<unit>/[observations]') if intelligence.json_structure else '/facts/<taxonomy>/<concept>/units/<unit>/[observations]'}",
        "- Structured JSON evidence should be retrieved through bounded JSON tools; the full resource is not loaded into agent context.",
        "",
        "Annual reporting periods:",
    ]

    if intelligence.annual_periods:
        for period in intelligence.annual_periods[-10:]:
            lines.append(
                f"- FY{period['fiscal_year']}, period end {period['period_end']}, "
                f"forms: {', '.join(period['forms'])}"
            )
    else:
        lines.append("- none detected")

    lines.extend(["", "Representative available financial concepts:"])
    if intelligence.concept_names:
        lines.extend(f"- {name}" for name in intelligence.concept_names[:80])
    else:
        lines.append("- none detected")

    lines.extend(
        [
            "",
            "Smoke-test purpose:",
            f"- Establish preliminary financial evidence for the {phase} phase before semantic research and agent analysis.",
            "- Do not infer financial conclusions merely from concept availability.",
        ]
    )
    if phase == "revenue-earnings-engine" and repository is not None:
        financial_evidence = collect_financial_intelligence(repository)
        if financial_evidence:
            lines.extend(["", financial_evidence])

    return "\n".join(lines)


def collect_phase_intelligence(
    repository,
    phase: str,
    intelligence: RepositoryIntelligence | None = None,
) -> tuple[RepositoryIntelligence, str]:
    intelligence = intelligence or collect_repository_intelligence(repository)
    return intelligence, build_phase_intelligence(intelligence, phase)
