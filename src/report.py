"""Markdown report built from the result of one agent run."""

from pathlib import Path

from src.agent import AgentResult
from src.llm import ToolName

_TOOL_TITLES = {
    ToolName.SECURITY_SCAN: "Security scan (Bandit)",
    ToolName.RUN_TESTS: "Test run",
    ToolName.WRITE_REPORT: "Report",
}


def _safe_block(text: str) -> str:
    """Wrap text in a code block that the text itself cannot break out of."""
    return "```text\n" + text.replace("```", "'''") + "\n```"


def build_report(target: str, result: AgentResult) -> str:
    """Return a Markdown report. Only the file name is shown, never the full path."""
    name = Path(target).name.replace("`", "")
    status = "completed" if result.finished else "incomplete"

    lines = [
        f"# Code review report: `{name}`",
        "",
        f"- Status: {status}",
    ]
    if result.error:
        lines.append(f"- Error: {result.error}")
    lines.append("- Tools run: " + (", ".join(result.completed) or "none"))

    for tool in result.completed:
        title = _TOOL_TITLES.get(tool, str(tool))
        lines += ["", f"## {title}", "", _safe_block(result.outputs.get(tool, ""))]

    return "\n".join(lines) + "\n"