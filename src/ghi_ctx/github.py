import json
import subprocess
import sys


def _gh(path: str) -> list | dict:
    result = subprocess.run(
        ["gh", "api", "--paginate", path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"gh api error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def get_open_issues(owner: str, repo: str) -> list[dict]:
    return _gh(f"/repos/{owner}/{repo}/issues?state=open&per_page=100")


def get_timeline(owner: str, repo: str, number: int) -> list[dict]:
    return _gh(f"/repos/{owner}/{repo}/issues/{number}/timeline")
