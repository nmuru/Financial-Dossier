"""Cancellation-aware repository cloning."""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from .run_control import RunCancelled, RunControl


def clone_repository(repo_url: str, workspace: Path, run_control: RunControl | None = None) -> Path:
    repository = workspace / "target-repository"
    if repository.exists():
        shutil.rmtree(repository, ignore_errors=True)

    process = subprocess.Popen(
        ["git", "clone", "--depth", "1", repo_url.strip(), str(repository)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        while process.poll() is None:
            if run_control and run_control.is_cancelled():
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
                raise RunCancelled("Analysis stopped by the user.")
            time.sleep(0.1)

        stdout, stderr = process.communicate()
        if run_control and run_control.is_cancelled():
            raise RunCancelled("Analysis stopped by the user.")
        if process.returncode != 0:
            raise RuntimeError("Could not clone the target repository: " + (stderr or stdout).strip()[:2000])
        return repository
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=2)
