"""
utils/data_load.py
Funciones de carga de datos, transformaciones y constantes compartidas.

Fuentes:
  - load_kaggle_data()            → dataset estático Kaggle (~114k tracks)
  - load_lastfm_top_artists()     → top artistas por país (live, TTL 1h)
  - load_lastfm_geo_tracks()      → top tracks por país (live, TTL 1h)
  - load_lastfm_multi_country()   → top artistas en los 8 países LATAM (live, TTL 3h)

Índices de popularidad:
  - compute_popularity_index()    → añade columna popularity_pct a un df con 'listeners'
  - compute_genre_index()         → agrega artistas por género con su share de oyentes
"""

import os
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

AUDIO_FEATURES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "speechiness",
    "instrumentalness",
    "liveness",
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
# Kaggle — dataset estático
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Cargando dataset...")
def load_kaggle_data(path: str = "data/kaggle_tracks.csv") -> pd.DataFrame:
    """
    Carga y normaliza el Kaggle Spotify Tracks Dataset.
    Columnas esperadas: track_id, artists, album_name, track_name, popularity,
    duration_ms, explicit, danceability, energy, key, loudness, mode,
    speechiness, acousticness, instrumentalness, liveness, valence, tempo,
    time_signature, track_genre
    """
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
# Índices de popularidad
# ---------------------------------------------------------------------------

def compute_popularity_index(df: pd.DataFrame, listeners_col: str = "listeners") -> pd.DataFrame:
    """
    Añade 'popularity_pct': porcentaje que representa cada fila
    sobre el total de oyentes del DataFrame.

    Ejemplo: un artista con 2M oyentes sobre 10M totales → popularity_pct = 20.0
    """
    df = df.copy()
    total = df[listeners_col].sum()
    df["popularity_pct"] = (
        (df[listeners_col] / total * 100).round(2) if total > 0 else 0.0
    )
    return df


def compute_genre_index(artists_df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega artistas por género y calcula el share de oyentes por género.
    Requiere columnas: genre, listeners.
    Devuelve: genre, listeners, popularity_pct ordenado desc.
    """
    genre_df = (
        artists_df.groupby("genre", as_index=False)["listeners"]
        .sum()
        .sort_values("listeners", ascending=False)
    )
    total = genre_df["listeners"].sum()
    genre_df["popularity_pct"] = (
        (genre_df["listeners"] / total * 100).round(2) if total > 0 else 0.0
    )
    return genre_df


# ---------------------------------------------------------------------------
# Last.fm — top artistas por país
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Consultando Last.fm — artistas...", ttl=3600)
def load_lastfm_top_artists(country_en: str, limit: int = 20) -> pd.DataFrame:
    """
    Top artistas por país con oyentes mensuales y género (tag principal).
    Requiere LASTFM_API_KEY en .env o Streamlit secrets.
    """
    api_key = os.getenv("LASTFM_API_KEY") or st.secrets.get("LASTFM_API_KEY", None)

    if not api_key:
        st.warning("API key de Last.fm no encontrada. Mostrando datos de ejemplo.")
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
                listeners = int(item.weight) if item.weight else 0
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


# ---------------------------------------------------------------------------
# Last.fm — top tracks por país
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Consultando Last.fm — tracks...", ttl=3600)
def load_lastfm_geo_tracks(country_en: str, limit: int = 20) -> pd.DataFrame:
    """
    Top tracks por país con oyentes.
    Devuelve: track, artist, listeners, country, popularity_pct.
    """
    api_key = os.getenv("LASTFM_API_KEY") or st.secrets.get("LASTFM_API_KEY", None)

    if not api_key:
        return _sample_tracks_data()

    try:
        import pylast
        network = pylast.LastFMNetwork(api_key=api_key)
        top_items = network.get_geo_top_tracks(country=country_en, limit=limit)

        records = []
        for item in top_items:
            track = item.item
            listeners = int(item.weight) if item.weight else 0
            records.append({
                "track":     track.get_name(),
                "artist":    track.get_artist().get_name(),
                "listeners": listeners,
                "country":   country_en,
            })

        df = pd.DataFrame(records)
        return compute_popularity_index(df) if not df.empty else df

    except Exception as exc:
        st.warning(f"Error consultando Last.fm tracks: {exc}. Mostrando datos de ejemplo.")
        return _sample_tracks_data()


# ---------------------------------------------------------------------------
# Last.fm — comparativa multi-país LATAM
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Cargando comparativa multi-país LATAM...", ttl=3600 * 3)
def load_lastfm_multi_country(limit: int = 15) -> pd.DataFrame:
    """
    Obtiene los top artistas de todos los países LATAM en llamadas encadenadas.
    Resultado: artist, country, rank — usado para el heatmap de presencia cruzada.
    TTL = 3 horas (son ~11 llamadas a la API).
    """
    api_key = os.getenv("LASTFM_API_KEY") or st.secrets.get("LASTFM_API_KEY", None)

    if not api_key:
        return _sample_multi_country_data()

    try:
        import pylast
        network = pylast.LastFMNetwork(api_key=api_key)
        records = []

        for country_label, country_en in LATAM_COUNTRIES.items():
            try:
                top_items = network.get_geo_top_artists(country=country_en, limit=limit)
                for rank, item in enumerate(top_items, 1):
                    records.append({
                        "artist":  item.item.get_name(),
                        "country": country_label,
                        "rank":    rank,
                    })
            except Exception:
                continue

        return pd.DataFrame(records)

    except Exception as exc:
        st.warning(f"Error en consulta multi-país: {exc}. Mostrando datos de ejemplo.")
        return _sample_multi_country_data()


# ---------------------------------------------------------------------------
# Datos de ejemplo (fallback sin API key)
# ---------------------------------------------------------------------------

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


def _sample_tracks_data() -> pd.DataFrame:
    df = pd.DataFrame({
        "track":    ["Tití Me Preguntó", "PROVENZA", "Ojitos Lindos", "La Bachata",
                     "Bzrp Music Sessions #53", "Ella Baila Sola",
                     "ASTRONOMÍA", "AMARGURA", "Yonaguni", "Efecto"],
        "artist":   ["Bad Bunny", "Karol G", "Bad Bunny", "Manuel Turizo",
                     "Bizarrap", "Peso Pluma", "Rauw Alejandro",
                     "Feid", "Bad Bunny", "Rauw Alejandro"],
        "listeners": [8_200_000, 6_100_000, 5_900_000, 5_400_000, 7_800_000,
                      4_300_000, 3_800_000, 3_200_000, 4_100_000, 3_500_000],
        "country":  ["Colombia"] * 10,
    })
    return compute_popularity_index(df)


def _sample_multi_country_data() -> pd.DataFrame:
    artists = ["Bad Bunny", "Karol G", "J Balvin", "Maluma", "Feid",
               "Peso Pluma", "Rauw Alejandro", "Bizarrap", "Ozuna", "Anuel AA"]
    countries = list(LATAM_COUNTRIES.keys())[:8]
    records = [
        {"artist": artist, "country": country, "rank": rank}
        for country in countries
        for rank, artist in enumerate(artists[:8], 1)
    ]
    return pd.DataFrame(records)
