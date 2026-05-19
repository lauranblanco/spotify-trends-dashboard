# Spotify Streaming Trends Dashboard

🌐 [Leer en Español](README.es.md)

**Author:** Laura Blanco | **Stack:** Python · pylast · Pandas · Plotly · Streamlit · statsmodels
**Live demo:** [spotify-trends-dashboard.streamlit.app](https://spotify-trends-dashboard-2kzwefkozz5grasp5w5yjp.streamlit.app/)

An interactive dashboard that combines two complementary perspectives on music: the **sonic structure** of tracks (audio features from a static Kaggle dataset) and the **real audience behavior** by country (live data from Last.fm API). The dashboard is organized into two tabs with clearly separated methodologies.

---

## Dashboard structure

### 🎵 Tab 1 — Audio DNA
*Source: Kaggle Spotify Tracks Dataset · Static snapshot (~2023)*

| Section | Description |
|---------|-------------|
| Feature relationship | Scatter between any pair of audio features, colored by genre |
| Feature correlation | Pearson heatmap between all audio features |
| Genre sonic profile | Radar chart comparing average audio features across selected genres |

### 📊 Tab 2 — Market Pulse
*Source: Last.fm API · Live data, refreshes every hour*

| Section | Description |
|---------|-------------|
| Live KPIs | Total listeners, dominant genre, #1 artist, #1 track in the selected country |
| Popularity index by genre | Audience share (%) per genre |
| Audience distribution | Treemap of genre share among total listeners |
| Top artists | Artists ranked by their % of total listeners |
| Top tracks | Most listened tracks with their audience share |
| Cross-country heatmap | Which artists appear in top charts across multiple LATAM countries |
| Audio features × Popularity | Cross-source correlation: do genres with higher energy attract larger audiences? |

---

## Methodology

### Data sources & freshness

| Source | Period | Updates |
|--------|--------|---------|
| Kaggle Spotify Tracks Dataset | Snapshot ~2023 | Static — updates only if CSV is manually replaced |
| Last.fm API — top artists by country | Current | Live — refreshes every hour |
| Last.fm API — top tracks by country | Current | Live — refreshes every hour |
| Last.fm API — multi-country comparison | Current | Live — refreshes every 3 hours |

### Popularity Index

Raw listener counts are hard to compare across countries and time periods (a top artist in Colombia might have 5M listeners, while one in Uruguay has 300K). To make the metric meaningful and comparable, all audience data is normalized to a **percentage of the observed market**:

```
popularity_pct = (entity_listeners / total_listeners) × 100
```

Applied at three levels:

| Level | Numerator | Denominator |
|-------|-----------|-------------|
| **Artist** | Monthly listeners of that artist | Sum of all top artists' listeners in the country |
| **Genre** | Sum of listeners of all artists tagged with that genre | Total listeners across all artists |
| **Track** | Listeners of that track | Sum of all top tracks' listeners in the country |

A genre with `popularity_pct = 35%` means that 35 out of every 100 listener-sessions in the top of that country go to artists of that genre.

### Cross-source analysis

The final section of Tab 2 crosses both datasets: it takes the **Last.fm genre popularity index** (live) and merges it with the **average audio features per genre** from Kaggle (static). The result answers: *which sonic characteristics correlate with real audience share in LATAM right now?*

Since the Last.fm data refreshes hourly, this correlation will shift over time as listening trends evolve — making it the most dynamic section of the dashboard.

---

## How to interpret the results

### 🎵 Audio DNA tab

**Feature relationship (scatter)**
Each point is a track. If points of the same color (genre) cluster together, that genre has a consistent sonic identity. Scattered points mean the genre is sonically diverse. Look for genres that occupy unique corners of the chart — those are the most sonically distinct.

**Feature correlation (heatmap)**
- Values near **+1**: features tend to appear together (e.g., high energy usually means high loudness)
- Values near **−1**: features are inversely related (e.g., more acoustic = less energy)
- Values near **0**: no linear relationship between the two features

Tip: `valence` (musical positivity) often shows surprising correlations — check whether happier-sounding songs are also more danceable in the dataset.

**Genre sonic profile (radar)**
A larger polygon means higher average values in those dimensions. Overlapping polygons signal similar sonic identities; diverging shapes reveal distinct genres. Use this to understand *what makes a genre sound like itself* — not just its name.

---

### 📊 Market Pulse tab

**Live KPIs**
These update every hour. The dominant genre reflects what is driving the market *right now* in the selected country. Compare across countries using the sidebar selector to spot regional differences.

**Popularity index by genre**
This is a relative metric — it measures *share of attention*, not absolute size. If reggaeton shows 40%, it means 4 in every 10 listener-sessions among the top artists go to reggaeton acts. A shift over time signals a changing market, not necessarily more or fewer total listeners.

**Audience distribution (treemap)**
Block size = audience share. A few dominant blocks suggest a concentrated market (winner-takes-all); many similarly sized blocks suggest a fragmented one. Compare LATAM countries to see how concentrated each market is.

**Top artists / top tracks**
The percentage shown is each artist's or track's share of the total observed listeners. An artist capturing 15% in a country is significantly dominant — most markets are highly fragmented with artists under 5%.

**Cross-country heatmap**
Numbers indicate rank in each country's local top (1 = most listened). Empty cells mean the artist does not appear in that country's chart. Artists with many colored cells are achieving cross-border reach — a key signal for labels and distributors looking to expand.

**Audio features × Popularity (cross-source)**
- The **bar chart** shows the Pearson correlation between each audio feature and genre popularity. Positive = genres with more of that feature tend to have larger audiences; negative = less of that feature correlates with more listeners.
- The **scatter plot** shows the strongest relationship. Each dot is a genre. The trend line indicates the direction — but always check how many genres are in the sample before drawing strong conclusions.
- Because the Last.fm index refreshes hourly, this section reflects *current* listening trends, not historical averages.

---

## Local setup

### 1. Clone the repository
```bash
git clone https://github.com/tu-usuario/spotify-trends-dashboard.git
cd spotify-trends-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the Last.fm API key
Create a `.env` file at the project root (never commit this to GitHub):
```
LASTFM_API_KEY=your_api_key_here
```

To get a free API key:
1. Create an account at [last.fm](https://www.last.fm/join)
2. Go to [last.fm/api/account/create](https://www.last.fm/api/account/create)
3. Fill in the form (app name: anything, e.g. `music-portfolio`)
4. Copy the generated API Key

### 4. Dataset
The dataset is already included in the repository at `data/kaggle_tracks.csv`.

Source: [Spotify Tracks Dataset — Audio Features](https://www.kaggle.com/datasets/saichaitanyareddyai/spotify-tracks-dataset-audio-features) on Kaggle.

### 5. Run the dashboard
```bash
streamlit run app.py
```

---

## Streamlit Cloud deployment

1. Push the repository to GitHub (`.env` is excluded via `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repository
3. Under **Settings → Secrets**, add:
   ```toml
   LASTFM_API_KEY = "your_api_key_here"
   ```
4. Streamlit Cloud will generate a public URL automatically

---

## Project structure

```
spotify-trends-dashboard/
├── app.py                      # Main Streamlit app (tab routing, sidebar, data loading)
├── utils/
│   ├── data_load.py            # Kaggle + Last.fm ingestion, popularity index calculation
│   └── statistics.py           # All visualization sections (Tab 1 & Tab 2)
├── data/
│   └── kaggle_tracks.csv       # Historical dataset (~18MB, versioned in git)
├── requirements.txt
├── .env.example                # Environment variable template
├── .gitignore
├── PACE_strategy.md            # Project strategy document
├── README.md                   # This file (English)
└── README.es.md                # Spanish version
```

---

## About the author

Laura Blanco — Data Scientist focused on music analytics and the LATAM market.

[LinkedIn](https://linkedin.com/in/tu-perfil) · [GitHub](https://github.com/tu-usuario) · [Full portfolio](https://github.com/tu-usuario)
