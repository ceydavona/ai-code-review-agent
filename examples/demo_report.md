# Code review report: `vulnerable_demo.py`

- Status: completed
- Tools run: security_scan

## Security scan (Bandit)

```text
Bandit findings for vulnerable_demo.py: 4
- [LOW/HIGH] B404 line 7: Consider possible security implications associated with the subprocess module.
- [LOW/MEDIUM] B105 line 9: Possible hardcoded password: 'hunter2'
- [HIGH/HIGH] B602 line 13: subprocess call with shell=True identified, security issue.
- [HIGH/HIGH] B324 line 17: Use of weak MD5 hash for security. Consider usedforsecurity=False
```
