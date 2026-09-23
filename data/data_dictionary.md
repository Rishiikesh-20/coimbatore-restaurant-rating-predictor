# Data dictionary

## raw_gmaps_scrape.csv (4,667 venues, 29 columns)
Food venues in Coimbatore district scraped from Google Maps on 22-23 September 2026, built by `scraping/build_dataset.py`. Personal data has been removed.

| Column | Description |
|---|---|
| place_id | Google's unique ID for the place (used to remove duplicates) |
| name | Business name |
| google_category | Main Google category, e.g. "South Indian restaurant" |
| concept | Restaurant type from the category: Multi-cuisine / General, South Indian & Regional, Vegetarian, Biryani & Non-veg, North Indian & Global, Fast food & Quick bites, Cafe & Beverages, Bakery & Desserts |
| address | Address |
| area | Locality, e.g. "R.S. Puram" |
| town | Town or city |
| pincode | Postal code |
| latitude, longitude | Coordinates |
| rating | Google average rating (1 to 5), empty if there are no reviews |
| reviews_count | Number of Google reviews |
| price_range | Price band shown by Google, e.g. "₹200-400" (empty if not shown) |
| website | Website on the profile |
| has_phone | 1 if a phone number is listed (the number itself is removed) |
| is_claimed | 1 if the profile has an owner account |
| is_closed | 1 if Google marks it as closed |
| online_order_partners | Ordering platforms linked on the profile, e.g. `swiggy.com;zomato.com` |
| reservation_partners | Table-booking platforms linked on the profile |
| menu_link | Menu link on the profile |
| open_hours | Opening hours for each weekday (JSON) |
| popular_times | How busy the place usually is for each hour of each weekday, 0 to 100 (JSON, available for about 29% of venues). Only used in the extra check in the notebook. |
| attributes | Google's "about" section: service options, amenities, payments, accessibility and so on (JSON, each option marked enabled or not) |
| maps_url | Google Maps link to the place |
| stars_1 ... stars_5 | Number of reviews with 1 to 5 stars. Only for description, never used as features because they make up the rating. |

## restaurant_clean.csv (3,412 venues, 38 columns)
Rated, open venues with at least 10 reviews, created in `analysis.ipynb` (Section 2).

| Column | Description |
|---|---|
| place_id, name, area, town, latitude, longitude | Identification and location |
| concept | Restaurant type (see above) |
| price_tier | Budget (up to ₹200), Mid (up to ₹400), Premium (above ₹400) or Not disclosed |
| rating, reviews_count | Google rating and number of reviews |
| high_rating | Target: 1 if rating is 4.2 or more, otherwise 0 |
| log_reviews | log(1 + reviews_count) |
| weekly_hours | Hours open per week (median used when opening hours are missing) |
| dist_centre_km | Distance to Coimbatore Town Hall in km |
| log_density | log(1 + number of other venues within 1 km) |
| is_claimed | Profile is claimed by an owner |
| own_website | Website is on the venue's own domain |
| social_page_only | The "website" is only an Instagram, Facebook, WhatsApp or Linktree page |
| has_phone | Phone number listed |
| has_menu_link | Menu link on the profile |
| online_ordering | Linked to an online-ordering platform |
| has_attributes | The "about" section exists |
| table_service, delivery, takes_reservations | Services (reservations also counts booking links) |
| restroom, wifi, free_parking, kid_friendly, outdoor_seating, wheelchair_access | Amenities marked as enabled |
| card_payments, digital_payments | Credit/debit cards, UPI/NFC/Google Pay |
| open_late, opens_early | Closes after 11 pm on at least one day, opens before 8 am on at least one day |
| has_hours | Opening hours listed |
| is_chain | Brand name appears at least 3 times in the data |
| veg_only | "Vegetarian options only" |
