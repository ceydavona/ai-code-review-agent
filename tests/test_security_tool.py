import pytest

from src.tools import security
from src.tools.security import (
    InvalidTargetError,
    TargetOutsideRootError,
    TargetTooLargeError,
    make_security_scan,
)


def test_reports_findings_for_vulnerable_file(tmp_path):
    target = tmp_path / "bad.py"
    target.write_text('password = "hunter2"\n')
    result = make_security_scan(tmp_path)(str(target))
    assert "B105" in result


def test_reports_zero_findings_for_clean_file(tmp_path):
    target = tmp_path / "clean.py"
    target.write_text("x = 1\n")
    result = make_security_scan(tmp_path)(str(target))
    assert "findings for clean.py: 0" in result


def test_rejects_file_outside_allowed_root(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("x = 1\n")
    with pytest.raises(TargetOutsideRootError):
        make_security_scan(root)(str(outside))


def test_rejects_non_python_file(tmp_path):
    target = tmp_path / "notes.txt"
    target.write_text("hello")
    with pytest.raises(InvalidTargetError):
        make_security_scan(tmp_path)(str(target))


def test_rejects_too_large_file(tmp_path, monkeypatch):
    monkeypatch.setattr(security, "MAX_FILE_BYTES", 10)
    target = tmp_path / "big.py"
    target.write_text("x = 1\n" * 10)
    with pytest.raises(TargetTooLargeError):
        make_security_scan(tmp_path)(str(target))


def test_secrets_are_removed_from_child_environment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy-value")
    assert "ANTHROPIC_API_KEY" not in security._safe_env()