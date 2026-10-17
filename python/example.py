"""Woolworths vs Coles price comparison to CSV (Google Sheets ready).

Usage: python example.py "milk" "coffee beans" --limit 20
Writes prices_<date>.csv with one row per product from both supermarkets.
"""
import argparse
import csv
import datetime
import os
import sys

from apify_client import ApifyClient

ACTORS = {
    "Woolworths": "lagenuina_agency/woolworths-scraper",
    "Coles": "lagenuina_agency/coles-scraper",
}
TOKEN = os.environ.get("APIFY_TOKEN")
if not TOKEN:
    sys.exit("Set APIFY_TOKEN first: https://console.apify.com/settings/integrations")


def unit_price(it):
    # Woolworths: cup_price + cup_measure ("$1.65 / 1L"); Coles: unit_price + unit_quantity + unit.
    if it.get("cup_price") is not None:
        return it["cup_price"], it.get("cup_measure")
    if it.get("unit_price") is not None:
        return it["unit_price"], f'{it.get("unit_quantity") or 1}{it.get("unit") or ""}'
    return None, None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("terms", nargs="+", help="products to compare, e.g. milk")
    p.add_argument("--limit", type=int, default=20, help="products per keyword and supermarket")
    p.add_argument("--specials-only", action="store_true")
    a = p.parse_args()

    client = ApifyClient(TOKEN)
    run_input = {"operation": "search", "query": a.terms[0], "searchTerms": a.terms[1:], "limit": a.limit, "specialsOnly": a.specials_only}
    today = datetime.date.today().isoformat()
    rows = 0
    with open(f"prices_{today}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "store", "search", "product", "brand", "size", "price", "special_price", "discount_pct", "unit_price", "per", "available", "url"])
        for store, actor in ACTORS.items():
            run = client.actor(actor).call(run_input=run_input)
            for it in client.dataset(run["defaultDatasetId"]).iterate_items():
                up, per = unit_price(it)
                w.writerow([today, store, it.get("search_query"), it.get("full_name") or it.get("name"), it.get("brand"), it.get("size"),
                            it.get("price"), it.get("discount_price"), it.get("discount_percent"), up, per, it.get("is_available"), it.get("source_url")])
                rows += 1
    print(f"{rows} products -> prices_{today}.csv")


if __name__ == "__main__":
    main()
