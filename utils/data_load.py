import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pylast
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AUDIO_FEATURES = [
    "danceability", "energy", "valence",
    "acousticness", "speechiness", "instrumentalness", "liveness",
]

LATAM_COUNTRIES = {
    "Colombia":  "Colombia",
    "México":    "Mexico",
    "Argentina": "Argentina",
    "Chile":     "Chile",
    "Perú":      "Peru",
    "Brasil":    "Brazil",
    "Venezuela": "Venezuela",
    "Ecuador":   "Ecuador",
    "Bolivia":   "Bolivia",
    "Paraguay":  "Paraguay",
    "Uruguay":   "Uruguay",
}

# ---------------------------------------------------------------------------
# Data loading — Kaggle dataset
# ---------------------------------------------------------------------------

def load_kaggle_data(path: str = "data/kaggle_tracks.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df["genre"] = df["track_genre"].str.strip()
    df["primary_artist"] = (
        df["artists"].str.split(r"[;,]").str[0].str.strip().str.strip("'\"[]")
    )
    df["duration_min"] = (df["duration_ms"] / 60_000).round(2)

    required = ["popularity"] + [f for f in AUDIO_FEATURES if f in df.columns]
    df = df.dropna(subset=required)
    df["popularity"] = df["popularity"].astype(int)
    return df

# ---------------------------------------------------------------------------
# Data loading — Last.fm API
# ---------------------------------------------------------------------------

def load_lastfm_top_artists(country_en: str, limit: int = 20) -> pd.DataFrame:
    api_key = os.getenv("LASTFM_API_KEY") or st.secrets.get("LASTFM_API_KEY", None)

    if not api_key:
        st.warning(
            "API key de Last.fm no encontrada. "
            "Agrega LASTFM_API_KEY a tu archivo .env o a los Secrets de Streamlit Cloud. "
            "Mostrando datos de ejemplo."
        )
        return _sample_artists_data()

    try:
        network = pylast.LastFMNetwork(api_key=api_key)
        top_items = network.get_geo_top_artists(country=country_en, limit=limit)

        records = []
        for item in top_items:
            artist = item.item
            try:
                listeners = int(artist.get_listener_count())
            except Exception:
                listeners = 0
            try:
                tags = artist.get_top_tags(limit=1)
                genre = tags[0].item.get_name() if tags else "—"
            except Exception:
                genre = "—"

            records.append({
                "artist":    artist.get_name(),
                "listeners": listeners,
                "genre":     genre,
                "country":   country_en,
            })

        return pd.DataFrame(records)

    except Exception as exc:
        st.warning(f"Error consultando Last.fm: {exc}. Mostrando datos de ejemplo.")
        return _sample_artists_data()


def _sample_artists_data() -> pd.DataFrame:
    return pd.DataFrame({
        "artist":    ["Bad Bunny", "J Balvin", "Karol G", "Peso Pluma", "Feid",
                      "Maluma", "Anuel AA", "Ozuna", "Rauw Alejandro", "Myke Towers"],
        "genre":     ["reggaeton", "latin pop", "reggaeton", "corridos tumbados",
                      "reggaeton", "latin pop", "trap latino", "reggaeton",
                      "latin pop", "reggaeton"],
        "listeners": [12_500_000, 8_200_000, 10_100_000, 7_400_000, 5_800_000,
                      7_900_000, 4_300_000, 6_600_000, 5_100_000, 3_900_000],
        "country":   ["Colombia"] * 10,
    })