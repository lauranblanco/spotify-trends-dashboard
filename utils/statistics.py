import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.data_load import AUDIO_FEATURES


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

    df_plot = artists_df.sort_values("listeners", ascending=True).tail(15)

    fig = px.bar(
        df_plot,
        x="listeners",
        y="artist",
        orientation="h",
        color="genre",
        title=f"Top artistas por oyentes mensuales — {filters['country_label']}",
        labels={"listeners": "Oyentes mensuales", "artist": "Artista", "genre": "Género"},
        template="plotly_dark",
        text=df_plot["listeners"].apply(
            lambda x: f"{x/1_000_000:.1f}M" if x >= 1_000_000 else f"{x:,}"
        ),
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

def section_radar_by_genre(df: pd.DataFrame) -> None:
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

