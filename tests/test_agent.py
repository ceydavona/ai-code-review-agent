from src.agent import Agent
from src.llm import Action, Brain, RuleBasedBrain, ToolName


def _fake_tools():
    return {
        ToolName.SECURITY_SCAN: lambda target: f"scan {target}",
        ToolName.RUN_TESTS: lambda target: f"tests {target}",
        ToolName.WRITE_REPORT: lambda target: f"report {target}",
    }


class _NeverFinishesBrain(Brain):
    def decide(self, completed):
        return Action(ToolName.SECURITY_SCAN)


def test_runs_full_plan_and_finishes():
    result = Agent(RuleBasedBrain(), _fake_tools()).run("example.py")
    assert result.finished
    assert result.error is None
    assert result.completed == (
        ToolName.SECURITY_SCAN,
        ToolName.RUN_TESTS,
        ToolName.WRITE_REPORT,
    )
    assert result.outputs[ToolName.SECURITY_SCAN] == "scan example.py"


def test_stops_at_step_limit():
    agent = Agent(_NeverFinishesBrain(), _fake_tools(), max_steps=3)
    result = agent.run("example.py")
    assert not result.finished
    assert result.error == "Step limit reached"
    assert len(result.completed) == 3


def test_fails_when_tool_is_not_registered():
    tools = _fake_tools()
    del tools[ToolName.RUN_TESTS]
    result = Agent(RuleBasedBrain(), tools).run("example.py")
    assert not result.finished
    assert "No tool registered" in result.error


def test_tool_failure_reports_only_error_type():
    def broken_tool(target):
        raise ValueError("secret path C:\\private\\file.py")

    tools = _fake_tools()
    tools[ToolName.SECURITY_SCAN] = broken_tool
    result = Agent(RuleBasedBrain(), tools).run("example.py")
    assert not result.finished
    assert "ValueError" in result.error
    assert "private" not in result.error