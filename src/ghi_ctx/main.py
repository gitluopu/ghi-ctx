import argparse
import json
import sys

from .classifier import classify
from .github import get_open_issues, get_timeline

DEFAULT_OWNER = "gitluopu"


def _parse_repo(raw: str) -> tuple[str, str]:
    if "/" in raw:
        owner, repo = raw.split("/", 1)
    else:
        owner, repo = DEFAULT_OWNER, raw
    return owner, repo


def _build_timeline(issue: dict, owner: str, repo: str) -> list[dict]:
    open_event = {
        "event": "opened",
        "user": issue.get("user"),
        "title": issue.get("title") or "",
        "body": issue.get("body") or "",
        "created_at": issue.get("created_at", ""),
    }
    return [open_event] + get_timeline(owner, repo, issue["number"])


def cmd_ctx(owner: str, repo: str):
    issues = get_open_issues(owner, repo)
    result_issues = []
    for issue in issues:
        timeline = _build_timeline(issue, owner, repo)
        classified = classify(timeline)
        if classified is None:
            continue
        result_issues.append(
            {
                "issueId": issue["number"],
                "context": classified["context"],
                "problem": classified["problem"],
            }
        )
    output = {
        "needHandleIssue": len(result_issues) > 0,
        "issues": result_issues,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_timeline(owner: str, repo: str, issue_id: int):
    timeline = get_timeline(owner, repo, issue_id)
    print(json.dumps(timeline, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="ghi-ctx",
        description="Get GitHub issue context for AI bot handoff",
    )
    parser.add_argument("repo", metavar="<repo>")
    parser.add_argument("subcommand", nargs="?", metavar="timeline")
    parser.add_argument("issue_id", nargs="?", type=int, metavar="<issue_id>")
    args = parser.parse_args()

    owner, repo = _parse_repo(args.repo)

    if args.subcommand == "timeline":
        if args.issue_id is None:
            parser.error("timeline requires an issue id")
        cmd_timeline(owner, repo, args.issue_id)
    else:
        cmd_ctx(owner, repo)


if __name__ == "__main__":
    main()
