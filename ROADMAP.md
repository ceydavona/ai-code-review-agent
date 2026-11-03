# Roadmap

Each phase ends with a working, tested, pushed version.

## Definition of Done (every task)
- `python -m pytest` passes
- `python -m bandit -r src` is clean (accepted risks are justified in code)
- No secrets in code or git history
- New code has tests
- Docs updated when behavior changes

## Phase 0: Foundation (done)
Environment, Brain interface, agent loop, Bandit tool, tests.

## Phase 1: End-to-end without an LLM (v0.1)
1.1 Report tool (Markdown) · 1.2 CLI in main.py · 1.3 Vulnerable examples · 1.4 End-to-end test

## Phase 2: Local LLM with Ollama (v0.2)
2.1 Pick model and install Ollama · 2.2 Extend Brain interface with tool outputs
2.3 OllamaBrain with validated structured output and fallback to RuleBasedBrain
2.4 Prompt injection tests · 2.5 Evaluation: known-vulnerability examples, detection results

## Phase 3: Test generation (optional)
Execution is off by default and requires an explicit flag.
Temp directory, timeout, output limit, filtered environment. Network isolation limits documented.

## Phase 4: Hardening
SECURITY.md (threat model, limits), pip-audit, CI with tests and Bandit, Dependabot, secret scanning

## Phase 5: Showcase (v1.0)
README with architecture, setup, demo, evaluation results and limitations. Release tag.

## Later
Streamlit UI, JavaScript support, hosted model brain.