# How the data was collected

Source: Google Maps public business listings.
Tool: [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) (open source, MIT licence), which uses a headless Chromium browser through Playwright.
Date: 22-23 September 2026.

## Steps
1. `python scraping/make_queries.py` writes `queries.txt` with 20 food keywords x 60 Coimbatore localities (1,200 searches, for example `biryani in RS Puram, Coimbatore`). Google Maps gives only about 120 results per search, so many small searches are needed to cover the district.
2. Run the scraper. It scrolls each result list and opens every place page:
   ```bash
   docker run -d --name cbe_scrape -v gmaps-cache:/opt \
     -v "$PWD/scraping/queries.txt:/q.txt:ro" -v "$PWD/scraping/out:/out" \
     gosom/google-maps-scraper -input /q.txt -results /out/results.csv -depth 2 -c 6 -exit-on-inactivity 5m
   ```
   The scraper was stopped at about 4,900 unique places because new searches were mostly returning places already collected.
3. `python scraping/build_dataset.py` writes `data/raw_gmaps_scrape.csv`. It:
   - removes duplicate places (4,917 rows to 4,908 unique places)
   - maps the 167 Google categories to restaurant types and drops grocery shops, wholesalers, lodging and services (236 places)
   - keeps venues inside the Coimbatore district (5 places dropped)
   - removes personal data: reviewer names, review text, photos, owner IDs, e-mails and phone numbers (phone is kept as a yes/no flag)

`scraping/out/` holds the raw scraper output. It contains reviewer names, so it is not committed (see `.gitignore`).
