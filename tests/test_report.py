from src.agent import AgentResult
from src.llm import ToolName
from src.report import build_report


def _result(output="Bandit findings for bad.py: 1", finished=True, error=None):
    return AgentResult(
        completed=(ToolName.SECURITY_SCAN,),
        outputs={ToolName.SECURITY_SCAN: output},
        finished=finished,
        error=error,
    )


def test_report_contains_findings_and_status(tmp_path):
    report = build_report(str(tmp_path / "bad.py"), _result())
    assert "bad.py" in report
    assert "Status: completed" in report
    assert "Bandit findings for bad.py: 1" in report


def test_report_never_shows_full_path(tmp_path):
    report = build_report(str(tmp_path / "bad.py"), _result())
    assert str(tmp_path) not in report


def test_incomplete_run_shows_error(tmp_path):
    result = _result(finished=False, error="Step limit reached")
    report = build_report(str(tmp_path / "bad.py"), result)
    assert "Status: incomplete" in report
    assert "Step limit reached" in report


def test_output_cannot_break_out_of_code_block(tmp_path):
    result = _result(output="x ``` # injected heading")
    report = build_report(str(tmp_path / "bad.py"), result)
    assert report.count("```") == 2  # only our own opening and closing fence