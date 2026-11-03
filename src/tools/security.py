"""Security scan tool: runs Bandit on one Python file, safely."""

import json
import os
# Justification: this tool exists to launch Bandit as a separate process.
import subprocess  # nosec B404
import sys
from pathlib import Path

from src.agent import ToolFunction

MAX_FILE_BYTES = 1_000_000
TIMEOUT_SECONDS = 60
MAX_FINDINGS = 50
_SECRET_HINTS = ("KEY", "TOKEN", "SECRET", "PASSWORD")


class InvalidTargetError(Exception):
    """Target is not a regular .py file."""


class TargetOutsideRootError(Exception):
    """Target is outside the allowed directory."""


class TargetTooLargeError(Exception):
    """Target is larger than MAX_FILE_BYTES."""


class ScanTimeoutError(Exception):
    """Bandit did not finish in time."""


class ScanFailedError(Exception):
    """Bandit failed or returned unreadable output."""


def validate_target(target: str, allowed_root: Path) -> Path:
    """Return the resolved path if the target is safe to scan."""
    path = Path(target).resolve()  # resolves "..", relative paths and symlinks
    root = allowed_root.resolve()
    if not path.is_relative_to(root):
        raise TargetOutsideRootError
    if path.suffix != ".py" or not path.is_file():
        raise InvalidTargetError
    if path.stat().st_size > MAX_FILE_BYTES:
        raise TargetTooLargeError
    return path


def _safe_env() -> dict[str, str]:
    """Copy of the environment without anything that looks like a secret."""
    return {
        name: value
        for name, value in os.environ.items()
        if not any(hint in name.upper() for hint in _SECRET_HINTS)
    }


def _run_bandit(path: Path) -> dict:
    command = [sys.executable, "-m", "bandit", "-f", "json", "-q", str(path)]
    try:
        # Justification: argument list with shell=False, and the target path was
        # validated by validate_target (absolute, inside allowed root, .py file).
        completed = subprocess.run(  # nosec B603
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            env=_safe_env(),
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ScanTimeoutError from exc
    # Bandit exits with 1 when it finds issues, which is a normal result.
    if completed.returncode not in (0, 1):
        raise ScanFailedError
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ScanFailedError from exc


def _summarize(report: dict, path: Path) -> str:
    results = report.get("results", [])
    lines = [f"Bandit findings for {path.name}: {len(results)}"]
    for item in results[:MAX_FINDINGS]:
        lines.append(
            f"- [{item.get('issue_severity')}/{item.get('issue_confidence')}] "
            f"{item.get('test_id')} line {item.get('line_number')}: "
            f"{item.get('issue_text')}"
        )
    if len(results) > MAX_FINDINGS:
        lines.append(f"... {len(results) - MAX_FINDINGS} more findings not shown")
    return "\n".join(lines)


def make_security_scan(allowed_root: Path) -> ToolFunction:
    """Build a security_scan tool restricted to allowed_root."""

    def security_scan(target: str) -> str:
        path = validate_target(target, allowed_root)
        return _summarize(_run_bandit(path), path)

    return security_scan