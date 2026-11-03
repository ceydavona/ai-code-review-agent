"""Command line entry point.

Usage: python -m src.main <file.py> [--output report.md]
"""

import argparse
import sys
from pathlib import Path

from src.agent import Agent
from src.llm import RuleBasedBrain, ToolName
from src.report import build_report
from src.tools.security import make_security_scan


class InvalidOutputError(Exception):
    """Output path is not a .md file inside the allowed directory."""


def build_agent(root: Path) -> Agent:
    """Agent for v0.1: a fixed plan with only the security scan."""
    return Agent(
        RuleBasedBrain(plan=(ToolName.SECURITY_SCAN,)),
        {ToolName.SECURITY_SCAN: make_security_scan(root)},
    )


def validate_output_path(output: str, root: Path) -> Path:
    """Return the resolved output path if it is safe to write to."""
    path = Path(output).resolve()
    if not path.is_relative_to(root.resolve()):
        raise InvalidOutputError
    if path.suffix != ".md" or not path.parent.is_dir():
        raise InvalidOutputError
    return path


def run(argv: list[str] | None = None, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="code-review-agent",
        description="Review a Python file with the code review agent.",
    )
    parser.add_argument("target", help="Python file to review")
    parser.add_argument(
        "--output",
        help="Write the report to this .md file (inside the current directory)",
    )
    args = parser.parse_args(argv)
    allowed_root = (root or Path.cwd()).resolve()

    output_path = None
    if args.output:
        try:
            output_path = validate_output_path(args.output, allowed_root)
        except InvalidOutputError:
            print(
                "Error: --output must be a .md file inside the current directory.",
                file=sys.stderr,
            )
            return 2

    result = build_agent(allowed_root).run(args.target)
    report = build_report(args.target, result)

    if output_path is not None:
        output_path.write_text(report, encoding="utf-8")
        print(f"Report written to {output_path.name}")
    else:
        print(report)
    return 0 if result.finished else 1


if __name__ == "__main__":
    sys.exit(run())