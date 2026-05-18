"""
Spotify Streaming Trends Dashboard
Laura Blanco — Music Analytics Portfolio, Proyecto 1

Fuentes:
  - Kaggle Spotify Tracks Dataset → audio features y popularidad
  - Last.fm API (pylast)          → top artistas por país LATAM en tiempo real

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

load_dotenv()

AUDIO_FEATURES = [
    "danceability", "energy", "valence",
    "acousticness", "speechiness", "instrumentalness", "liveness",
]

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
# Data loading — Kaggle dataset
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Cargando dataset...")
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

LATAM_COUNTRIES = {
    "Colombia":  "Colombia",
    "México":    "Mexico",
    "Argentina": "Argentina",
    "Chile":     "Chile",
    "Perú":      "Peru",
    "Brasil":    "Brazil",
    "Venezuela": "Venezuela",
    "Ecuador":   "Ecuador",
}


@st.cache_data(show_spinner="Consultando Last.fm...", ttl=3600)
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
        import pylast
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
        "min_popularity":  min_popularity,
        "top_n_genres":    top_n_genres,
        "country_label":   selected_country,
        "country_en":      LATAM_COUNTRIES[selected_country],
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    return df[df["popularity"] >= filters["min_popularity"]].copy()


# ---------------------------------------------------------------------------
# Section 1 — KPI overview
# ---------------------------------------------------------------------------

def section_kpis(df: pd.DataFrame) -> None:
    st.header("Visión general")
    top_track = df.loc[df["popularity"].idxmax()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Canciones analizadas", f"{len(df):,}")
    c2.metric("Géneros únicos", df["genre"].nunique())
    c3.metric("Popularidad promedio", f"{df['popularity'].mean():.1f}")
    c4.metric(
        "Canción más popular",
        f"{top_track['track_name']} — {top_track['primary_artist']}",
    )


# ---------------------------------------------------------------------------
# Section 2 — Genre popularity ranking
# ---------------------------------------------------------------------------

def section_genre_ranking(df: pd.DataFrame, filters: dict) -> None:
    st.header("Popularidad por género")

    genre_stats = (
        df.groupby("genre")
        .agg(avg_popularity=("popularity", "mean"), track_count=("track_name", "count"))
        .reset_index()
        .sort_values("avg_popularity", ascending=False)
        .head(filters["top_n_genres"])
    )

    fig = px.bar(
        genre_stats.sort_values("avg_popularity"),
        x="avg_popularity",
        y="genre",
        orientation="h",
        color="track_count",
        color_continuous_scale="Teal",
        title=f"Top {filters['top_n_genres']} géneros por popularidad promedio",
        labels={
            "avg_popularity": "Popularidad promedio",
            "genre": "Género",
            "track_count": "Nº tracks",
        },
        template="plotly_dark",
        text=genre_stats.sort_values("avg_popularity")["avg_popularity"].round(1),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=500, coloraxis_colorbar_title="Nº tracks")
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Section 3 — Audio features scatter
# ---------------------------------------------------------------------------

def section_audio_features(df: pd.DataFrame) -> None:
    st.header("Audio features vs. popularidad")

    available = [f for f in AUDIO_FEATURES if f in df.columns]
    col_x, col_y = st.columns(2)
    x_axis = col_x.selectbox("Eje X", available, index=0)
    y_axis = col_y.selectbox("Eje Y", available, index=1)

    sample = df.sample(min(4000, len(df)), random_state=42)

    fig = px.scatter(
        sample,
        x=x_axis, y=y_axis,
        color="popularity",
        color_continuous_scale="Viridis",
        opacity=0.55,
        title=f"{x_axis.capitalize()} vs. {y_axis.capitalize()} — coloreado por popularidad",
        labels={"popularity": "Popularidad"},
        template="plotly_dark",
        hover_data=["track_name", "primary_artist", "genre"],
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Section 4 — Correlation heatmap
# ---------------------------------------------------------------------------

def section_correlation(df: pd.DataFrame) -> None:
    st.header("Correlación: audio features × popularidad")

    cols = ["popularity"] + [f for f in AUDIO_FEATURES if f in df.columns]
    corr = df[cols].corr()

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale="RdBu",
        zmid=0,
        text=corr.round(2).values,
        texttemplate="%{text}",
    ))
    fig.update_layout(
        title="Matriz de correlación",
        template="plotly_dark",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Section 5 — Top LATAM artists via Last.fm
# ---------------------------------------------------------------------------

def section_top_artists(artists_df: pd.DataFrame, filters: dict) -> None:
    st.header(f"Top artistas en {filters['country_label']} — Last.fm")

    fig = px.bar(
        artists_df.sort_values("listeners", ascending=True).tail(15),
        x="listeners",
        y="artist",
        orientation="h",
        color="genre",
        title=f"Top artistas por oyentes mensuales — {filters['country_label']}",
        labels={"listeners": "Oyentes mensuales", "artist": "Artista", "genre": "Género"},
        template="plotly_dark",
        text=artists_df.sort_values("listeners", ascending=True)
            .tail(15)["listeners"]
            .apply(lambda x: f"{x/1_000_000:.1f}M" if x >= 1_000_000 else f"{x:,}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=500, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Section 6 — Popularity distribution by genre (box plot)
# ---------------------------------------------------------------------------

def section_popularity_distribution(df: pd.DataFrame, filters: dict) -> None:
    st.header("Distribución de popularidad por género")

    top_genres = (
        df.groupby("genre")["popularity"]
        .mean()
        .nlargest(filters["top_n_genres"])
        .index
    )
    df_top = df[df["genre"].isin(top_genres)].copy()
    genre_order = (
        df_top.groupby("genre")["popularity"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )

    fig = px.box(
        df_top,
        x="genre", y="popularity",
        color="genre",
        category_orders={"genre": genre_order},
        title=f"Distribución de popularidad — Top {filters['top_n_genres']} géneros",
        labels={"popularity": "Popularidad", "genre": "Género"},
        template="plotly_dark",
        points=False,
    )
    fig.update_layout(height=430, showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Section 7 — Audio features radar by genre
# ---------------------------------------------------------------------------

def section_radar_by_genre(df: pd.DataFrame, filters: dict) -> None:
    st.header("Perfil de audio features por género")

    available = [f for f in AUDIO_FEATURES if f in df.columns and f != "liveness"]
    default_genres = (
        df.groupby("genre")["popularity"]
        .mean()
        .nlargest(5)
        .index.tolist()
    )

    selected = st.multiselect(
        "Géneros a comparar",
        options=sorted(df["genre"].unique().tolist()),
        default=default_genres,
        max_selections=8,
    )

    if not selected:
        st.info("Selecciona al menos un género.")
        return

    radar_df = (
        df[df["genre"].isin(selected)]
        .groupby("genre")[available]
        .mean()
        .reset_index()
    )

    fig = go.Figure()
    for _, row in radar_df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=row[available].values,
            theta=available,
            fill="toself",
            name=row["genre"],
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Perfil promedio de audio features por género",
        template="plotly_dark",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)


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

    col_left, col_right = st.columns([3, 2])
    with col_left:
        section_genre_ranking(df, filters)
    with col_right:
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
    section_radar_by_genre(df, filters)

    st.markdown("---")
    st.caption(
        "Datos: Last.fm API (top artistas por país) · "
        "Kaggle Spotify Tracks Dataset (audio features) · "
        "Laura Blanco 2026"
    )


if __name__ == "__main__":
    main()
