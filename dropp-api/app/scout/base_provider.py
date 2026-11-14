from typing import List, Dict

class BaseSearchProvider:
    """Every external search engine (SerpApi, Google, Bing) implements this."""
    name: str = "base"

    def search(self, query: str, location: str, max_results: int = 20) -> List[Dict]:
        """
        Returns a list of raw results:
        [
            {
                "platform": "instagram",
                "url": "https://instagram.com/p/...",
                "seller_handle": "@seller",
                "title": "Nike Air Jordan 1",
                "price_display": "$280",
                "image_url": "...",
                "engagement": {"likes": 1200, "comments": 45}
            }, ...
        ]
        """
        raise NotImplementedError
