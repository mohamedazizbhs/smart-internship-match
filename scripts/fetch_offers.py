
import os
import json
import time
import requests

APP_ID = os.environ["ADZUNA_APP_ID"]
APP_KEY = os.environ["ADZUNA_APP_KEY"]

API_URL = "https://api.adzuna.com/v1/api/jobs/fr/search/1"

SEARCH_TERMS = [
    "stage data scientist",
    "stage intelligence artificielle",
    "stage machine learning",
    "stage data engineer"
]

def fetch_offers(keyword):
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 20,
        "what": keyword,
        "sort_by": "date",
        "content-type": "application/json"
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()
    return response.json().get("results", [])


def main():
    all_offers = []
    seen_ids = set()

    for keyword in SEARCH_TERMS:
        print(f"Searching: {keyword}")

        try:
            results = fetch_offers(keyword)
            print(f"Found {len(results)} offers")

            for offer in results:
                offer_id = str(offer.get("id", ""))

                if not offer_id or offer_id in seen_ids:
                    continue

                seen_ids.add(offer_id)

                all_offers.append({
                    "id": offer_id,
                    "source": "adzuna",
                    "title": offer.get("title", ""),
                    "company": (
                        offer.get("company") or {}
                    ).get("display_name", ""),
                    "location": (
                        offer.get("location") or {}
                    ).get("display_name", ""),
                    "description": offer.get(
                        "description", ""
                    ),
                    "url": offer.get("redirect_url"),
                    "date_posted": offer.get("created")
                })

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

        time.sleep(1)

    os.makedirs("data/offers", exist_ok=True)

    output = {
        "fetched_at": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime()
        ),
        "source": "adzuna",
        "search_terms": SEARCH_TERMS,
        "offers": all_offers
    }

    with open(
        "data/offers/raw_offers.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Total unique offers: {len(all_offers)}"
    )
    print("Wrote data/offers/raw_offers.json")


if __name__ == "__main__":
    main()
