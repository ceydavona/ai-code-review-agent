"""Brain interface for the code review agent.

The agent asks a "brain" what to do next. The brain can be rule-based,
a local model (Ollama) or a hosted model (Claude), as long as it follows
the same Brain contract. The brain may only choose from the tools listed
in ToolName, so it can never trigger anything outside that allowlist.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class ToolName(StrEnum):
    """The only actions the agent is allowed to take."""

    SECURITY_SCAN = "security_scan"
    RUN_TESTS = "run_tests"
    WRITE_REPORT = "write_report"
    FINISH = "finish"


@dataclass(frozen=True)
class Action:
    """A single decision made by the brain."""

    tool: ToolName


class Brain(ABC):
    """Contract that every brain must follow."""

    @abstractmethod
    def decide(self, completed: tuple[ToolName, ...]) -> Action:
        """Return the next action, given the tools already completed."""


class RuleBasedBrain(Brain):
    """Free brain without any model: follows a fixed plan in order."""

    _DEFAULT_PLAN = (
        ToolName.SECURITY_SCAN,
        ToolName.RUN_TESTS,
        ToolName.WRITE_REPORT,
    )

    def __init__(self, plan: tuple[ToolName, ...] = _DEFAULT_PLAN) -> None:
        self._plan = plan

    def decide(self, completed: tuple[ToolName, ...]) -> Action:
        for tool in self._plan:
            if tool not in completed:
                return Action(tool)
        return Action(ToolName.FINISH)