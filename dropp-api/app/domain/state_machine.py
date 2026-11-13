STATES = {
    "draft": {"sent", "cancelled"},
    "sent": {"viewed", "negotiating", "declined", "expired", "cancelled"},  # <-- Updated
    "viewed": {"negotiating", "declined", "expired", "cancelled"},
    "negotiating": {"buyer_accepted", "seller_accepted", "declined", "expired", "cancelled"},
    "buyer_accepted": {"seller_accepted", "expired", "cancelled"},
    "seller_accepted": {"awaiting_payment", "expired", "cancelled"},
    "awaiting_payment": {"funded", "expired"},
    "funded": {"shipped", "disputed", "refunded"},
    "shipped": {"delivered", "disputed"},
    "delivered": {"completed", "disputed"},
    "disputed": {"refunded", "completed"},
    "completed": set(),
    "refunded": set(),
    "declined": set(),
    "expired": set(),
    "cancelled": set()
}

def validate_transition(current_state: str, new_state: str) -> bool:
    if current_state not in STATES:
        raise ValueError(f"Unknown current state: {current_state}")
    if new_state not in STATES[current_state]:
        raise ValueError(f"Invalid transition from '{current_state}' to '{new_state}'. Allowed: {STATES[current_state]}")
    return True
