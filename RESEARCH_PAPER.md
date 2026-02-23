## AI-Powered Local Market Research Platform – Research Summary

### 1. Introduction

This project targets data-driven identification of business opportunities in Almaty, Kazakhstan.
It combines heterogeneous data sources (business listings, reviews, classifieds-style feeds) with
lightweight analytics and LLM-based reasoning to help entrepreneurs and policymakers understand
where demand is underserved and which sectors are attractive in specific districts.

### 2. Related Work (Literature Review)

Existing work on local market analysis focuses on:

- **Location-based decision support** – studies use POI (points-of-interest) data and census
  statistics to estimate demand and competition for retail locations, often relying on gravity
  models or distance-decay functions.
- **Urban informatics and geospatial data mining** – research exploits open data (e.g. OpenStreetMap,
  Google Maps) to understand urban structure, business density, and activity hotspots.
- **Recommender systems for entrepreneurship** – some systems suggest business types or locations
  based on observed success patterns, but are typically tailored to specific cities or datasets.
- **LLM-assisted business planning** – recent work uses large language models to generate narratives,
  SWOT analyses, and opportunity overviews, but often without strong quantitative grounding.

This platform positions itself at the intersection of these areas: it uses structured analytics
to compute demand, competition, and gaps, and then leverages LLMs to turn those metrics into
actionable, localized recommendations for Almaty.

### 3. Methodology

1. **Data collection and cleaning**
   - Collect business listings from Google Maps and Avito-style sources.
   - Normalize business attributes (name, category, address, coordinates).
   - Validate and clean records, remove duplicates via fingerprinting across ID, name,
     category, and address.

2. **Enrichment**
   - Map raw addresses and district labels to a canonical Almaty district taxonomy.
   - Normalize categories into higher-level business sectors.
   - Compute sentiment scores for descriptions and reviews using lightweight models
     (VADER + keyword heuristics).

3. **Analytics**
   - **Demand scoring**: combine rating, number of reviews, and sentiment into a normalized
     demand score per area/sector.
   - **Competition index**: measure business density (per district and sector).
   - **Market gap score**: high demand with relatively low competition yields stronger scores.
   - **Clustering**: apply KMeans to numerical features to identify latent business clusters.
   - **Trend detection**: use moving averages on time-based aggregates to infer increasing or
     decreasing demand/competition.

4. **LLM integration**
   - Provide structured metrics and key findings as context to an LLM.
   - Use carefully designed prompts to obtain JSON-structured recommendations (title, sector,
     district, rationale, score, risks).
   - Validate and normalize responses client-side to ensure numeric ranges and field presence.

5. **User-facing layer**
   - Expose analytics and recommendations via FastAPI endpoints.
   - Present results through a React dashboard with charts for demand/competition and ranked
   opportunity cards.

### 4. Evaluation

The MVP uses the following evaluation approaches:

- **Quantitative metrics for scoring models**
  - Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) for regression-style scores
    against any available ground truth or expert labels.
  - Rank-based metrics (NDCG, precision@k, recall@k, rank correlation) to assess ordering of
    opportunities and recommendations.
- **Logging and monitoring**
  - Model outputs and evaluation metrics are logged to structured JSON files for offline analysis.
  - This supports longitudinal tracking of how changes in scoring formulas or features affect
    rankings.
- **Qualitative expert review**
  - Domain experts can review top-N recommendations, checking whether high-score opportunities
    align with local knowledge about Almaty’s districts and sectors.

### 5. Limitations and Future Work

- Data coverage may be incomplete or biased toward businesses that maintain an online presence.
- The current sentiment and clustering methods are intentionally lightweight; future iterations
  may incorporate more advanced embeddings and temporal models.
- LLM outputs, even when structurally validated, can still reflect biases from training data;
  human oversight remains critical.
- Future improvements could include user feedback loops, personalization, and forecasting of
  future demand using richer time-series models.

