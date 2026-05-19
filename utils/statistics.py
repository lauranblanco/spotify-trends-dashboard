"""
utils/statistics.py
Secciones visuales del dashboard, organizadas por pestaña.

Tab 1 — Audio DNA (Kaggle, estático):
  section_audio_scatter()         → scatter entre cualquier par de audio features
  section_correlation_audio()     → heatmap de correlación solo entre audio features
  section_radar_by_genre()        → radar comparativo de audio features por género

Tab 2 — Market Pulse (Last.fm, en vivo):
  section_kpis_live()             → KPIs de audiencia actual
  section_genre_popularity_live() → share de oyentes por género (índice de popularidad)
  section_genre_distribution()    → treemap de distribución de audiencia por género
  section_top_artists_live()      → top artistas por share de popularidad
  section_top_tracks_live()       → top tracks por país en tiempo real
  section_multi_country_heatmap() → presencia de artistas en múltiples países LATAM
  section_cross_correlation()     → correlación entre audio features y popularidad real
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_load import AUDIO_FEATURES, compute_genre_index


# ===========================================================================
# TAB 1 — Audio DNA (Kaggle, sin popularidad)
# ===========================================================================

def section_audio_scatter(df: pd.DataFrame) -> None:
    """Scatter entre cualquier par de audio features, coloreado por género."""
    st.header("Relación entre audio features")

    available = [f for f in AUDIO_FEATURES if f in df.columns]
    col_x, col_y = st.columns(2)
    x_axis = col_x.selectbox("Eje X", available, index=0, key="scatter_x")
    y_axis = col_y.selectbox("Eje Y", available, index=1, key="scatter_y")

    sample = df.sample(min(4000, len(df)), random_state=42)

    fig = px.scatter(
        sample,
        x=x_axis, y=y_axis,
        color="genre",
        opacity=0.55,
        title=f"{x_axis.capitalize()} vs. {y_axis.capitalize()} — por género",
        labels={"genre": "Género"},
        template="plotly_dark",
        hover_data=["track_name", "primary_artist", "genre"],
    )
    fig.update_layout(height=500, legend_title="Género")
    st.plotly_chart(fig, use_container_width=True)


def section_correlation_audio(df: pd.DataFrame) -> None:
    """Heatmap de correlación entre audio features (sin incluir popularidad)."""
    st.header("Correlación entre audio features")

    cols = [f for f in AUDIO_FEATURES if f in df.columns]
    corr = df[cols].corr()

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale="RdBu",
        zmid=0,
        text=corr.round(2).values,
        texttemplate="%{text}",
        showscale=True,
    ))
    fig.update_layout(
        title="¿Qué features van juntos?",
        template="plotly_dark",
        height=470,
    )
    st.plotly_chart(fig, use_container_width=True)


def section_radar_by_genre(df: pd.DataFrame) -> None:
    """Radar comparativo del perfil promedio de audio features por género."""
    st.header("Perfil sonoro por género")

    available = [f for f in AUDIO_FEATURES if f in df.columns and f != "liveness"]

    # Default: géneros más frecuentes por número de tracks (sin usar popularidad)
    default_genres = df["genre"].value_counts().head(5).index.tolist()

    selected = st.multiselect(
        "Géneros a comparar",
        options=sorted(df["genre"].unique().tolist()),
        default=default_genres,
        max_selections=8,
        key="radar_genres",
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
        title="¿Cómo suena cada género en promedio?",
        template="plotly_dark",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# TAB 2 — Market Pulse (Last.fm, en vivo)
# ===========================================================================

def section_kpis_live(
    artists_df: pd.DataFrame,
    tracks_df: pd.DataFrame,
    filters: dict,
) -> None:
    """KPIs de audiencia en tiempo real desde Last.fm."""
    st.header(f"Pulso del mercado — {filters['country_label']} ahora mismo")

    genre_df = compute_genre_index(artists_df)
    top_genre     = genre_df.iloc[0]["genre"] if not genre_df.empty else "—"
    top_genre_pct = genre_df.iloc[0]["popularity_pct"] if not genre_df.empty else 0

    top_artist_row = artists_df.loc[artists_df["listeners"].idxmax()] if not artists_df.empty else None
    top_track_row  = tracks_df.loc[tracks_df["listeners"].idxmax()]   if not tracks_df.empty else None
    total_listeners = artists_df["listeners"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Oyentes totales (top artistas)",
        f"{total_listeners / 1_000_000:.1f}M",
        help="Suma de oyentes mensuales de todos los artistas en el top local",
    )
    c2.metric(
        "Género dominante",
        top_genre,
        delta=f"{top_genre_pct:.1f}% del mercado",
        delta_color="off",
    )
    c3.metric(
        "Artista #1",
        top_artist_row["artist"] if top_artist_row is not None else "—",
        delta=(
            f"{top_artist_row['listeners'] / 1_000_000:.1f}M oyentes"
            if top_artist_row is not None else ""
        ),
        delta_color="off",
    )
    c4.metric(
        "Track #1",
        (
            f"{top_track_row['track']} — {top_track_row['artist']}"
            if top_track_row is not None else "—"
        ),
        help="Canción más escuchada según Last.fm en este país ahora",
    )


def section_genre_popularity_live(
    artists_df: pd.DataFrame,
    filters: dict,
) -> None:
    """Índice de popularidad por género: share de oyentes mensuales."""
    st.header("Índice de popularidad por género")
    st.caption("% de oyentes mensuales totales que escuchan artistas de ese género")

    genre_df = compute_genre_index(artists_df)

    fig = px.bar(
        genre_df.sort_values("popularity_pct"),
        x="popularity_pct",
        y="genre",
        orientation="h",
        color="popularity_pct",
        color_continuous_scale="Teal",
        title=f"Share de audiencia por género — {filters['country_label']}",
        labels={"popularity_pct": "% del total de oyentes", "genre": "Género"},
        template="plotly_dark",
        text=genre_df.sort_values("popularity_pct")["popularity_pct"].apply(
            lambda x: f"{x:.1f}%"
        ),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=420, showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)


def section_genre_distribution(
    artists_df: pd.DataFrame,
    filters: dict,
) -> None:
    """Treemap de distribución de audiencia por género."""
    st.header("Distribución de audiencia")

    genre_df = compute_genre_index(artists_df)

    fig = px.treemap(
        genre_df,
        path=["genre"],
        values="listeners",
        color="popularity_pct",
        color_continuous_scale="Teal",
        title=f"Distribución de oyentes por género — {filters['country_label']}",
        custom_data=["popularity_pct"],
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[0]:.1f}%",
        textfont_size=13,
    )
    fig.update_layout(template="plotly_dark", height=420, coloraxis_colorbar_title="%")
    st.plotly_chart(fig, use_container_width=True)


def section_top_artists_live(
    artists_df: pd.DataFrame,
    filters: dict,
) -> None:
    """Top artistas con índice de popularidad."""
    st.header(f"Top artistas — {filters['country_label']}")

    df_plot = artists_df.sort_values("popularity_pct", ascending=True).tail(15)

    fig = px.bar(
        df_plot,
        x="popularity_pct",
        y="artist",
        orientation="h",
        color="genre",
        title=f"Share de audiencia por artista — {filters['country_label']}",
        labels={"popularity_pct": "% del total de oyentes", "artist": "Artista", "genre": "Género"},
        template="plotly_dark",
        text=df_plot["popularity_pct"].apply(lambda x: f"{x:.2f}%"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)


def section_top_tracks_live(
    tracks_df: pd.DataFrame,
    filters: dict,
) -> None:
    """Top tracks por país en tiempo real."""
    st.header(f"Top tracks — {filters['country_label']}")

    df_plot = tracks_df.sort_values("popularity_pct", ascending=True).tail(15)

    fig = px.bar(
        df_plot,
        x="popularity_pct",
        y="track",
        orientation="h",
        color="artist",
        title=f"Canciones por share de audiencia — {filters['country_label']}",
        labels={"popularity_pct": "% del total de oyentes", "track": "Canción", "artist": "Artista"},
        template="plotly_dark",
        text=df_plot["popularity_pct"].apply(lambda x: f"{x:.2f}%"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)


def section_multi_country_heatmap(multi_df: pd.DataFrame) -> None:
    """
    Heatmap de presencia de artistas en múltiples países LATAM.
    Muestra la posición en el ranking local (1 = top). Solo artistas en 2+ países.
    """
    st.header("¿Qué artistas rompen fronteras en LATAM?")
    st.caption("Posición en el top local de cada país · Solo artistas presentes en 2+ países")

    pivot = multi_df.pivot_table(
        index="artist", columns="country", values="rank", aggfunc="min"
    ).fillna(0).astype(int)

    countries_count = (pivot > 0).sum(axis=1)
    multi_artists = pivot[countries_count >= 2]

    if multi_artists.empty:
        st.info("No hay artistas presentes en múltiples países con los datos actuales.")
        return

    # Ordenar por número de países donde aparecen (más países primero)
    multi_artists = multi_artists.loc[
        countries_count[countries_count >= 2].sort_values(ascending=False).index
    ]

    text_values = multi_artists.replace(0, "").astype(str)

    fig = go.Figure(go.Heatmap(
        z=multi_artists.values,
        x=multi_artists.columns.tolist(),
        y=multi_artists.index.tolist(),
        colorscale="Teal",
        reversescale=True,
        showscale=False,
        text=text_values.values,
        texttemplate="%{text}",
        zmin=0,
        zmax=multi_artists.values.max(),
    ))
    fig.update_layout(
        title="Posición en top local (blanco = no aparece en ese país)",
        template="plotly_dark",
        height=max(380, len(multi_artists) * 30),
        xaxis_title="País",
        yaxis_title="Artista",
    )
    st.plotly_chart(fig, use_container_width=True)


def section_cross_correlation(
    artists_df: pd.DataFrame,
    kaggle_df: pd.DataFrame,
) -> None:
    """
    Correlación cruzada: índice de popularidad Last.fm por género
    vs. audio features promedio de ese género en Kaggle.

    Responde: ¿qué características sonoras tienen los géneros
    con más audiencia en LATAM ahora mismo?
    """
    st.header("¿Qué audio features definen a los géneros más populares?")
    st.caption(
        "Cruza el índice de popularidad Last.fm (audiencia real) "
        "con las audio features promedio por género de Kaggle"
    )

    genre_index = compute_genre_index(artists_df)[["genre", "popularity_pct"]]

    available = [f for f in AUDIO_FEATURES if f in kaggle_df.columns]
    genre_audio = (
        kaggle_df.groupby("genre")[available]
        .mean()
        .reset_index()
    )

    cross = genre_index.merge(genre_audio, on="genre", how="inner")

    if len(cross) < 3:
        st.info(
            "No hay suficientes géneros en común entre Last.fm y Kaggle "
            "para este país. Prueba con otro país en el sidebar."
        )
        return

    corr_series = (
        cross[["popularity_pct"] + available]
        .corr()["popularity_pct"]
        .drop("popularity_pct")
    )
    corr_df = (
        corr_series
        .reset_index()
        .rename(columns={"index": "feature", "popularity_pct": "correlation"})
        .assign(abs_corr=lambda x: x["correlation"].abs())
        .sort_values("correlation", ascending=True)
    )

    col_bar, col_scatter = st.columns([2, 3])

    with col_bar:
        fig_bar = px.bar(
            corr_df,
            x="correlation",
            y="feature",
            orientation="h",
            color="correlation",
            color_continuous_scale="RdBu",
            range_color=[-1, 1],
            title="Correlación de cada feature con la popularidad real",
            labels={"correlation": "Pearson r", "feature": "Audio feature"},
            template="plotly_dark",
            text=corr_df["correlation"].round(2),
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(height=400, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_scatter:
        top_feature = corr_df.loc[corr_df["abs_corr"].idxmax(), "feature"]
        fig_scatter = px.scatter(
            cross,
            x=top_feature,
            y="popularity_pct",
            text="genre",
            title=f"Popularidad vs. {top_feature} — un punto = un género",
            labels={
                top_feature: top_feature.capitalize(),
                "popularity_pct": "% de audiencia (Last.fm)",
            },
            template="plotly_dark",
            trendline="ols",
            trendline_color_override="#00b4d8",
        )
        fig_scatter.update_traces(textposition="top center", marker_size=11)
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
