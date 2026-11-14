import re
from typing import List, Dict

def extract_price(price_display: str) -> int:
    try:
        digits = re.sub(r"[^\d.]", "", price_display)
        if not digits:
            return 0
        return int(float(digits) * 100)
    except Exception:
        return 0

def score_match(result: Dict, target_price_minor: int, keywords: List[str]) -> float:
    """
    Score a result 0.0 - 1.0:
    - Price match (50%): below target = high, at target = good, above = penalty
    - Engagement (25%): social proof
    - Keyword relevance (25%)
    """
    # --- Price Score (50%) ---
    found_price = extract_price(result.get("price_display", ""))
    if target_price_minor <= 0 or found_price == 0:
        price_score = 0.3
    elif found_price <= target_price_minor:
        # Below target: reward cheaper items. Free = 1.0, at target = 0.85
        discount_ratio = found_price / target_price_minor
        price_score = 1.0 - (0.15 * discount_ratio)
    else:
        # Above target: penalize. 50% over target = 0
        overage = (found_price - target_price_minor) / target_price_minor
        price_score = max(0.0, 0.85 - (overage * 2))

    # --- Engagement Score (25%) ---
    likes = result.get("engagement", {}).get("likes", 0)
    comments = result.get("engagement", {}).get("comments", 0)
    engagement_raw = likes + comments * 5
    engagement_score = min(1.0, engagement_raw / 5000)

    # --- Keyword Score (25%) ---
    title_lower = result.get("title", "").lower()
    if keywords:
        hits = sum(1 for kw in keywords if kw.lower() in title_lower)
        relevance_score = hits / len(keywords)
    else:
        relevance_score = 0.5

    return round(
        (price_score * 0.50) + (engagement_score * 0.25) + (relevance_score * 0.25),
        2
    )
