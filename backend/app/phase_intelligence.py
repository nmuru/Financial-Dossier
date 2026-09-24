"""Phase-specific deterministic evidence packages.

Collectors aggregate programmatically obtainable repository facts. They deliberately expose
candidates, evidence and relationships rather than making architectural or design conclusions.
"""
from __future__ import annotations

from collections import Counter

from .repository_intelligence import RepositoryIntelligence, collect_repository_intelligence


def _append_items(lines: list[str], items, empty: str = "- none detected") -> None:
    rendered = list(items)
    if rendered:
        lines.extend(rendered)
    else:
        lines.append(empty)


def _topology(intelligence: RepositoryIntelligence, limit: int = 40) -> list[str]:
    counts = Counter(path.split("/", 1)[0] for path in intelligence.files)
    return [f"- {name}: {count} tracked files" for name, count in counts.most_common(limit)]


def _dependency_edges(intelligence: RepositoryIntelligence, limit: int = 160) -> list[str]:
    return [
        f"- {edge.source} -> {edge.target} (import: {edge.imported_as})"
        if edge.imported_as
        else f"- {edge.source} -> {edge.target}"
        for edge in intelligence.dependency_edges[:limit]
    ]


def _signal_files(intelligence: RepositoryIntelligence, signals: set[str], limit: int = 80) -> list[str]:
    patterns = {
        "context": ("context", "provider"),
        "adapter": ("adapter",),
        "repository": ("repository",),
        "factory": ("factory",),
        "observer": ("subscribe", "listener", "event", "observer"),
        "state": ("store", "context", "provider", "redux", "zustand"),
        "cache": ("cache", "revalidate"),
        "integration": (
            "client", "sdk", "api", "graphql", "stripe", "shopify", "supabase", "firebase",
            "openai", "github", "aws", "azure", "gcp",
        ),
        "validation": ("validate", "schema", "zod", "validator", "guard"),
        "error": ("error", "exception", "fallback", "retry"),
        "test": ("test", "spec", "fixture", "mock", "stub"),
    }
    selected: list[str] = []
    for item in intelligence.source_files:
        haystack = (
            item.path + " " + " ".join(item.imports) + " " + " ".join(item.exports)
            + " " + " ".join(sum(item.symbols.values(), []))
        ).lower()
        if any(any(token in haystack for token in patterns[name]) for name in signals if name in patterns):
            selected.append(item.path)
    return selected[:limit]


def _technology_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = []
    for evidence in intelligence.technology_evidence[:100]:
        location = f"{evidence.file}:{evidence.line}" if evidence.line else evidence.file
        detail = f"; {evidence.detail}" if evidence.detail else ""
        lines.append(f"- {evidence.value} [{evidence.confidence}] — {location}{detail}")
    return lines or ["- none detected"]


def _operation_symbols(intelligence: RepositoryIntelligence, limit: int = 120) -> list[str]:
    operation_words = (
        "create", "update", "delete", "remove", "get", "list", "search", "login", "logout",
        "register", "upload", "export", "analyze", "generate", "clone", "run", "render",
        "save", "load", "fetch", "submit", "checkout", "cart", "product", "order", "revalidate",
        "add", "set", "select", "filter", "sort", "handle", "process", "validate", "send",
    )
    lines: list[str] = []
    for item in intelligence.source_files:
        names = [
            name
            for names in item.symbols.values()
            for name in names
            if any(word in name.lower() for word in operation_words)
        ]
        if names:
            lines.append(f"- {item.path}: {', '.join(names[:30])}")
            if len(lines) >= limit:
                break
    return lines


def _symbol_inventory(intelligence: RepositoryIntelligence, limit: int = 140) -> list[str]:
    lines: list[str] = []
    for item in intelligence.source_files:
        rendered = [f"{kind}: {', '.join(names[:24])}" for kind, names in item.symbols.items() if names]
        if rendered:
            lines.append(f"- {item.path} — " + "; ".join(rendered))
            if len(lines) >= limit:
                break
    return lines


def _documentation_evidence(intelligence: RepositoryIntelligence, limit: int = 8) -> list[str]:
    lines: list[str] = []
    for path, excerpt in list(intelligence.documentation_excerpts.items())[:limit]:
        lines.extend([f"- {path}:", "  BEGIN EXCERPT"])
        lines.extend(f"  {line}" for line in excerpt.splitlines())
        lines.append("  END EXCERPT")
    return lines or ["- no README/AGENTS purpose excerpt detected"]


def _architecture_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = ["ARCHITECTURE EVIDENCE COLLECTED PROGRAMMATICALLY", "", "Runtime and framework evidence:"]
    lines.extend(_technology_evidence(intelligence))

    lines.extend(["", "Detected languages:"])
    _append_items(lines, (f"- {language}: {count} source files" for language, count in sorted(intelligence.languages.items())))

    lines.extend(["", "Application topology:", *_topology(intelligence), "", "Entry points:"])
    _append_items(lines, (f"- {path}" for path in intelligence.entry_points[:80]))

    lines.extend(["", "Routes and page files:"])
    _append_items(lines, (f"- {path}" for path in (intelligence.api_routes + intelligence.page_files)[:160]))

    lines.extend(["", "Configuration and CI/deployment evidence:"])
    _append_items(lines, (f"- {path}" for path in (intelligence.config_files + intelligence.ci_files)[:120]))

    lines.extend(["", "External integration candidates:"])
    _append_items(lines, (f"- {path}" for path in intelligence.integration_files[:80]))

    lines.extend(["", "State-management candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"state"})))

    lines.extend(["", "Caching and revalidation candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"cache"})))

    lines.extend(["", "Environment-variable evidence:"])
    _append_items(
        lines,
        (
            f"- {evidence.value} — {evidence.file}:{evidence.line}"
            if evidence.line
            else f"- {evidence.value} — {evidence.file}"
            for evidence in intelligence.env_variable_evidence[:120]
        ),
    )

    lines.extend(["", "Resolved local dependency graph:"])
    _append_items(lines, _dependency_edges(intelligence))
    return lines


def _pattern_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    groups = {
        "Provider/Context candidates": {"context"},
        "Adapter candidates": {"adapter", "integration"},
        "Repository candidates": {"repository"},
        "Factory candidates": {"factory"},
        "Observer/subscription candidates": {"observer"},
    }
    lines = ["PATTERN EVIDENCE COLLECTED PROGRAMMATICALLY"]
    for title, signals in groups.items():
        matches = _signal_files(intelligence, signals)
        lines.extend(["", title + ":"])
        _append_items(lines, (f"- {path}" for path in matches), "- no conventional candidate detected")

    lines.extend(["", "Structural symbols in candidate files:"])
    candidates = set(sum((_signal_files(intelligence, signals) for signals in groups.values()), []))
    by_path = {item.path: item for item in intelligence.source_files}
    symbol_lines: list[str] = []
    for path in sorted(candidates)[:100]:
        item = by_path[path]
        symbols = [f"{kind}: {', '.join(names[:20])}" for kind, names in item.symbols.items() if names]
        if symbols:
            symbol_lines.append(f"- {path} — " + "; ".join(symbols))
    _append_items(lines, symbol_lines)

    lines.extend(["", "Local dependency relationships:"])
    _append_items(lines, _dependency_edges(intelligence))
    return lines


def _requirements_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = ["REQUIREMENTS EVIDENCE COLLECTED PROGRAMMATICALLY", "", "Application entry points:"]
    _append_items(lines, (f"- {path}" for path in intelligence.entry_points[:80]))

    lines.extend(["", "API routes / operations:"])
    _append_items(lines, (f"- {path}" for path in intelligence.api_routes[:160]))

    lines.extend(["", "Pages / user-facing surfaces:"])
    _append_items(lines, (f"- {path}" for path in intelligence.page_files[:160]))

    lines.extend(["", "Potential operation-bearing symbols:"])
    _append_items(lines, _operation_symbols(intelligence))

    lines.extend(["", "Validation / guard candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"validation"})))

    lines.extend(["", "State and persistence candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"state"})))

    lines.extend(["", "Relevant dependency relationships:"])
    _append_items(lines, _dependency_edges(intelligence))
    return lines


def _business_purpose_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = [
        "BUSINESS-PURPOSE EVIDENCE COLLECTED PROGRAMMATICALLY",
        "",
        "Primary documentation and explicit repository intent:",
        *_documentation_evidence(intelligence),
        "",
        "Detected runtime/framework evidence:",
        *_technology_evidence(intelligence),
        "",
        "Application entry points:",
    ]
    _append_items(lines, (f"- {path}" for path in intelligence.entry_points[:80]))

    lines.extend(["", "User-facing pages / surfaces:"])
    _append_items(lines, (f"- {path}" for path in intelligence.page_files[:120]))

    lines.extend(["", "API / externally callable operations:"])
    _append_items(lines, (f"- {path}" for path in intelligence.api_routes[:160]))

    lines.extend(["", "External integration candidates:"])
    _append_items(lines, (f"- {path}" for path in intelligence.integration_files[:100]))

    lines.extend(["", "Potential capability-bearing symbols:"])
    _append_items(lines, _operation_symbols(intelligence, limit=100))

    lines.extend(["", "Representative resolved dependency relationships:"])
    _append_items(lines, _dependency_edges(intelligence, limit=120))

    lines.extend(["", "Repository topology:"])
    lines.extend(_topology(intelligence))
    return lines


def _business_requirements_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = [
        "BUSINESS-REQUIREMENTS EVIDENCE COLLECTED PROGRAMMATICALLY",
        "",
        "Explicit product/domain intent from documentation:",
        *_documentation_evidence(intelligence, limit=6),
        "",
        "User-facing surfaces that may imply actor goals and workflows:",
    ]
    _append_items(lines, (f"- {path}" for path in intelligence.page_files[:140]))

    lines.extend(["", "Externally callable operations / integration boundaries:"])
    _append_items(lines, (f"- {path}" for path in intelligence.api_routes[:160]))

    lines.extend(["", "Capability and state-changing operation symbols:"])
    _append_items(lines, _operation_symbols(intelligence, limit=140))

    lines.extend(["", "State-management candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"state"}, limit=100)))

    lines.extend(["", "Validation / guard candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"validation"}, limit=100)))

    lines.extend(["", "External integration candidates:"])
    _append_items(lines, (f"- {path}" for path in intelligence.integration_files[:100]))

    lines.extend(["", "Representative dependency relationships relevant to workflows:"])
    _append_items(lines, _dependency_edges(intelligence, limit=160))
    return lines


def _features_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = ["FEATURE EVIDENCE COLLECTED PROGRAMMATICALLY", "", "User-facing pages / feature surfaces:"]
    _append_items(lines, (f"- {path}" for path in intelligence.page_files[:180]))

    lines.extend(["", "Routes / externally invoked feature operations:"])
    _append_items(lines, (f"- {path}" for path in intelligence.api_routes[:180]))

    lines.extend(["", "Capability-bearing symbols:"])
    _append_items(lines, _operation_symbols(intelligence, limit=160))

    lines.extend(["", "State-management candidates supporting interactive features:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"state"}, limit=100)))

    lines.extend(["", "External integrations used by features:"])
    _append_items(lines, (f"- {path}" for path in intelligence.integration_files[:100]))

    lines.extend(["", "Representative dependency paths linking feature surfaces to implementation:"])
    _append_items(lines, _dependency_edges(intelligence, limit=160))
    return lines

def _scope_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = [
        "SCOPE EVIDENCE COLLECTED PROGRAMMATICALLY",
        "",
        "Repository baseline:",
        f"- tracked files: {intelligence.file_count}",
        f"- technologies: {', '.join(intelligence.technologies) or 'not detected'}",
        f"- languages: {intelligence.languages or 'none detected'}",
        "",
        "Primary documentation and explicit repository intent:",
    ]
    lines.extend(_documentation_evidence(intelligence))

    lines.extend(["", "Application entry points:"])
    _append_items(
        lines,
        (f"- {path}" for path in intelligence.entry_points[:100]),
    )

    lines.extend(["", "API routes / externally callable surfaces:"])
    _append_items(
        lines,
        (f"- {path}" for path in intelligence.api_routes[:160]),
    )

    lines.extend(["", "User-facing pages / application surfaces:"])
    _append_items(
        lines,
        (f"- {path}" for path in intelligence.page_files[:160]),
    )

    lines.extend(["", "Application topology:"])
    _append_items(lines, _topology(intelligence, limit=60))

    lines.extend(["", "External integration candidates:"])
    _append_items(
        lines,
        (f"- {path}" for path in intelligence.integration_files[:120]),
    )

    lines.extend(["", "Configuration and deployment boundaries:"])
    _append_items(
        lines,
        (
            f"- {path}"
            for path in (intelligence.config_files + intelligence.ci_files)[:160]
        ),
    )

    lines.extend(["", "Representative dependency relationships:"])
    _append_items(
        lines,
        _dependency_edges(intelligence, limit=180),
    )

    return lines


def _high_level_design_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = ["HIGH-LEVEL-DESIGN EVIDENCE COLLECTED PROGRAMMATICALLY", "", "Repository topology:", *_topology(intelligence)]

    lines.extend(["", "Entry points and externally visible boundaries:"])
    _append_items(lines, (f"- {path}" for path in (intelligence.entry_points + intelligence.api_routes + intelligence.page_files)[:200]))

    lines.extend(["", "External integration boundaries:"])
    _append_items(lines, (f"- {path}" for path in intelligence.integration_files[:100]))

    lines.extend(["", "State-management candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"state"}, limit=100)))

    lines.extend(["", "Caching/revalidation candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"cache"}, limit=100)))

    lines.extend(["", "Configuration and deployment boundaries:"])
    _append_items(lines, (f"- {path}" for path in (intelligence.config_files + intelligence.ci_files)[:120]))

    lines.extend(["", "Resolved dependency relationships for subsystem interaction:"])
    _append_items(lines, _dependency_edges(intelligence, limit=220))
    return lines


def _low_level_design_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = ["LOW-LEVEL-DESIGN EVIDENCE COLLECTED PROGRAMMATICALLY", "", "Source symbols and local contracts:"]
    _append_items(lines, _symbol_inventory(intelligence, limit=180))

    lines.extend(["", "Operation-bearing symbols and implementation entry points:"])
    _append_items(lines, _operation_symbols(intelligence, limit=160))

    lines.extend(["", "Validation / guard candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"validation"}, limit=100)))

    lines.extend(["", "State-management candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"state"}, limit=100)))

    lines.extend(["", "Detailed local dependency relationships:"])
    _append_items(lines, _dependency_edges(intelligence, limit=260))
    return lines


def _implementation_detail_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = ["IMPLEMENTATION-DETAIL EVIDENCE COLLECTED PROGRAMMATICALLY", "", "Runtime/framework and dependency evidence:"]
    lines.extend(_technology_evidence(intelligence))

    lines.extend(["", "Package scripts:"])
    _append_items(lines, (f"- {name}: {command}" for name, command in intelligence.package_scripts.items()))

    lines.extend(["", "Implementation symbols:"])
    _append_items(lines, _symbol_inventory(intelligence, limit=180))

    lines.extend(["", "Operational / state-changing symbols:"])
    _append_items(lines, _operation_symbols(intelligence, limit=180))

    lines.extend(["", "Configuration and environment evidence:"])
    _append_items(lines, (f"- {path}" for path in intelligence.config_files[:120]))
    _append_items(lines, (f"- env {name}" for name in intelligence.env_variables[:120]))

    lines.extend(["", "Integration implementation candidates:"])
    _append_items(lines, (f"- {path}" for path in intelligence.integration_files[:120]))

    lines.extend(["", "Error / fallback candidates:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"error"}, limit=100)))

    lines.extend(["", "Resolved implementation dependency graph:"])
    _append_items(lines, _dependency_edges(intelligence, limit=260))
    return lines


def _testing_harness_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = ["TESTING-HARNESS EVIDENCE COLLECTED PROGRAMMATICALLY", "", "Detected test files:"]
    _append_items(lines, (f"- {path}" for path in intelligence.test_files[:180]))

    lines.extend(["", "Test / fixture / mock candidates from source symbols and paths:"])
    _append_items(lines, (f"- {path}" for path in _signal_files(intelligence, {"test"}, limit=120)))

    lines.extend(["", "Test-related package scripts:"])
    _append_items(
        lines,
        (
            f"- {name}: {command}"
            for name, command in intelligence.package_scripts.items()
            if any(token in name.lower() or token in command.lower() for token in ("test", "jest", "vitest", "playwright", "cypress", "pytest"))
        ),
    )

    lines.extend(["", "Configuration / CI files that may define test execution:"])
    _append_items(lines, (f"- {path}" for path in (intelligence.config_files + intelligence.ci_files)[:160]))

    lines.extend(["", "Representative dependency relationships involving test files:"])
    test_set = set(intelligence.test_files)
    test_edges = [
        f"- {edge.source} -> {edge.target}" + (f" (import: {edge.imported_as})" if edge.imported_as else "")
        for edge in intelligence.dependency_edges
        if edge.source in test_set or edge.target in test_set
    ]
    _append_items(lines, test_edges[:180])
    return lines


def _future_directions_evidence(intelligence: RepositoryIntelligence) -> list[str]:
    lines = ["FUTURE-DIRECTIONS EVIDENCE COLLECTED PROGRAMMATICALLY", "", "Explicit maintenance / debt markers:"]
    markers = [f"- {item.path}: {', '.join(item.markers)}" for item in intelligence.source_files if item.markers]
    _append_items(lines, markers[:140])

    lines.extend(["", "Parser coverage / analysis gaps:"])
    lines.append(f"- parse summary: {intelligence.parse_summary}")

    lines.extend(["", "Testing evidence available for identifying coverage gaps:"])
    _append_items(lines, (f"- {path}" for path in intelligence.test_files[:140]))

    lines.extend(["", "Configuration / CI evidence relevant to operational maturity:"])
    _append_items(lines, (f"- {path}" for path in (intelligence.config_files + intelligence.ci_files)[:140]))

    lines.extend(["", "External integrations that may represent brittle or evolving boundaries:"])
    _append_items(lines, (f"- {path}" for path in intelligence.integration_files[:100]))

    lines.extend(["", "Representative dependency relationships for concentration / coupling review:"])
    _append_items(lines, _dependency_edges(intelligence, limit=180))
    return lines


def _baseline(intelligence: RepositoryIntelligence) -> list[str]:
    parsed = intelligence.parse_summary.get("parsed", 0)
    failed = intelligence.parse_summary.get("failed", 0)
    unavailable = intelligence.parse_summary.get("unavailable", 0)
    attempted = intelligence.parse_summary.get("attempted", parsed + failed + unavailable)
    parser_text = f"{parsed} parsed / {failed} parse errors / {unavailable} parser unavailable ({attempted} attempted)"
    return [
        "REPOSITORY BASELINE",
        f"Repository files considered: {intelligence.file_count}",
        f"Technologies: {', '.join(intelligence.technologies) or 'not detected'}",
        f"Languages: {intelligence.languages or 'none detected'}",
        f"Environment variables: {', '.join(intelligence.env_variables) or 'none detected'}",
        f"Package scripts: {intelligence.package_scripts}",
        f"Documentation files: {', '.join(intelligence.documentation_files[:40]) or 'none detected'}",
        f"Tree-sitter parsing: {parser_text}",
    ]


def _generic_evidence(intelligence: RepositoryIntelligence, phase: str) -> list[str]:
    lines = [
        f"PROGRAMMATIC EVIDENCE FOR {phase}",
        "",
        "Directory structure:",
        *_topology(intelligence),
        "",
        "Routes:",
    ]
    _append_items(lines, (f"- {path}" for path in intelligence.routes[:120]))

    lines.extend(["", "Tests:"])
    _append_items(lines, (f"- {path}" for path in intelligence.test_files[:120]))

    lines.extend(["", "Dependency relationships:"])
    _append_items(lines, _dependency_edges(intelligence))
    return lines


def build_phase_intelligence(intelligence: RepositoryIntelligence, phase: str) -> str:
    lines = [
        f"PHASE-SPECIFIC DETERMINISTIC INTELLIGENCE: {phase}",
        "The following evidence was collected programmatically before the LLM started. Treat verified facts as repository evidence, distinguish inference from fact, and do not repeat repository-wide discovery merely to rediscover these facts.",
        "",
        *_baseline(intelligence),
        "",
    ]
    collectors = {
        "business-purpose": _business_purpose_evidence,
         "scope": _scope_evidence,
        "business-requirements": _business_requirements_evidence,
        "features": _features_evidence,
        "software-requirements": _requirements_evidence,
        "technology-architecture": _architecture_evidence,
        "design-pattern": _pattern_evidence,
        "high-level-design": _high_level_design_evidence,
        "low-level-design": _low_level_design_evidence,
        "implementation-detail": _implementation_detail_evidence,
        "testing-harness": _testing_harness_evidence,
        "future-directions": _future_directions_evidence,
    }
    collector = collectors.get(phase)
    if collector:
        lines.extend(collector(intelligence))
    else:
        lines.extend(_generic_evidence(intelligence, phase))
    return "\n".join(lines)


def collect_phase_intelligence(
    repository,
    phase: str,
    intelligence: RepositoryIntelligence | None = None,
) -> tuple[RepositoryIntelligence, str]:
    intelligence = intelligence or collect_repository_intelligence(repository)
    return intelligence, build_phase_intelligence(intelligence, phase)
