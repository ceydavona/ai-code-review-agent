from src.llm import Action, RuleBasedBrain, ToolName


def test_first_action_is_security_scan():
    brain = RuleBasedBrain()
    assert brain.decide(()) == Action(ToolName.SECURITY_SCAN)


def test_follows_plan_in_order():
    brain = RuleBasedBrain()
    done = (ToolName.SECURITY_SCAN,)
    assert brain.decide(done) == Action(ToolName.RUN_TESTS)


def test_finishes_when_plan_is_complete():
    brain = RuleBasedBrain()
    done = (ToolName.SECURITY_SCAN, ToolName.RUN_TESTS, ToolName.WRITE_REPORT)
    assert brain.decide(done) == Action(ToolName.FINISH)


def test_custom_plan_is_respected():
    brain = RuleBasedBrain(plan=(ToolName.SECURITY_SCAN,))
    assert brain.decide(()) == Action(ToolName.SECURITY_SCAN)
    assert brain.decide((ToolName.SECURITY_SCAN,)) == Action(ToolName.FINISH)