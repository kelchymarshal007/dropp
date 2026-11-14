import hashlib
from typing import List, Dict
from app.scout.base_provider import BaseSearchProvider

class MockSearchProvider(BaseSearchProvider):
    name = "mock"

    def search(self, query: str, location: str, max_results: int = 20) -> List[Dict]:
        platforms = ["instagram", "tiktok", "facebook", "whatsapp"]
        results = []
        for i in range(min(max_results, 5)):
            seed = hashlib.md5(f"{query}{i}".encode()).hexdigest()[:8]
            platform = platforms[i % len(platforms)]
            # Cheaper items have MORE engagement (realistic marketplace behavior)
            results.append({
                "platform": platform,
                "url": f"https://{platform}.com/p/{seed}",
                "seller_handle": f"@seller_{seed}",
                "title": query,
                "price_display": f"${250 + i * 15}",  # $250, $265, $280, $295, $310
                "image_url": f"https://picsum.photos/seed/{seed}/400/400",
                "engagement": {
                    "likes": 2000 - i * 300,   # 2000, 1700, 1400, 1100, 800
                    "comments": 60 - i * 10    # 60, 50, 40, 30, 20
                }
            })
        return results
