import os
from typing import List, Dict, Optional

import httpx

YELP_API_KEY = os.getenv("YELP_API_KEY")
BASE_URL = "https://api.yelp.com/v3/businesses/search"


def search_businesses(
    term: str,
    latitude: float,
    longitude: float,
    categories: Optional[List[str]] = None,
    limit: int = 5,
) -> List[Dict]:
    """
    Minimal Yelp Fusion search wrapper.
    Returns a small subset of fields used by the itinerary generator.
    """
    if not YELP_API_KEY:
        print("YELP_API_KEY not set; skip Yelp search.")
        return []

    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    params = {
        "term": term or "food",
        "latitude": latitude,
        "longitude": longitude,
        "limit": limit,
        "sort_by": "rating",
    }
    if categories:
        params["categories"] = ",".join(categories)

    print(f"Yelp search term={params['term']}, lat={latitude}, lon={longitude}")

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(BASE_URL, headers=headers, params=params)
            resp.raise_for_status()
    except Exception as exc:
        print("Yelp API request failed:", exc)
        return []

    data = resp.json().get("businesses", [])
    results = []
    for b in data:
        results.append(
            {
                "name": b.get("name"),
                "address": ", ".join(b.get("location", {}).get("display_address", [])),
                "rating": b.get("rating"),
                "review_count": b.get("review_count"),
                "url": b.get("url"),
                "categories": [c.get("title") for c in b.get("categories", [])],
                "latitude": b.get("coordinates", {}).get("latitude"),
                "longitude": b.get("coordinates", {}).get("longitude"),
            }
        )
    print(f"Yelp returned {len(results)} businesses")
    return results
