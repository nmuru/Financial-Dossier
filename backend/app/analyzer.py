"""Repository analysis orchestration."""

import json
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Optional

from .agent_runner import run_phase_agent
from .cancellable_download import download_company_facts
from .config import settings
from .exporter import create_download_package
from .edgar_financials import build_financial_intelligence
from .phase_intelligence import build_phase_intelligence
from .renderer import render_analysis
from .repository_intelligence import RepositoryIntelligence, collect_repository_intelligence
from .resource_diagnostics import ResourceDiagnostics
from .run_control import RunCancelled, RunControl
from .cancellable_research import run_phase_research, run_repository_research
from .semantic_research import write_research_artifact
from .review_runner import run_review_code_base, ReviewRunnerError

PHASES = [("revenue-earnings-engine", "Revenue & Earnings Engine"), ("financial-resilience", "Financial Resilience"), ("capital-cash-deployment", "Capital & Cash Deployment"), ("accounting-signals-anomalies", "Accounting Signals & Anomalies")]
REVIEW_PHASE = ("review-code-base", "Review Code Base")
PhaseCompleteCallback = Callable[[dict], None]


def _check_cancelled(run_control: Optional[RunControl]) -> None:
    if run_control and run_control.is_cancelled():
        raise RunCancelled("Analysis stopped by the user.")



def _run_single_phase(phase_key: str, phase_name: str, repository: Path, phase_intelligence: str, output_run_dir: Path, run_id: str, provider: str, model: str, api_key: str, diagnostics: Optional[ResourceDiagnostics] = None, batch_index: Optional[int] = None, run_control: Optional[RunControl] = None, objective: str = "document") -> dict:
    _check_cancelled(run_control)
    if diagnostics: diagnostics.phase_start(phase_key, phase_name, batch_index=batch_index)
    if run_control: run_control.phase_started(phase_key)
    try:
        raw_result, actual_model = run_phase_agent(phase=phase_key, phase_name=phase_name, repository=repository, phase_intelligence=phase_intelligence, provider=provider, model=model, api_key=api_key, run_control=run_control)
        _check_cancelled(run_control)
        if not raw_result.strip(): raise RuntimeError(f"OpenAI Agents SDK returned an empty result for phase '{phase_key}'.")
        phase_output_dir = output_run_dir / phase_key
        phase_output_dir.mkdir(parents=True, exist_ok=True)
        (phase_output_dir / "agent-output.md").write_text(raw_result, encoding="utf-8")
        rendered_result = render_analysis(phase=phase_key, analysis=raw_result, objective=objective, provider=provider, model=actual_model, api_key=api_key, diagnostics=diagnostics, run_control=run_control)
        _check_cancelled(run_control)
        if not rendered_result.strip(): raise RuntimeError(f"Renderer returned an empty result for phase '{phase_key}'.")
        document = f"---\nmodel: {actual_model}\n---\n\n{rendered_result}\n"
        raw_path = phase_output_dir / "raw.md"
        raw_path.write_text(document, encoding="utf-8")
        provenance = {"model": actual_model}
        (phase_output_dir / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
        if run_control: run_control.phase_completed(phase_key)
        if diagnostics: diagnostics.phase_end(phase_key, phase_name, batch_index=batch_index, status="completed")
        return {"phase": phase_key, "phase_name": phase_name, "raw_analysis": rendered_result, "raw_path": str(raw_path), "run_id": run_id, "provenance": provenance}
    except RunCancelled:
        if diagnostics: diagnostics.phase_end(phase_key, phase_name, batch_index=batch_index, status="cancelled")
        raise
    except Exception:
        if run_control and run_control.is_cancelled():
            if diagnostics: diagnostics.phase_end(phase_key, phase_name, batch_index=batch_index, status="cancelled")
            raise RunCancelled("Analysis stopped by the user.")
        if run_control: run_control.phase_failed(_phase_failure(phase_key, phase_name, RuntimeError("Phase execution failed.")))
        if diagnostics: diagnostics.phase_end(phase_key, phase_name, batch_index=batch_index, status="failed")
        raise


def _phase_failure(phase_key: str, phase_name: str, exc: Exception) -> dict:
    error = str(exc)
    error_lower = error.lower()
    if type(exc).__name__.lower() == "maxturnsexceeded" or "max turns" in error_lower or "max_turns" in error_lower:
        error = f"Max turns exceeded for phase '{phase_name}'. Retry the phase or try a different model."
    return {"phase": phase_key, "phase_name": phase_name, "error_type": type(exc).__name__, "error": error}


def _run_batch(batch: list[tuple[str, str]], repository: Path, phase_packages: dict[str, str], output_run_dir: Path, run_id: str, on_phase_complete: Optional[PhaseCompleteCallback] = None, provider: str = "openrouter", model: str = "openrouter/free", api_key: str = "", diagnostics: Optional[ResourceDiagnostics] = None, batch_index: Optional[int] = None, run_control: Optional[RunControl] = None, objective: str = "document") -> tuple[dict, list[dict]]:
    batch_results: dict[str, dict] = {}
    batch_failures: list[dict] = []
    phase_by_future = {}
    with ThreadPoolExecutor(max_workers=len(batch)) as executor:
        for key, name in batch:
            _check_cancelled(run_control)
            future = executor.submit(_run_single_phase, key, name, repository, phase_packages[key], output_run_dir, run_id, provider, model, api_key, diagnostics, batch_index, run_control, objective)
            phase_by_future[future] = (key, name)
        for future in as_completed(phase_by_future):
            key, name = phase_by_future[future]
            try:
                result = future.result()
                batch_results[result["phase"]] = result
                if on_phase_complete and not (run_control and run_control.is_cancelled()): on_phase_complete(result)
            except RunCancelled:
                raise
            except Exception as exc:
                failure = _phase_failure(key, name, exc)
                batch_failures.append(failure)
                if run_control: run_control.phase_failed(failure)
    return batch_results, batch_failures


def _phase_context(phase: str, deterministic: str, repository_research: str, phase_research: str) -> str:
    """Build agent context with deterministic financial data first.

    Legacy repository/semantic research is retained for provenance and secondary
    clues, but it must not force the agent to rediscover financial statement data.
    """
    return "\n\n".join([
        deterministic,
        "LEGACY REPOSITORY / SEMANTIC RESEARCH — SECONDARY CONTEXT ONLY",
        repository_research,
        f"LEGACY PHASE RESEARCH FOR {phase} — SECONDARY CONTEXT ONLY",
        phase_research,
        "PRIMARY EVIDENCE RULE: use the structured SEC financial data above for quantitative claims. "
        "Do not reconstruct statements from the legacy research or generic JSON search.",
    ])


def analyze_repository(company_name: str, phases_per_batch: int = settings.phases_per_batch, number_of_batches: Optional[int] = None, batch_mode: str = "parallel", on_phase_complete: Optional[PhaseCompleteCallback] = None, selected_phases: Optional[list[str]] = None, work_id: Optional[str] = None, provider: str = "openrouter", model: str = "openrouter/free", api_key: Optional[str] = None, run_control: Optional[RunControl] = None, objective: str = "document") -> dict:
    if not company_name or not company_name.strip(): raise ValueError("company_name cannot be empty")
    provider = (provider or "").strip().lower()
    if provider not in {"openrouter", "openai"}: raise ValueError("This backend currently supports OpenRouter and OpenAI through the OpenAI Agents SDK")
    if not model or not model.strip(): raise ValueError("model cannot be empty")
    if not api_key or not api_key.strip(): raise ValueError("api_key cannot be empty")
    if phases_per_batch < 1: raise ValueError("phases_per_batch must be at least 1")
    if batch_mode not in {"parallel", "sequence"}: raise ValueError("batch_mode must be 'parallel' or 'sequence'")
    objective = (objective or "document").strip().lower()
    if objective not in {"document", "understand"}: raise ValueError("objective must be 'document' or 'understand'")

    available = {key for key, _ in PHASES}
    if selected_phases is None:
        count = number_of_batches or 1; selected_ids = [key for key, _ in PHASES[:phases_per_batch * count]]
    else:
        if not selected_phases: raise ValueError("selected_phases must contain at least one phase")
        if len(set(selected_phases)) != len(selected_phases): raise ValueError("selected_phases must not contain duplicates")
        if selected_phases == [REVIEW_PHASE[0]]:
            selected_ids = [REVIEW_PHASE[0]]
        else:
            unknown = set(selected_phases) - available
            if unknown: raise ValueError("selected_phases contains unknown phases: " + ", ".join(sorted(unknown)))
            selected_ids = selected_phases

    run_id = work_id or uuid.uuid4().hex
    if not run_id.isalnum(): raise ValueError("work_id must contain only letters and numbers")
    output_root = Path(settings.analysis_results_dir)
    if not output_root.is_absolute(): output_root = Path(__file__).resolve().parents[1] / output_root
    output_run_dir = output_root / run_id; output_run_dir.mkdir(parents=True, exist_ok=True)
    stale_download = output_run_dir / "sdlc-documentation.zip"
    if stale_download.exists(): stale_download.unlink()

    if selected_ids == [REVIEW_PHASE[0]]:
        _check_cancelled(run_control)
        try:
            result = run_review_code_base(repo_url=repo_url, output_run_dir=output_run_dir, provider=provider, model=model, api_key=api_key, run_control=run_control)
        except ReviewRunnerError:
            raise
        except RunCancelled:
            raise
        create_download_package(output_run_dir)
        if on_phase_complete:
            on_phase_complete({"phase": REVIEW_PHASE[0], "phase_name": REVIEW_PHASE[1], "raw_analysis": result["content"], "raw_path": result["raw_path"], "run_id": run_id, "provenance": result["provenance"]})
        return {"run_id": run_id, "results": {REVIEW_PHASE[0]: {"phase": REVIEW_PHASE[0], "phase_name": REVIEW_PHASE[1], "raw_analysis": result["content"], "raw_path": result["raw_path"], "run_id": run_id, "provenance": result["provenance"]}}, "failures": []}

    phase_by_id = dict(PHASES); definitions = [(key, phase_by_id[key]) for key in selected_ids]; batches = [definitions[i:i + phases_per_batch] for i in range(0, len(definitions), phases_per_batch)]
    diagnostics_dir = Path(settings.resource_diagnostics_dir)
    if not diagnostics_dir.is_absolute(): diagnostics_dir = output_run_dir / diagnostics_dir
    diagnostics = ResourceDiagnostics(enabled=settings.resource_diagnostics_enabled, output_dir=diagnostics_dir, sample_interval_seconds=settings.resource_diagnostics_interval_seconds, run_id=run_id)
    diagnostics.start(); diagnostics.run_event("analysis_started", selected_phases=selected_ids, phases_per_batch=phases_per_batch, batch_mode=batch_mode, batch_count=len(batches), provider=provider, model=model)
    results: dict[str, dict] = {}; failures: list[dict] = []
    try:
        _check_cancelled(run_control)
        with tempfile.TemporaryDirectory(prefix="reverse-engineer-") as tmp:
            workspace = Path(tmp); diagnostics.run_event("workspace_created", workspace=str(workspace)); repository = download_company_facts(company_name, workspace, run_control=run_control); _check_cancelled(run_control)
            # size_bytes = repository_size_bytes(repository)
            # if size_bytes > max_bytes: raise _repository_size_limit_error()
            diagnostics.run_event("financial_source_downloaded", repository=str(repository), 
                                #   repository_size_bytes=size_bytes
                                  )
            intelligence: RepositoryIntelligence = collect_repository_intelligence(repository); diagnostics.run_event("repository_intelligence_collected", files_considered=intelligence.file_count); _check_cancelled(run_control)
            financial_intelligence = build_financial_intelligence(company_name, historical_periods=5, view="standard")
            (output_run_dir / "financial-intelligence.json").write_text(financial_intelligence, encoding="utf-8")
            diagnostics.run_event("financial_intelligence_collected", output_chars=len(financial_intelligence))
            _check_cancelled(run_control)
            # Retain the legacy repository/phase research artifacts, but do not spend
            # LLM turns generating them. Deterministic financial intelligence is now the
            # primary evidence supplied to the analysis agents.
            diagnostics.run_event("repository_research_started", execution="deterministic_only")
            repository_research = intelligence.to_json()
            write_research_artifact(output_run_dir / "repository-research.md", kind="repository", phase=None, content=repository_research)
            diagnostics.run_event("repository_research_completed", output_chars=len(repository_research), llm_requests=0)

            deterministic_phase_packages = {key: build_phase_intelligence(intelligence, key, financial_intelligence=financial_intelligence) for key in selected_ids}
            phase_research: dict[str, str] = {}
            phase_research_failures: list[dict] = []
            diagnostics.run_event("phase_research_started", phase_count=len(selected_ids), expected_llm_requests=0, execution="deterministic_only")
            for key in selected_ids:
                _check_cancelled(run_control)
                phase_research[key] = deterministic_phase_packages[key]
                write_research_artifact(output_run_dir / key / "phase-research.md", kind="phase", phase=key, content=phase_research[key])
                diagnostics.run_event("phase_research_completed", phase=key, output_chars=len(phase_research[key]), llm_requests=0)
            runnable_ids = [key for key in selected_ids if key in phase_research]; runnable_batches = []
            for batch in batches:
                runnable_batch = [(key, name) for key, name in batch if key in phase_research]
                if runnable_batch: runnable_batches.append(runnable_batch)
            phase_packages = {key: _phase_context(key, deterministic_phase_packages[key], repository_research, phase_research[key]) for key in runnable_ids}
            diagnostics.run_event("semantic_context_ready", repository_research_chars=len(repository_research), phase_research_chars={key: len(value) for key, value in phase_research.items()}, phase_research_failed=[failure["phase"] for failure in phase_research_failures], expected_upfront_llm_requests=1 + len(selected_ids))
            if batch_mode == "parallel":
                if runnable_batches:
                    _check_cancelled(run_control)
                    with ThreadPoolExecutor(max_workers=len(runnable_batches)) as executor:
                        futures = {executor.submit(_run_batch, batch, repository, phase_packages, output_run_dir, run_id, on_phase_complete, provider, model, api_key, diagnostics, index, run_control, objective): index for index, batch in enumerate(runnable_batches, start=1)}
                        for future in as_completed(futures):
                            _check_cancelled(run_control); batch_results, batch_failures = future.result(); results.update(batch_results); failures.extend(batch_failures)
            else:
                for index, batch in enumerate(runnable_batches, start=1):
                    _check_cancelled(run_control); batch_results, batch_failures = _run_batch(batch, repository, phase_packages, output_run_dir, run_id, on_phase_complete, provider, model, api_key, diagnostics, index, run_control, objective); results.update(batch_results); failures.extend(batch_failures)
        _check_cancelled(run_control)
        if failures:
            diagnostics.run_event("analysis_failed", completed_phases=list(results), failed_phases=[failure["phase"] for failure in failures])
            create_download_package(output_run_dir)
            return {"run_id": run_id, "results": results, "failures": failures}
        create_download_package(output_run_dir); diagnostics.run_event("analysis_completed", completed_phases=list(results), failed_phases=[]); return {"run_id": run_id, "results": results, "failures": []}
    except RunCancelled:
        diagnostics.run_event("analysis_cancelled", completed_phases=list(results), failed_phases=[failure["phase"] for failure in failures])
        raise
    finally:
        diagnostics.stop()
