# Premium Positioning Viability Predictor for Coimbatore Restaurants

Business Analytics, individual case study
Rishiikesh S K | CB.SC.U4CSE23236 | CSE-C
Domain: Food and Hospitality

## 1. Problem statement
In Coimbatore's crowded restaurant market, the Google Maps rating is usually the first thing a customer looks at. A rating of 4.2 stars or more is treated as the entry ticket to premium positioning: below it, customers are less willing to pay more and delivery platforms show the listing less prominently.

Owners do not know which of the things they control (Google profile, services, amenities, price, opening hours, type of restaurant) go with reaching this rating, so money often goes into décor while cheaper changes are ignored. Restaurant owners, investors and food-delivery platforms would benefit from knowing this.

## 2. Objectives
1. Collect a dataset of Coimbatore food venues by scraping Google Maps.
2. Predict whether a venue reaches 4.2 stars using attributes that do not leak the rating, and compare Logistic Regression, Decision Tree and KNN (plus a Random Forest) on Accuracy, F1 and ROC-AUC.
3. Measure the effect of each factor and give practical recommendations.

## 3. Data collection
- Source: Google Maps public business listings.
- Tool: the open-source [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) (headless browser, run in Docker).
- Procedure: Google Maps shows only about 120 results per search, so 1,200 small searches were run (20 food keywords x 60 Coimbatore localities, made by `scraping/make_queries.py`) and the results were merged on Google's `place_id`.
- Date: 22-23 September 2026.
- Numbers: 4,917 rows, 4,908 unique places, 4,667 food venues inside Coimbatore district, and 3,412 venues used for modelling (rated, open, at least 10 reviews).
- Cleaning: `scraping/build_dataset.py` removes duplicates, maps the 167 Google categories to 8 restaurant types or drops them, keeps venues inside the district, and removes personal data (reviewer names, review text, photos, owner IDs, e-mails and phone numbers; only a yes/no phone flag is kept).

A first pilot of 200 listings was collected with the Apify Google Places Crawler, but its free credit was not enough, so the final data was collected with the open-source scraper. The pilot is not part of this analysis.

More detail is in [scraping/README.md](scraping/README.md), and every column is explained in [data/data_dictionary.md](data/data_dictionary.md).

## 4. Methods
- Preprocessing: dropped venues with fewer than 10 reviews (their ratings are too noisy), built 29 features from the raw fields (27 numeric or yes/no and 2 categorical, 37 model columns after encoding), log-transformed the review count, and handled missing values with flags instead of deleting rows. The star counts, review text and review-based "Highlights" are not used as features because they make up the rating. The highest VIF is below 4.
- EDA: chi-square tests (with Benjamini-Hochberg correction), a with/without chart for each feature, opening hours and location.
- Models: Logistic Regression, Decision Tree, KNN and Random Forest, tuned with 5-fold cross-validated grid search on an 80% training split, then checked on the 20% test set and with 5-fold cross-validation on all the data.
- Interpretation: odds ratios with confidence intervals (statsmodels), average marginal effects, Random Forest permutation importance, a small decision tree, and a table scoring each factor.
- Robustness: different review cut-offs (5, 25, 50), a model without the review count, and OLS on the raw rating. An extra check with five features built from Google's popular times (how busy a place is by hour) did not improve any model, so they are not used.

## 5. Results
| Model | CV accuracy | CV F1 | CV ROC-AUC |
|---|---|---|---|
| Logistic Regression | 0.703 ± 0.025 | 0.745 ± 0.020 | 0.768 ± 0.030 |
| Decision Tree | 0.664 ± 0.021 | 0.709 ± 0.021 | 0.718 ± 0.024 |
| KNN | 0.715 ± 0.022 | 0.787 ± 0.017 | 0.760 ± 0.028 |
| Random Forest (extra) | 0.716 ± 0.028 | 0.761 ± 0.024 | 0.783 ± 0.028 |
| Majority-class baseline | 0.609 | - | 0.500 |

Random Forest predicts best. Logistic Regression is the best of the three main models and is the one used to explain the factors. KNN's high F1 comes from predicting "4.2 or higher" for nearly every venue (recall 0.86).

What the logistic regression shows, holding the other features fixed:
1. A claimed Google profile is the strongest factor that is also well supported: the odds are 2.2 times higher, about +15.5 percentage points. 26% of venues have not claimed theirs.
2. Own website (x1.6), menu link (x1.9), online ordering link (x1.6) and UPI/NFC payments (x1.5) also go with better ratings. Wi-Fi is x3.6 but only 3% of venues have it, so that estimate is uncertain.
3. Cafés reach 4.2 in 78% of cases and traditional South Indian restaurants in 32%. Biryani/non-veg places (x0.51) and chain outlets (x0.61) are also lower.
4. Very long weekly opening hours lower the odds (x0.50 per standard deviation). For the same total hours, opening early or late is positive.
5. The mid price band (₹200 to 400) does worst (x0.57).
6. The findings stay the same with different review cut-offs, and the OLS model agrees in direction on all 21 significant factors.

The data is observational, so these are associations, not proof of cause.

## 6. Repository contents
```
README.md
analysis.ipynb            notebook with preprocessing, EDA, models and results
Case_Study_Report.pdf     final report
data/
    raw_gmaps_scrape.csv      collected dataset (4,667 venues, 29 columns)
    restaurant_clean.csv      cleaned modelling dataset (3,412 venues, 38 columns)
    data_dictionary.md
figures/                  charts saved by the notebook
scraping/                 scripts and steps used for data collection
requirements.txt
```

To run the analysis, install `requirements.txt` and run `analysis.ipynb` from the repository root. It reads `data/raw_gmaps_scrape.csv` and rewrites `data/restaurant_clean.csv` and `figures/`. The raw scraper output is not included because it contains reviewer names.

## 7. References
1. Zhang, M., & Luo, L. (2023). Can consumer-posted photos serve as a leading indicator of restaurant survival? Evidence from Yelp. *Management Science*, 69(1), 25–50. https://doi.org/10.1287/mnsc.2022.4359
2. Li, H., Yu, B. X. B., Li, G., & Gao, H. (2023). Restaurant survival prediction using customer-generated content: An aspect-based sentiment analysis of online reviews. *Tourism Management*, 96, 104707.
3. Starakiewicz, T., & Wójcik, P. (2025). Predicting restaurant survival using nationwide Google Maps data. *Knowledge-Based Systems*. https://www.sciencedirect.com/science/article/pii/S095070512500245X
4. Anderson, M., & Magruder, J. (2012). Learning from the crowd: Regression discontinuity estimates of the effects of an online review database. *The Economic Journal*, 122(563), 957–989.
5. Luca, M. (2016). Reviews, reputation, and revenue: The case of Yelp.com. Harvard Business School Working Paper No. 12-016.
6. gosom. *google-maps-scraper*. https://github.com/gosom/google-maps-scraper
7. Google Maps. Public business listings, Coimbatore district, accessed 22–23 September 2026.
8. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *JMLR*, 12, 2825–2830. Seabold, S., & Perktold, J. (2010). statsmodels: Econometric and statistical modeling with Python.
