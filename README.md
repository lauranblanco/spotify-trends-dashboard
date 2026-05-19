# Spotify Streaming Trends Dashboard

🌐 [Leer en Español](README.es.md)

**Author:** Laura Blanco | **Stack:** Python · pylast · Pandas · Plotly · Streamlit
**Live demo:** [spotify-trends-dashboard.streamlit.app](https://spotify-trends-dashboard-2kzwefkozz5grasp5w5yjp.streamlit.app/)

An interactive dashboard analyzing music streaming trends by combining two data sources: the Kaggle Spotify Tracks Dataset (~114k songs with audio features) and the Last.fm API for real-time artist data by LATAM country.

---

## Analyses included

| Section | Source | Type | Description |
|---------|--------|------|-------------|
| Overview | Kaggle | 📸 Static | KPIs: total tracks, genres, avg popularity, #1 track |
| Popularity by genre | Kaggle | 📸 Static | Horizontal bar chart: top N genres by average popularity + track count |
| Audio features vs. popularity | Kaggle | 📸 Static | Interactive scatter between any pair of features, colored by popularity |
| Correlation matrix | Kaggle | 📸 Static | Pearson correlation between all audio features and popularity |
| Top LATAM artists | Last.fm API | 🔄 Live | Most listened artists by country (Colombia, Mexico, Argentina…) |
| Popularity distribution | Kaggle | 📸 Static | Box plot: popularity spread by genre (median, IQR, outliers) |
| Audio features radar | Kaggle | 📸 Static | Comparative profile of average features across selected genres |

## Data scope & freshness

| Source | Period | Updates |
|--------|--------|---------|
| Kaggle Spotify Tracks Dataset | Snapshot collected ~2023 | Static — only updates if the CSV is manually replaced |
| Last.fm API (top artists) | Current | Live — refreshes every hour per country |

> **Note:** Popularity scores, genre rankings, and all audio feature analyses reflect the state of the Kaggle dataset at the time of collection (~2023). They are not connected to real-time Spotify data. Only the "Top LATAM Artists" section reflects current listening trends via Last.fm.

---

## Key findings

> *This section will be completed after finishing the analysis. Three concrete findings with supporting visualizations will be documented here.*

**Finding 1 — Genre popularity patterns:**
*(coming soon)*

**Finding 2 — Audio features and popularity:**
*(coming soon)*

**Finding 3 — Surprising insight about the LATAM market:**
*(coming soon)*

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
├── app.py                  # Main Streamlit dashboard
├── data/
│   └── kaggle_tracks.csv   # Historical dataset (~18MB, versioned in git)
├── utils/                  # Helper modules (in progress)
├── requirements.txt
├── .env.example            # Environment variable template
├── .gitignore
├── PACE_strategy.md        # Project strategy document
├── README.md               # This file (English)
└── README.es.md            # Spanish version
```

---

## Data sources

- **Last.fm API** (via pylast) — real-time top artists by LATAM country, monthly listeners, genres
- **Kaggle Spotify Tracks Dataset** — ~114k songs with full audio features (danceability, energy, valence, tempo, etc.)

---

## About the author

Laura Blanco — Data Scientist focused on music analytics and the LATAM market.

[LinkedIn](https://linkedin.com/in/tu-perfil) · [GitHub](https://github.com/tu-usuario) · [Full portfolio](https://github.com/tu-usuario)
