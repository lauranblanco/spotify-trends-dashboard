"""
Spotify Streaming Trends Dashboard
Laura Blanco — Music Analytics Portfolio, Proyecto 1

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

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Spotify Streaming Trends",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

AUDIO_FEATURES = [
    "danceability", "energy", "valence", "acousticness",
    "speechiness", "instrumentalness", "liveness",
]

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Cargando dataset...")
def load_kaggle_data(path: str = "data/kaggle_tracks.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Normalizar géneros (cada fila ya tiene un único género en track_genre)
    df["genre"] = df["track_genre"].str.strip()

    # Primer artista cuando hay varios listados (e.g. "Artist A; Artist B")
    df["primary_artist"] = (
        df["artists"]
        .str.split(r"[;,]")
        .str[0]
        .str.strip()
        .str.strip("'\"[]")
    )

    df["duration_min"] = (df["duration_ms"] / 60_000).round(2)

    required = ["popularity"] + [f for f in AUDIO_FEATURES if f in df.columns]
    df = df.dropna(subset=required)
    df["popularity"] = df["popularity"].astype(int)

    return df


@st.cache_data(show_spinner="Consultando Spotify API...")
def load_spotify_top_artists(market: str = "global", limit_per_genre: int = 10) -> pd.DataFrame:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        st.warning(
            "Credenciales de Spotify no encontradas en .env. Mostrando datos de ejemplo."
        )
        return _sample_artists_data()

    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
    )

    latam_genres = ["reggaeton", "latin pop", "cumbia", "vallenato", "sertanejo", "trap latino"]
    records = []
    for genre in latam_genres:
        results = sp.search(
            q=f"genre:{genre}",
            type="artist",
            limit=limit_per_genre,
            market=market if market != "global" else None,
        )
        for artist in results["artists"]["items"]:
            records.append({
                "artist": artist["name"],
                "genre": genre,
                "followers": artist["followers"]["total"],
                "popularity": artist["popularity"],
            })

    return pd.DataFrame(records)


def _sample_artists_data() -> pd.DataFrame:
    return pd.DataFrame({
        "artist":    ["Bad Bunny", "J Balvin", "Karol G", "Peso Pluma", "Feid",
                      "Maluma", "Anuel AA", "Ozuna", "Rauw Alejandro", "Myke Towers"],
        "genre":     ["reggaeton", "latin pop", "reggaeton", "corridos tumbados", "reggaeton",
                      "latin pop", "trap latino", "reggaeton", "latin pop", "reggaeton"],
        "followers": [48_000_000, 35_000_000, 30_000_000, 22_000_000, 18_000_000,
                      30_000_000, 17_000_000, 28_000_000, 15_000_000, 12_000_000],
        "popularity": [97, 88, 92, 90, 85, 86, 82, 84, 88, 80],
    })


# ---------------------------------------------------------------------------
# Sidebar — filtros globales
# ---------------------------------------------------------------------------

def render_sidebar() -> dict:
    st.sidebar.header("Filtros")

    min_popularity = st.sidebar.slider(
        "Popularidad mínima",
        min_value=0, max_value=100, value=0,
        help="Filtra canciones por debajo de este umbral de popularidad",
    )

    top_n_genres = st.sidebar.slider("Top N géneros a mostrar", 5, 25, 12)

    latam_countries = {
        "Global": None,
        "Colombia": "CO",
        "México": "MX",
        "Argentina": "AR",
        "Chile": "CL",
        "Perú": "PE",
        "Brasil": "BR",
    }
    selected_market = st.sidebar.selectbox("Mercado (API Spotify)", list(latam_countries.keys()))

    return {
        "min_popularity": min_popularity,
        "top_n_genres": top_n_genres,
        "market": latam_countries[selected_market],
        "market_label": selected_market,
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    return df[df["popularity"] >= filters["min_popularity"]].copy()


# ---------------------------------------------------------------------------
# Section 1 — KPI overview
# ---------------------------------------------------------------------------

def section_kpis(df: pd.DataFrame) -> None:
    st.header("Visión general")

    top_track = df.loc[df["popularity"].idxmax()]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Canciones analizadas", f"{len(df):,}")
    col2.metric("Géneros únicos", df["genre"].nunique())
    col3.metric("Popularidad promedio", f"{df['popularity'].mean():.1f}")
    col4.metric(
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
            "track_count": "Nº de tracks",
        },
        template="plotly_dark",
        text=genre_stats.sort_values("avg_popularity")["avg_popularity"].round(1),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=480, coloraxis_colorbar_title="Nº tracks")
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
        x=x_axis,
        y=y_axis,
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
# Section 5 — Top LATAM artists (Spotify API)
# ---------------------------------------------------------------------------

def section_top_artists(artists_df: pd.DataFrame, filters: dict) -> None:
    st.header(f"Top artistas — {filters['market_label']} (Spotify API)")

    fig = px.bar(
        artists_df.sort_values("followers", ascending=False),
        x="artist",
        y="followers",
        color="genre",
        title=f"Artistas por seguidores — {filters['market_label']}",
        labels={"followers": "Seguidores", "artist": "Artista", "genre": "Género"},
        template="plotly_dark",
    )
    fig.update_layout(height=400, xaxis_tickangle=-30)
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
        x="genre",
        y="popularity",
        color="genre",
        category_orders={"genre": genre_order},
        title=f"Distribución de popularidad — Top {filters['top_n_genres']} géneros",
        labels={"popularity": "Popularidad", "genre": "Género"},
        template="plotly_dark",
        points=False,
    )
    fig.update_layout(
        height=430,
        showlegend=False,
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Section 7 — Audio features radar by genre
# ---------------------------------------------------------------------------

def section_radar_by_genre(df: pd.DataFrame, filters: dict) -> None:
    st.header("Perfil de audio features por género")

    available_features = [f for f in AUDIO_FEATURES if f in df.columns and f != "liveness"]
    top_genres = (
        df.groupby("genre")["popularity"]
        .mean()
        .nlargest(6)
        .index.tolist()
    )

    selected_genres = st.multiselect(
        "Géneros a comparar",
        options=df["genre"].unique().tolist(),
        default=top_genres[:5],
        max_selections=8,
    )

    if not selected_genres:
        st.info("Selecciona al menos un género.")
        return

    radar_df = (
        df[df["genre"].isin(selected_genres)]
        .groupby("genre")[available_features]
        .mean()
        .reset_index()
    )

    fig = go.Figure()
    for _, row in radar_df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=row[available_features].values,
            theta=available_features,
            fill="toself",
            name=row["genre"],
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Perfil promedio de audio features por género",
        template="plotly_dark",
        height=480,
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

    artists_df = load_spotify_top_artists(market=filters["market"] or "global")

    # --- Row 1: KPIs
    section_kpis(df)
    st.markdown("---")

    # --- Row 2: Genre ranking + Top artists
    col_left, col_right = st.columns([3, 2])
    with col_left:
        section_genre_ranking(df, filters)
    with col_right:
        section_top_artists(artists_df, filters)

    st.markdown("---")

    # --- Row 3: Scatter features
    section_audio_features(df)

    st.markdown("---")

    # --- Row 4: Correlation + Box plot
    col_corr, col_box = st.columns(2)
    with col_corr:
        section_correlation(df)
    with col_box:
        section_popularity_distribution(df, filters)

    st.markdown("---")

    # --- Row 5: Radar chart
    section_radar_by_genre(df, filters)

    st.markdown("---")
    st.caption("Datos: Spotify Web API · Kaggle Spotify Tracks Dataset · Laura Blanco 2026")


if __name__ == "__main__":
    main()
