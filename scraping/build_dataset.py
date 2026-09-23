"""
Builds data/raw_gmaps_scrape.csv from the scraper output in scraping/out/.

  1. merge the scraper files and drop duplicate places (same place_id)
  2. keep only food venues (category -> concept map) inside Coimbatore district
  3. remove personal data: reviewer names, review text, photos, owner ids,
     e-mails and phone numbers (phone is kept only as a 0/1 flag)

Run from the project root:  python scraping/build_dataset.py
"""

import glob
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "scraping", "out", "results*.csv")
OUT = os.path.join(ROOT, "data", "raw_gmaps_scrape.csv")

# Coimbatore district bounding box (city + Pollachi / Mettupalayam / Annur)
LAT_MIN, LAT_MAX = 10.55, 11.40
LNG_MIN, LNG_MAX = 76.70, 77.25

# Each Google category found in the scrape is mapped to a dining concept.
# Anything not listed here (grocery, wholesale, lodging, etc.) is dropped.
CONCEPTS = {
    "Multi-cuisine / General": [
        "Restaurant", "Indian restaurant", "Family restaurant", "Food court",
        "Fine dining restaurant", "Buffet restaurant", "Eatery", "Dhaba", "Cafeteria",
        "Small plates restaurant", "Bistro", "Country food restaurant", "Indian takeaway",
        "Meal delivery", "Breakfast restaurant", "Soup kitchen", "Soup restaurant",
        "Health food restaurant", "Organic restaurant", "Bar", "Bar & grill", "Lounge bar",
    ],
    "South Indian & Regional": [
        "South Indian restaurant", "Chettinad restaurant", "Kerala restaurant",
        "Karnataka restaurant", "Tiffin center", "Tiffin Service Provider",
    ],
    "Vegetarian": [
        "Vegetarian restaurant", "Vegan restaurant", "Gujarati restaurant", "Rajasthani Restaurant",
    ],
    "Biryani & Non-veg": [
        "Biryani restaurant", "Non Vegetarian Restaurant", "Chicken restaurant",
        "Barbecue restaurant", "Seafood restaurant", "Fish restaurant", "Arab restaurant",
        "Lebanese restaurant", "Middle Eastern restaurant", "Halal restaurant",
        "Mughlai restaurant", "Hyderabadi restaurant", "Kebab shop",
    ],
    "North Indian & Global": [
        "North Indian restaurant", "Punjabi restaurant", "Chinese restaurant",
        "Italian restaurant", "Asian restaurant", "Pan-Asian restaurant",
        "Continental restaurant", "Western restaurant", "Burmese restaurant",
        "European restaurant", "Mexican restaurant", "Malaysian restaurant",
        "Vietnamese restaurant", "American restaurant", "Southern restaurant (US)",
        "Momo restaurant", "Noodle shop", "Delivery Chinese restaurant",
        "Chinese takeaway", "Fish & chips restaurant",
    ],
    "Fast food & Quick bites": [
        "Fast food restaurant", "Pizza restaurant", "Pizza takeaway", "Pizza delivery",
        "Shawarma restaurant", "Hamburger restaurant", "Fried chicken takeaway",
        "Snack bar", "Sandwich shop", "Takeout restaurant",
    ],
    "Cafe & Beverages": [
        "Cafe", "Coffee shop", "Juice shop", "Tea store", "Tea house", "Coffee store",
        "Bubble tea store", "Art cafe", "Chocolate cafe", "Soft drinks shop",
        "Fruit parlor", "Beverages", "Coffee roastery",
    ],
    "Bakery & Desserts": [
        "Bakery and Cake Shop", "Ice cream shop", "Cake shop", "Dessert shop",
        "Indian sweets shop", "Sweet shop", "Dessert restaurant", "Pastry shop",
        "Sweets and dessert buffet", "Patisserie", "Wedding bakery",
    ],
}
CATEGORY_TO_CONCEPT = {cat: concept for concept, cats in CONCEPTS.items() for cat in cats}
PHONE_IN_TEXT = r"(?i)(phone number|phone|mobile|mob|cell|ph)?[\s.:]*(\+?91[\s-]?)?\b\d{5}\s?\d{5}\b"


def parse_json(val, default):
    try:
        return json.loads(val) if isinstance(val, str) and val.strip() else default
    except json.JSONDecodeError:
        return default


def partner_sources(val):
    """[{"link":..., "source":"swiggy.com"}, ...] -> "swiggy.com;zomato.com" """
    items = parse_json(val, [])
    names = sorted({i.get("source", "") for i in items if isinstance(i, dict) and i.get("source")})
    return ";".join(names) if names else pd.NA


def menu_link(val):
    m = parse_json(val, {})
    link = m.get("link") if isinstance(m, dict) else None
    return link if link else pd.NA


def area_of(a):
    """Locality name: last part of the borough, else the part before the comma in
    the city field ("Gandhipuram, Coimbatore" -> "Gandhipuram")."""
    borough = (a.get("borough") or "").split(",")[-1].strip()
    if borough:
        return borough
    city = [p.strip() for p in (a.get("city") or "").split(",") if p.strip()]
    return city[0] if city else pd.NA


def main():
    files = sorted(f for f in glob.glob(SRC) if not os.path.basename(f).startswith("_"))
    df = pd.concat([pd.read_csv(f, low_memory=False) for f in files], ignore_index=True)
    log = [f"merged {len(files)} scrape file(s): {len(df)} rows"]

    df = df.drop_duplicates(subset="place_id").reset_index(drop=True)
    log.append(f"unique places (place_id): {len(df)}")

    df["concept"] = df["category"].map(CATEGORY_TO_CONCEPT)
    out_of_scope = df["concept"].isna().sum()
    df = df[df["concept"].notna()]
    log.append(f"removed {out_of_scope} non-food-service places (retail, wholesale, lodging, services)")

    inside = df["latitude"].between(LAT_MIN, LAT_MAX) & df["longitude"].between(LNG_MIN, LNG_MAX)
    log.append(f"removed {(~inside).sum()} places outside Coimbatore district")
    df = df[inside].reset_index(drop=True)

    addr = df["complete_address"].apply(lambda v: parse_json(v, {}))
    owner = df["owner"].apply(lambda v: parse_json(v, {}))
    stars = df["reviews_per_rating"].apply(lambda v: parse_json(v, {}))

    raw = pd.DataFrame({
        "place_id": df["place_id"],
        "name": df["title"],
        "google_category": df["category"],
        "concept": df["concept"],
        # some owners type a phone number into the address - strip it
        "address": df["address"].str.replace(PHONE_IN_TEXT, "", regex=True)
                                .str.replace(r"\s*,\s*(,\s*)+", ", ", regex=True).str.strip(" ,"),
        "area": addr.apply(area_of),
        "town": addr.apply(lambda a: (a.get("city") or "").split(",")[-1].strip() or pd.NA),
        "pincode": addr.apply(lambda a: a.get("postal_code") or pd.NA),
        "latitude": df["latitude"],
        "longitude": df["longitude"],
        "rating": df["review_rating"].where(df["review_count"] > 0),
        "reviews_count": df["review_count"],
        "price_range": df["price_range"],
        "website": df["website"],
        "has_phone": df["phone"].notna().astype(int),
        # claimed = the profile shows an owner account
        "is_claimed": owner.apply(lambda o: int(bool(o.get("id")))),
        "is_closed": (df["status"].astype(str).str.upper() == "CLOSED").astype(int),
        "online_order_partners": df["order_online"].apply(partner_sources),
        "reservation_partners": df["reservations"].apply(partner_sources),
        "menu_link": df["menu"].apply(menu_link),
        "open_hours": df["open_hours"].where(df["open_hours"].fillna("{}") != "{}"),
        "popular_times": df["popular_times"].where(df["popular_times"].fillna("{}").str.len() > 2),
        "attributes": df["about"],
        "maps_url": df["link"],
    })
    # star counts are kept for description only, they are not used as features
    for k, name in zip("12345", ["stars_1", "stars_2", "stars_3", "stars_4", "stars_5"]):
        raw[name] = stars.apply(lambda s: s.get(k, 0)).astype(int)

    raw.to_csv(OUT, index=False, encoding="utf-8")
    log.append(f"saved {os.path.relpath(OUT, ROOT)}: {raw.shape[0]} rows x {raw.shape[1]} columns")
    log.append(f"  rated: {raw['rating'].notna().sum()} | closed: {raw['is_closed'].sum()}")
    print("\n".join("[BUILD] " + line for line in log))
    print(raw["concept"].value_counts().to_string())


if __name__ == "__main__":
    main()
