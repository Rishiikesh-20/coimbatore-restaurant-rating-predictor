"""Writes queries.txt: every food keyword combined with every Coimbatore locality.

Google Maps returns only about 120 places per search, so many small
searches are used and the duplicates are removed afterwards (build_dataset.py)."""

KEYWORDS = [
    "restaurant", "cafe", "bakery", "fast food", "biryani", "mess",
    "veg restaurant", "non veg restaurant", "family restaurant",
    "fine dining", "chettinad restaurant", "south indian restaurant",
    "north indian restaurant", "chinese restaurant", "pizza", "shawarma",
    "juice shop", "ice cream", "tea shop", "hotel food",
]

LOCALITIES = [
    "RS Puram", "Gandhipuram", "Peelamedu", "Saibaba Colony", "Saravanampatti",
    "Singanallur", "Race Course", "Vadavalli", "Town Hall", "Ukkadam",
    "Ramanathapuram", "Sulur", "Kuniyamuthur", "Thudiyalur", "Ganapathy",
    "Hopes College", "Avinashi Road", "Tidel Park Coimbatore", "Kalapatti",
    "Ondipudur", "Podanur", "Kovaipudur", "Sundarapuram", "Vilankurichi",
    "Neelambur", "Chinniyampalayam", "Thondamuthur", "Perur", "Kavundampalayam",
    "Edayarpalayam", "Sivananda Colony", "Tatabad", "Gandhi Park",
    "Selvapuram", "Koundampalayam", "Vellalore", "Karamadai", "Mettupalayam",
    "Annur", "Pollachi", "Kinathukadavu", "Madukkarai", "Ettimadai",
    "Nallampalayam", "Uppilipalayam", "Puliyakulam", "Sowripalayam",
    "Kurichi", "Periyanaickenpalayam", "Narasimhanaickenpalayam",
    "Saravanampatti Keeranatham", "Chinnavedampatti", "Vilankurichi Road",
    "Trichy Road Coimbatore", "Mettupalayam Road Coimbatore",
    "Sathy Road Coimbatore", "Pollachi Road Coimbatore", "Palakkad Road Coimbatore",
    "Marudhamalai Road", "Thadagam Road",
]

with open("queries.txt", "w") as f:
    for loc in LOCALITIES:
        for kw in KEYWORDS:
            f.write(f"{kw} in {loc}, Coimbatore\n")
print(len(KEYWORDS) * len(LOCALITIES), "queries written")
