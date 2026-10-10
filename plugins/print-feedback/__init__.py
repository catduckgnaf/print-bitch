"""Safe, deterministic Discord intake guard primitives for Print Bitch.

This module deliberately contains no printer, slicer, filesystem, or network
control. The host plugin adapter must pass the active profile explicitly.
"""
from collections import OrderedDict
import os
import threading
import time

SEEN_TTL = 3600
SEEN_LIMIT = 1024
TERMINAL_LIMIT = 2
CLARIFY_CHOICE_LIMIT = 4

_turns = OrderedDict()
_lock = threading.Lock()


def _purge(mapping, now):
    while mapping and (now - next(iter(mapping.values()))["at"] > SEEN_TTL
                       or len(mapping) >= SEEN_LIMIT):
        mapping.popitem(last=False)


def cap_clarifications(tool_name=None, args=None, platform=None, profile=None, **kwargs):
    """Cap choice lists for the configured Discord profile, preserving an Other path."""
    platform = platform or os.getenv("HERMES_SESSION_PLATFORM")
    profile = profile or os.getenv("HERMES_SESSION_PROFILE")
    if tool_name != "clarify" or platform != "discord" or not isinstance(args, dict):
        return None
    if profile != os.getenv("PRINT_BITCH_PROFILE", "3dprinting"):
        return None
    questions = args.get("questions")
    if not isinstance(questions, list):
        return None
    result = []
    changed = False
    for item in questions:
        if not isinstance(item, dict) or not isinstance(item.get("choices"), list):
            result.append(item)
            continue
        choices = item["choices"]
        if len(choices) <= CLARIFY_CHOICE_LIMIT:
            result.append(item)
            continue
        question = str(item.get("question") or "").strip()
        notice = "Additional options exist. Choose Other to name one or request the remainder."
        if notice not in question:
            question = f"{question} {notice}".strip()
        result.append({**item, "question": question, "choices": choices[:CLARIFY_CHOICE_LIMIT]})
        changed = True
    return {"action": "modify", "args": {**args, "questions": result}} if changed else None


def guard_repeated_terminal(tool_name=None, args=None, profile=None,
                            session_id=None, turn_id=None, **kwargs):
    """Block the third identical terminal request in one explicit turn.

    The guard does not limit distinct commands and has no effect when turn
    identity is unavailable. It is an interaction guard, not a safety system.
    """
    if tool_name != "terminal" or profile != os.getenv("PRINT_BITCH_PROFILE", "3dprinting"):
        return None
    if not session_id or not turn_id or not isinstance(args, dict):
        return None
    command = args.get("command")
    if not isinstance(command, str):
        return None
    key = (str(session_id), str(turn_id))
    now = time.monotonic()
    with _lock:
        _purge(_turns, now)
        state = _turns.setdefault(key, {"at": now, "commands": {}})
        count = state["commands"].get(command, 0)
        if count >= TERMINAL_LIMIT:
            return {"action": "block", "message":
                    "Repeated terminal command already attempted twice this turn. "
                    "Report the result or blocker; do not poll or rephrase to bypass this guard."}
        state["commands"][command] = count + 1
    return None


def reset_state():
    """Clear in-memory guard state; intended for tests and host reloads."""
    with _lock:
        _turns.clear()


def register(ctx):
    """Register only the two non-operational interaction guards."""
    ctx.register_hook("pre_tool_call", cap_clarifications)
    ctx.register_hook("pre_tool_call", guard_repeated_terminal)
