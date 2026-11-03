"""Agent loop: ask the brain what to do, run the chosen tool, repeat."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from src.llm import Brain, ToolName

MAX_STEPS = 10

# A tool receives the path of the file under review and returns its output.
ToolFunction = Callable[[str], str]


@dataclass(frozen=True)
class AgentResult:
    """Outcome of one agent run."""

    completed: tuple[ToolName, ...]
    outputs: dict[ToolName, str]
    finished: bool
    error: str | None = None


class Agent:
    """Runs tools chosen by a brain, within a fixed step limit."""

    def __init__(
        self,
        brain: Brain,
        tools: Mapping[ToolName, ToolFunction],
        max_steps: int = MAX_STEPS,
    ) -> None:
        self._brain = brain
        self._tools = dict(tools)
        self._max_steps = max_steps

    def run(self, target: str) -> AgentResult:
        completed: list[ToolName] = []
        outputs: dict[ToolName, str] = {}

        for _ in range(self._max_steps):
            action = self._brain.decide(tuple(completed))

            if action.tool is ToolName.FINISH:
                return AgentResult(tuple(completed), outputs, finished=True)

            tool = self._tools.get(action.tool)
            if tool is None:
                return self._fail(completed, outputs, f"No tool registered: {action.tool}")

            try:
                outputs[action.tool] = tool(target)
            except Exception as exc:  # report only the error type, never its message
                return self._fail(
                    completed, outputs, f"Tool {action.tool} failed: {type(exc).__name__}"
                )
            completed.append(action.tool)

        return self._fail(completed, outputs, "Step limit reached")

    @staticmethod
    def _fail(
        completed: list[ToolName], outputs: dict[ToolName, str], message: str
    ) -> AgentResult:
        return AgentResult(tuple(completed), outputs, finished=False, error=message)