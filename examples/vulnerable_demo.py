"""INTENTIONALLY VULNERABLE demo file for the code review agent.

Never import or run this file. It only exists to be scanned.
"""

import hashlib
import subprocess

password = "hunter2"


def run(command):
    return subprocess.call(command, shell=True)


def digest(data):
    return hashlib.md5(data).hexdigest()