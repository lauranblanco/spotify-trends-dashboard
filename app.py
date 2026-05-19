"""
Spotify Streaming Trends Dashboard
Laura Blanco — Music Analytics Portfolio, Proyecto 1

Estructura:
  Tab 1 — Audio DNA     : análisis de audio features (Kaggle, estático ~2023)
  Tab 2 — Market Pulse  : comportamiento de usuarios en tiempo real (Last.fm)
"""

import os
import streamlit as st
from dotenv import load_dotenv

from utils.data_load import (
    load_kaggle_data,
    load_lastfm_top_artists,
    load_lastfm_geo_tracks,
    load_lastfm_multi_country,
    compute_popularity_index,
    LATAM_COUNTRIES,
)
from utils.statistics import (
    # Tab 1
    section_audio_scatter,
    section_correlation_audio,
    section_radar_by_genre,
    # Tab 2
    section_kpis_live,
    section_genre_popularity_live,
    section_genre_distribution,
    section_top_artists_live,
    section_top_tracks_live,
    section_multi_country_heatmap,
    section_cross_correlation,
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
        "Popularidad mínima — Kaggle",
        min_value=0, max_value=100, value=0,
        help="Filtra las canciones del dataset por score mínimo de popularidad",
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


def apply_filters(df, filters):
    return df[df["popularity"] >= filters["min_popularity"]].copy()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.title("Spotify Streaming Trends Dashboard")
    st.caption("Music Analytics Portfolio · Laura Blanco · 2026")
    st.markdown("---")

    filters = render_sidebar()

    # --- Carga de datos estáticos (Kaggle)
    try:
        df_raw = load_kaggle_data()
    except FileNotFoundError:
        st.error(
            "Dataset no encontrado en `data/kaggle_tracks.csv`. "
            "Descárgalo desde Kaggle y colócalo en la carpeta `data/`."
        )
        st.stop()

    df = apply_filters(df_raw, filters)

    # --- Tabs
    tab1, tab2 = st.tabs(["🎵 Audio DNA", "📊 Market Pulse"])

    # -----------------------------------------------------------------------
    # Tab 1 — Audio DNA
    # -----------------------------------------------------------------------
    with tab1:
        st.caption("Análisis de audio features · Dataset Kaggle (~2023, estático)")
        st.markdown("---")

        section_audio_scatter(df)
        st.markdown("---")

        col_corr, col_radar = st.columns(2)
        with col_corr:
            section_correlation_audio(df)
        with col_radar:
            section_radar_by_genre(df)

    # -----------------------------------------------------------------------
    # Tab 2 — Market Pulse
    # -----------------------------------------------------------------------
    with tab2:
        st.caption("Comportamiento de usuarios · Last.fm API (en vivo, refresco cada hora)")
        st.markdown("---")

        artists_df = compute_popularity_index(
            load_lastfm_top_artists(country_en=filters["country_en"])
        )
        tracks_df  = load_lastfm_geo_tracks(country_en=filters["country_en"])
        multi_df   = load_lastfm_multi_country()

        section_kpis_live(artists_df, tracks_df, filters)
        st.markdown("---")

        col_pop, col_tree = st.columns([3, 2])
        with col_pop:
            section_genre_popularity_live(artists_df, filters)
        with col_tree:
            section_genre_distribution(artists_df, filters)

        st.markdown("---")

        col_art, col_trk = st.columns(2)
        with col_art:
            section_top_artists_live(artists_df, filters)
        with col_trk:
            section_top_tracks_live(tracks_df, filters)

        st.markdown("---")
        section_multi_country_heatmap(multi_df)

        st.markdown("---")
        section_cross_correlation(artists_df, df)

    st.markdown("---")
    st.caption(
        "Datos: Last.fm API (oyentes en tiempo real) · "
        "Kaggle Spotify Tracks Dataset (audio features ~2023) · "
        "Laura Blanco 2026"
    )


if __name__ == "__main__":
    main()
