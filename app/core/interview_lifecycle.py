ALLOWED_TRANSITIONS = {
    "scheduled": {"ongoing", "cancelled"},
    "ongoing": {"completed"},
    "completed": set(),
    "cancelled": set()
}

def is_vaild_transition(current_status: str, new_status: str) -> bool:
    """
    Check whether an interview status transition is allowed.

    Example:
    - scheduled -> ongoing ✅
    - ongoing -> completed ✅
    - scheduled -> completed ❌
    """
    return new_status in ALLOWED_TRANSITIONS.get(current_status, set())