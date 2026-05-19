"""
Spotify Streaming Trends Dashboard
Laura Blanco — Music Analytics Portfolio, Proyecto 1

Fuentes:
  - Kaggle Spotify Tracks Dataset  →  audio features y popularidad
  - Last.fm API (pylast)           →  top artistas por país LATAM en tiempo real

Dataset columnas: track_id, artists, album_name, track_name, popularity,
duration_ms, explicit, danceability, energy, key, loudness, mode,
speechiness, acousticness, instrumentalness, liveness, valence, tempo,
time_signature, track_genre
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from utils.data_load import (
    load_kaggle_data,
    load_lastfm_top_artists,
    AUDIO_FEATURES,
    LATAM_COUNTRIES,
)
from utils.statistics import (
    section_kpis,
    section_genre_ranking,
    section_audio_features,
    section_correlation,
    section_popularity_distribution,
    section_radar_by_genre,
    section_top_artists,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Spotify Streaming Trends",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar — filtros globales
# ---------------------------------------------------------------------------

def render_sidebar() -> dict:
    st.sidebar.header("Filtros")

    min_popularity = st.sidebar.slider(
        "Popularidad mínima (dataset Kaggle)",
        min_value=0, max_value=100, value=0,
    )

    top_n_genres = st.sidebar.slider("Top N géneros a mostrar", 5, 25, 12)

    selected_country = st.sidebar.selectbox(
        "País LATAM (Last.fm)",
        list(LATAM_COUNTRIES.keys()),
        index=0,
    )

    return {
        "min_popularity": min_popularity,
        "top_n_genres":   top_n_genres,
        "country_label":  selected_country,
        "country_en":     LATAM_COUNTRIES[selected_country],
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    return df[df["popularity"] >= filters["min_popularity"]].copy()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.title("Spotify Streaming Trends Dashboard")
    st.caption("Music Analytics Portfolio · Laura Blanco · 2026")
    st.markdown("---")

    filters = render_sidebar()

    try:
        df_raw = load_kaggle_data()
    except FileNotFoundError:
        st.error(
            "Dataset no encontrado en `data/kaggle_tracks.csv`. "
            "Descárgalo desde Kaggle y colócalo en la carpeta `data/`."
        )
        st.stop()

    df = apply_filters(df_raw, filters)
    artists_df = load_lastfm_top_artists(country_en=filters["country_en"])

    section_kpis(df)
    st.markdown("---")
    section_genre_ranking(df, filters)
    
    st.markdown("---")
    section_top_artists(artists_df, filters)

    st.markdown("---")
    section_audio_features(df)

    st.markdown("---")
    col_corr, col_box = st.columns(2)
    with col_corr:
        section_correlation(df)
    with col_box:
        section_popularity_distribution(df, filters)

    st.markdown("---")
    section_radar_by_genre(df)

    st.markdown("---")
    st.caption(
        "Datos: Last.fm API (top artistas por país) · "
        "Kaggle Spotify Tracks Dataset (audio features) · "
        "Laura Blanco 2026"
    )


if __name__ == "__main__":
    main()
