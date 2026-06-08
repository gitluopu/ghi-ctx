USER_ACTOR = "gitluopu"
BOT_ACTOR = "ai-paul-bot"


def _label_for_login(login: str) -> str | None:
    if login == USER_ACTOR:
        return "user"
    # GitHub appends "[bot]" suffix to bot accounts
    if login == BOT_ACTOR or login.startswith(BOT_ACTOR + "["):
        return "bot"
    return None


def _actor_of(event: dict) -> str | None:
    for key in ("actor", "user"):
        a = event.get(key)
        if a and isinstance(a, dict):
            return a.get("login")
    return None


def _render_event(event: dict, label: str) -> str:
    etype = event.get("event", "commented")
    body = event.get("body") or ""
    header = f"### [{label}] {etype}"
    if body:
        return f"{header}\n{body}"
    return header


def classify(timeline: list[dict]) -> dict | None:
    """
    Returns None for caseA (bot handled last).
    Returns {"context": str, "problem": str} for caseB.
    """
    labeled = []
    for event in timeline:
        login = _actor_of(event)
        if login is None:
            continue
        label = _label_for_login(login)
        if label is None:
            continue
        labeled.append((label, event))

    if not labeled:
        return None

    last_label, _ = labeled[-1]
    if last_label == "bot":
        return None  # caseA

    # caseB — find last bot index
    last_bot_idx = None
    for i, (label, _) in enumerate(labeled):
        if label == "bot":
            last_bot_idx = i

    if last_bot_idx is None:
        # no bot message at all — everything is problem, no context
        ctx_events = []
        problem_events = labeled
    else:
        ctx_events = labeled[: last_bot_idx + 1]
        problem_events = labeled[last_bot_idx + 1 :]

    context = "\n\n---\n\n".join(
        _render_event(e, lbl) for lbl, e in ctx_events
    )
    problem = "\n\n---\n\n".join(
        _render_event(e, lbl) for lbl, e in problem_events
    )
    return {"context": context, "problem": problem}
