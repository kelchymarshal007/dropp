from typing import Dict, Set

# Strictly enforced transitions based on DROPP_PROJECT_SCOPE.md
STATES = {
    "draft": {"sent", "cancelled"},
    "sent": {"viewed", "declined", "expired", "cancelled"},
    "viewed": {"negotiating", "declined", "expired", "cancelled"},
    "negotiating": {"agreed", "declined", "expired", "cancelled"},
    "agreed": {"awaiting_payment", "expired"},
    "awaiting_payment": {"funded", "expired"},
    "funded": {"shipped", "disputed", "refunded"},
    "shipped": {"delivered", "disputed"},
    "delivered": {"completed", "disputed"},
    "disputed": {"refunded", "completed"},
    # Terminal states
    "completed": set(),
    "refunded": set(),
    "declined": set(),
    "expired": set(),
    "cancelled": set()
}

def validate_transition(current_state: str, new_state: str) -> bool:
    if current_state not in STATES:
        raise ValueError(f"Unknown current state: {current_state}")
    
    allowed = STATES[current_state]
    if new_state not in allowed:
        raise ValueError(f"Invalid transition from '{current_state}' to '{new_state}'. Allowed: {allowed}")
        
    return True
