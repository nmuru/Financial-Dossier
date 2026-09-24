"""Deterministic repository intelligence extraction.

The repository scan is intentionally LLM-free. It extracts cheap, reproducible facts
that can be projected into individual SDLC phases before an agent starts reasoning.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

try:
    from tree_sitter_language_pack import get_parser
except ImportError:  # pragma: no cover - dependency is declared in requirements.txt
    get_parser = None  # type: ignore[assignment]

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".mdx", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".css", ".scss", ".mjs", ".cjs", ".html", ".sql",
    ".graphql", ".gql", ".env", ".txt", ".xml", ".properties",
}
SOURCE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist", "build"}
MAX_FILES = 3000
MAX_TEXT_BYTES_PER_FILE = 500_000
MAX_ITEMS_PER_FILE = 100
MAX_DOCUMENT_EXCERPT_CHARS = 1800

LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
}


@dataclass
class Evidence:
    """A machine-derived fact with enough provenance to audit it."""

    kind: str
    value: str
    file: str
    line: int | None = None
    detail: str | None = None
    confidence: str = "verified"


@dataclass
class DependencyEdge:
    source: str
    target: str
    kind: str = "local-import"
    imported_as: str | None = None
    confidence: str = "verified"


@dataclass
class SymbolIntelligence:
    name: str
    kind: str
    line: int
    exported: bool = False


@dataclass
class FileIntelligence:
    path: str
    extension: str
    size: int
    line_count: int
    language: str | None = None
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    symbols: dict[str, list[str]] = field(default_factory=dict)
    symbol_details: list[SymbolIntelligence] = field(default_factory=list)
    resolved_local_imports: list[str] = field(default_factory=list)
    markers: list[str] = field(default_factory=list)
    parse_status: str = "not-attempted"


@dataclass
class RepositoryIntelligence:
    """Versioned, serializable repository knowledge used by phase projections."""

    schema_version: str
    root: str
    file_count: int
    files: list[str]
    directories: list[str]
    languages: dict[str, int]
    technologies: list[str]
    technology_evidence: list[Evidence]
    package_scripts: dict[str, str]
    dependencies: dict[str, str]
    dev_dependencies: dict[str, str]
    env_variables: list[str]
    env_variable_evidence: list[Evidence]
    routes: list[str]
    page_files: list[str]
    api_routes: list[str]
    entry_points: list[str]
    test_files: list[str]
    config_files: list[str]
    ci_files: list[str]
    documentation_files: list[str]
    documentation_excerpts: dict[str, str]
    integration_files: list[str]
    dependency_edges: list[DependencyEdge]
    source_files: list[FileIntelligence]
    parse_summary: dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


def _iter_files(root: Path) -> Iterable[Path]:
    count = 0
    for path in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts) or not path.is_file():
            continue
        yield path
        count += 1
        if count >= MAX_FILES:
            return


def _read_text(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES_PER_FILE:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _imports(text: str, language: str | None = None) -> list[str]:
    out: list[str] = []
    js_patterns = [
        r"(?:from|import)\s+['\"]([^'\"]+)['\"]",
        r"from\s+['\"]([^'\"]+)['\"]",
        r"require\(\s*['\"]([^'\"]+)['\"]\s*\)",
    ]
    for pattern in js_patterns:
        out.extend(re.findall(pattern, text))

    if language == "python":
        for match in re.finditer(r"^\s*from\s+([.\w]+)\s+import\s+", text, flags=re.M):
            out.append(match.group(1))
        for match in re.finditer(r"^\s*import\s+([A-Za-z_][\w.]*)", text, flags=re.M):
            out.append(match.group(1))
    return _unique(out)[:MAX_ITEMS_PER_FILE]


def _exports(text: str) -> list[str]:
    out = re.findall(
        r"export\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var|type|interface)\s+([A-Za-z_$][\w$]*)",
        text,
    )
    return _unique(out)[:MAX_ITEMS_PER_FILE]


def _symbols(text: str, language: str | None = None) -> dict[str, list[str]]:
    symbols = {
        "functions": _unique(re.findall(r"\b(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", text))[:MAX_ITEMS_PER_FILE],
        "classes": _unique(re.findall(r"\bclass\s+([A-Za-z_$][\w$]*)", text))[:MAX_ITEMS_PER_FILE],
        "interfaces": _unique(re.findall(r"\binterface\s+([A-Za-z_$][\w$]*)", text))[:MAX_ITEMS_PER_FILE],
        "types": _unique(re.findall(r"\btype\s+([A-Za-z_$][\w$]*)\s*=", text))[:MAX_ITEMS_PER_FILE],
    }
    if language == "python":
        symbols["functions"] = _unique([
            *symbols["functions"],
            *re.findall(r"^\s*(?:async\s+)?def\s+([A-Za-z_][\w]*)\s*\(", text, flags=re.M),
        ])[:MAX_ITEMS_PER_FILE]
        symbols["classes"] = _unique([
            *symbols["classes"],
            *re.findall(r"^\s*class\s+([A-Za-z_][\w]*)\s*(?:\(|:)", text, flags=re.M),
        ])[:MAX_ITEMS_PER_FILE]
    return symbols


def _language_for(path: Path) -> str | None:
    return LANGUAGE_BY_EXTENSION.get(path.suffix.lower())


def _node_line(node) -> int:
    return int(node.start_point[0]) + 1


def _walk_tree(root_node):
    stack = [root_node]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(node.children))


def _ast_symbols(text: str, language: str) -> tuple[dict[str, list[str]], list[SymbolIntelligence], str]:
    """Extract structural symbols with Tree-sitter, falling back gracefully on parse issues."""
    if get_parser is None:
        return {}, [], "parser-unavailable"

    parser = None
    candidates = [language]
    if language == "tsx":
        candidates = ["tsx", "typescript"]
    for candidate in candidates:
        try:
            parser = get_parser(candidate)
            break
        except Exception:
            parser = None
    if parser is None:
        return {}, [], "parser-unavailable"

    try:
        tree = parser.parse(text.encode("utf-8"))
    except Exception:
        return {}, [], "parse-error"

    type_map = {
        "function_declaration": "functions",
        "function_definition": "functions",
        "method_definition": "methods",
        "class_declaration": "classes",
        "class_definition": "classes",
        "interface_declaration": "interfaces",
        "type_alias_declaration": "types",
        "enum_declaration": "enums",
    }
    name_node_types = {"identifier", "type_identifier", "property_identifier"}
    grouped: dict[str, list[str]] = {}
    details: list[SymbolIntelligence] = []
    for node in _walk_tree(tree.root_node):
        kind = type_map.get(node.type)
        if not kind:
            continue
        name = None
        for child in node.children:
            if child.type in name_node_types:
                name = child.text.decode("utf-8", errors="replace")
                break
        if not name:
            continue
        grouped.setdefault(kind, []).append(name)
        details.append(SymbolIntelligence(name=name, kind=kind, line=_node_line(node)))

    for values in grouped.values():
        del values[MAX_ITEMS_PER_FILE:]
    return grouped, details[:MAX_ITEMS_PER_FILE], "parsed"


def _resolve_js_import(importer: Path, specifier: str, root: Path) -> str | None:
    if not specifier.startswith("."):
        return None
    base = (importer.parent / specifier).resolve()
    candidates = [base]
    for extension in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"):
        candidates.append(Path(str(base) + extension))
    candidates.extend(base / f"index{extension}" for extension in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"))
    for candidate in candidates:
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        if candidate.is_file():
            return candidate.relative_to(root).as_posix()
    return None


def _resolve_python_import(importer: Path, specifier: str, root: Path) -> str | None:
    if specifier.startswith("."):
        dots = len(specifier) - len(specifier.lstrip("."))
        module = specifier[dots:].replace(".", "/")
        base = importer.parent
        for _ in range(max(0, dots - 1)):
            base = base.parent
        candidates = [base / f"{module}.py", base / module / "__init__.py"]
    else:
        module = specifier.replace(".", "/")
        candidates = [
            root / f"{module}.py",
            root / module / "__init__.py",
            importer.parent / f"{module}.py",
            importer.parent / module / "__init__.py",
        ]
    for candidate in candidates:
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        if candidate.is_file():
            return candidate.relative_to(root).as_posix()
    return None


def _resolve_local_import(importer: Path, specifier: str, root: Path, language: str | None) -> str | None:
    if language in {"javascript", "typescript", "tsx"}:
        return _resolve_js_import(importer, specifier, root)
    if language == "python":
        return _resolve_python_import(importer, specifier, root)
    return None


def _package_manifests(root: Path, paths: list[Path]) -> list[tuple[str, dict]]:
    manifests: list[tuple[str, dict]] = []
    for path in paths:
        if path.name != "package.json":
            continue
        try:
            data = json.loads(_read_text(path))
        except (TypeError, json.JSONDecodeError):
            continue
        manifests.append((_relative(path, root), data))
    return manifests


def _python_requirement_files(root: Path, paths: list[Path]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for path in paths:
        if path.name.lower() in {"requirements.txt", "pyproject.toml", "pipfile"}:
            text = _read_text(path)
            if text:
                result.append((_relative(path, root), text))
    return result


def _manifest_maps(package_manifests: list[tuple[str, dict]]) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    scripts: dict[str, str] = {}
    dependencies: dict[str, str] = {}
    dev_dependencies: dict[str, str] = {}
    for manifest_path, package in package_manifests:
        scope = str(Path(manifest_path).parent).replace("\\", "/")
        if scope == ".":
            scope = "root"
        for key, value in package.get("scripts", {}).items():
            script_key = str(key) if scope == "root" else f"{scope}:{key}"
            scripts[script_key] = str(value)
        for key, value in package.get("dependencies", {}).items():
            dep_key = str(key) if str(key) not in dependencies else f"{scope}:{key}"
            dependencies[dep_key] = str(value)
        for key, value in package.get("devDependencies", {}).items():
            dep_key = str(key) if str(key) not in dev_dependencies else f"{scope}:{key}"
            dev_dependencies[dep_key] = str(value)
    return scripts, dependencies, dev_dependencies


def _technology_evidence(
    package_manifests: list[tuple[str, dict]],
    python_requirement_files: list[tuple[str, str]],
    files: list[str],
) -> tuple[list[str], list[Evidence]]:
    node_mapping = {
        "next": "Next.js", "react": "React", "typescript": "TypeScript", "tailwindcss": "Tailwind CSS",
        "fastapi": "FastAPI", "pydantic": "Pydantic", "django": "Django", "flask": "Flask",
        "pytest": "Pytest", "playwright": "Playwright", "cypress": "Cypress", "jest": "Jest",
        "vitest": "Vitest", "graphql": "GraphQL", "openai": "OpenAI",
    }
    python_mapping = {
        "fastapi": "FastAPI", "pydantic": "Pydantic", "pydantic-settings": "Pydantic",
        "django": "Django", "flask": "Flask", "pytest": "Pytest", "openai": "OpenAI",
        "openai-agents": "OpenAI Agents SDK", "uvicorn": "Uvicorn",
    }
    result: list[str] = []
    evidence: list[Evidence] = []

    for manifest_path, package in package_manifests:
        deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
        for key, label in node_mapping.items():
            if key in deps:
                result.append(label)
                evidence.append(Evidence("technology", label, manifest_path, detail=f"dependency {key}={deps[key]}"))
        result.append("Node.js")
        evidence.append(Evidence("technology", "Node.js", manifest_path, detail="Node package metadata present"))

    for requirement_path, text in python_requirement_files:
        result.append("Python")
        evidence.append(Evidence("technology", "Python", requirement_path, detail="Python project metadata present"))
        lowered = text.lower()
        for key, label in python_mapping.items():
            if re.search(rf"(?mi)^\s*{re.escape(key)}(?:\[.*?\])?\s*(?:[<>=!~].*)?$", lowered):
                result.append(label)
                evidence.append(Evidence("technology", label, requirement_path, detail=f"Python dependency {key}"))

    lower_paths = "\n".join(files).lower()
    if any("dockerfile" in path.lower() or "docker-compose" in path.lower() for path in files):
        result.append("Docker")
        matching = next(path for path in files if "docker" in path.lower())
        evidence.append(Evidence("technology", "Docker", matching, detail="Docker configuration present"))
    if "graphql" in lower_paths:
        result.append("GraphQL")
        matching = next((path for path in files if "graphql" in path.lower()), "repository path")
        evidence.append(Evidence("technology", "GraphQL", matching, detail="GraphQL path detected", confidence="inferred"))

    return _unique(result), evidence


def _documentation_excerpt(text: str) -> str:
    lines = []
    in_code_fence = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence or not line:
            continue
        lines.append(line)
        if sum(len(item) + 1 for item in lines) >= MAX_DOCUMENT_EXCERPT_CHARS:
            break
    return "\n".join(lines)[:MAX_DOCUMENT_EXCERPT_CHARS]


def _route_signals(rel: str, text: str) -> list[str]:
    signals: list[str] = []
    lower = rel.lower()
    if lower.endswith(("/route.ts", "/route.tsx", "/route.js", "/route.jsx", "/route.py")) or "/api/" in lower:
        signals.append(rel)

    decorators = re.finditer(
        r"(?m)^\s*@(app|router|api_router)\.(get|post|put|patch|delete|options|head)\(\s*[\"']([^\"']+)[\"']",
        text,
    )
    for match in decorators:
        signals.append(f"{rel}: {match.group(2).upper()} {match.group(3)}")

    flask_routes = re.finditer(r"(?m)^\s*@\w+\.route\(\s*[\"']([^\"']+)[\"'](?:,\s*methods=\[([^\]]+)\])?", text)
    for match in flask_routes:
        methods = (match.group(2) or "GET").replace("\"", "").replace("'", "").strip()
        signals.append(f"{rel}: {methods} {match.group(1)}")
    return signals


def collect_repository_intelligence(repository: Path) -> RepositoryIntelligence:
    root = repository.resolve()
    if not root.is_dir():
        raise ValueError(f"Repository path does not exist: {repository}")

    paths = list(_iter_files(root))
    files = [_relative(path, root) for path in paths]
    dirs = _unique(parent.as_posix() for path in paths for parent in path.relative_to(root).parents if parent.as_posix() != ".")
    package_manifests = _package_manifests(root, paths)
    python_requirement_files = _python_requirement_files(root, paths)
    package_scripts, dependencies, dev_dependencies = _manifest_maps(package_manifests)

    source: list[FileIntelligence] = []
    dependency_edges: list[DependencyEdge] = []
    languages: dict[str, int] = {}
    routes: list[str] = []
    page_files: list[str] = []
    api_routes: list[str] = []
    entry_points: list[str] = []
    test_files: list[str] = []
    config_files: list[str] = []
    ci_files: list[str] = []
    docs: list[str] = []
    doc_excerpts: dict[str, str] = {}
    integration_files: list[str] = []
    env_vars: list[str] = []
    env_evidence: list[Evidence] = []
    parse_summary = {"attempted": 0, "parsed": 0, "failed": 0, "unavailable": 0}

    config_names = {
        "package.json", "requirements.txt", "pyproject.toml", "pipfile", "tsconfig.json", "next.config.ts",
        "next.config.js", "next.config.mjs", "vite.config.ts", "postcss.config.mjs", "tailwind.config.js",
        "tailwind.config.ts", "dockerfile", "docker-compose.yml", "docker-compose.yaml",
    }
    integration_tokens = (
        "shopify", "stripe", "postgres", "mysql", "redis", "kafka", "aws", "gcp", "azure",
        "openai", "graphql", "supabase", "firebase", "github",
    )

    for path in paths:
        rel = _relative(path, root)
        lower = rel.lower()
        ext = path.suffix.lower()
        name = path.name.lower()
        if name in config_names:
            config_files.append(rel)
        if lower.startswith(".github/"):
            ci_files.append(rel)
        if ext in {".md", ".mdx"} or name.startswith("readme"):
            docs.append(rel)
        if re.search(r"(^|/)(tests?|spec|__tests__)(/|$)|\.(test|spec)\.[^.]+$", lower):
            test_files.append(rel)
        if re.search(r"(^|/)(route|api)(/|$)|route\.[jt]sx?$", lower):
            routes.append(rel)
        if re.search(r"(^|/)(page|pages)(/|$)|/page\.[jt]sx?$", lower):
            page_files.append(rel)
        if name in {
            "main.py", "app.py", "server.py", "manage.py", "wsgi.py", "asgi.py",
            "index.ts", "index.tsx", "index.js", "index.jsx", "main.ts", "main.js",
        }:
            entry_points.append(rel)

        language = _language_for(path)
        if language:
            languages[language] = languages.get(language, 0) + 1
        text = _read_text(path) if ext in TEXT_EXTENSIONS or name in {"dockerfile", "makefile"} else ""
        if not text:
            continue

        if rel in docs and (name.startswith("readme") or name in {"agents.md", "contributing.md"}):
            excerpt = _documentation_excerpt(text)
            if excerpt:
                doc_excerpts[rel] = excerpt

        for line_no, line in enumerate(text.splitlines(), 1):
            if name.startswith(".env"):
                match = re.match(r"\s*([A-Z][A-Z0-9_]+)\s*=", line)
                if match:
                    variable = match.group(1)
                    env_vars.append(variable)
                    env_evidence.append(Evidence("environment-variable", variable, rel, line=line_no, detail="assignment found"))
            for match in re.finditer(r"(?:process\.env\.|os\.getenv\(\s*[\"']|os\.environ\.get\(\s*[\"'])([A-Z][A-Z0-9_]+)", line):
                variable = match.group(1)
                env_vars.append(variable)
                env_evidence.append(Evidence("environment-variable", variable, rel, line=line_no, detail="environment access found"))

        route_signals = _route_signals(rel, text)
        routes.extend(route_signals)
        api_routes.extend(route_signals)

        imports = _imports(text, language)
        exports = _exports(text)
        regex_symbols = _symbols(text, language)
        ast_symbols: dict[str, list[str]] = {}
        symbol_details: list[SymbolIntelligence] = []
        parse_status = "not-attempted"
        if language:
            parse_summary["attempted"] += 1
            ast_symbols, symbol_details, parse_status = _ast_symbols(text, language)
            if parse_status == "parsed":
                parse_summary["parsed"] += 1
            elif parse_status == "parser-unavailable":
                parse_summary["unavailable"] += 1
            else:
                parse_summary["failed"] += 1

        merged_symbols: dict[str, list[str]] = {}
        for kind in set(regex_symbols) | set(ast_symbols):
            merged_symbols[kind] = _unique([*ast_symbols.get(kind, []), *regex_symbols.get(kind, [])])[:MAX_ITEMS_PER_FILE]

        exported_set = set(exports)
        for detail in symbol_details:
            detail.exported = detail.name in exported_set

        resolved_imports: list[str] = []
        for imported in imports:
            target = _resolve_local_import(path, imported, root, language)
            if target:
                resolved_imports.append(target)
                dependency_edges.append(DependencyEdge(rel, target, imported_as=imported))

        markers = _unique(re.findall(r"\b(?:TODO|FIXME|HACK|XXX|DEPRECATED)\b", text, flags=re.I))
        source.append(
            FileIntelligence(
                rel, ext, path.stat().st_size, text.count("\n") + 1, language, imports, exports,
                merged_symbols, symbol_details[:MAX_ITEMS_PER_FILE], _unique(resolved_imports), markers, parse_status,
            )
        )

        integration_haystack = f"{lower} {' '.join(imports).lower()}"
        if any(token in integration_haystack for token in integration_tokens):
            integration_files.append(rel)

    technologies, technology_evidence = _technology_evidence(package_manifests, python_requirement_files, files)
    return RepositoryIntelligence(
        schema_version="1.2",
        root=str(root),
        file_count=len(files),
        files=files,
        directories=dirs,
        languages=languages,
        technologies=technologies,
        technology_evidence=technology_evidence,
        package_scripts=package_scripts,
        dependencies=dependencies,
        dev_dependencies=dev_dependencies,
        env_variables=_unique(env_vars),
        env_variable_evidence=env_evidence,
        routes=_unique(routes),
        page_files=_unique(page_files),
        api_routes=_unique(api_routes),
        entry_points=_unique(entry_points),
        test_files=_unique(test_files),
        config_files=_unique(config_files),
        ci_files=_unique(ci_files),
        documentation_files=_unique(docs),
        documentation_excerpts=doc_excerpts,
        integration_files=_unique(integration_files),
        dependency_edges=dependency_edges[:MAX_FILES * 10],
        source_files=source,
        parse_summary=parse_summary,
    )
