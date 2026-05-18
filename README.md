# Spotify Streaming Trends Dashboard

**Autor:** Laura Blanco | **Stack:** Python · Spotipy · Pandas · Plotly · Streamlit
**Demo:** *(URL pública disponible al deployar en Streamlit Cloud)*

Un dashboard interactivo que analiza tendencias de streaming musical usando la Spotify Web API y datos históricos abiertos. Muestra cómo evolucionan géneros, artistas y mercados a lo largo del tiempo, con foco en el mercado LATAM.

---

## Análisis incluidos

| Sección | Descripción |
|---------|-------------|
| Visión general | KPIs globales: total canciones, géneros, popularidad promedio, track #1 |
| Popularidad por género | Bar chart horizontal: top N géneros por popularidad promedio + nº de tracks |
| Audio features vs. popularidad | Scatter interactivo: cualquier par de features, coloreado por popularidad |
| Matriz de correlación | Correlación de Pearson entre todas las audio features y la popularidad |
| Top artistas LATAM | Artistas líderes por seguidores según género (vía Spotify API) |
| Distribución de popularidad | Box plot: spread de popularidad por género (mediana, IQR, outliers) |
| Radar de audio features | Perfil comparativo de features promedio entre géneros seleccionados |

---

## Hallazgos clave

> *Esta sección se completa al finalizar el análisis. Se documentarán 3 hallazgos concretos con visualizaciones de soporte.*

**Hallazgo 1 — Evolución de géneros en LATAM:**
*(placeholder)*

**Hallazgo 2 — Audio features y popularidad:**
*(placeholder)*

**Hallazgo 3 — Insight sorprendente del mercado LATAM:**
*(placeholder)*

---

## Setup local

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/spotify-trends-dashboard.git
cd spotify-trends-dashboard
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar credenciales de Spotify
Crea un archivo `.env` en la raíz del proyecto (nunca lo subas a GitHub):
```
SPOTIFY_CLIENT_ID=tu_client_id_aqui
SPOTIFY_CLIENT_SECRET=tu_client_secret_aqui
```

Para obtener estas credenciales:
1. Ve a [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Crea una nueva app
3. Copia el `Client ID` y `Client Secret`

### 4. Descargar el dataset histórico
- Ve a [Kaggle — Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/spotify-tracks-dataset)
- Descarga el CSV y colócalo en `data/kaggle_tracks.csv`

### 5. Ejecutar el dashboard
```bash
streamlit run app.py
```

---

## Deploy en Streamlit Cloud

1. Haz push del repositorio a GitHub (asegúrate de que `.env` esté en `.gitignore`)
2. Ve a [share.streamlit.io](https://share.streamlit.io) y conecta tu repositorio
3. En la configuración de la app, agrega los secrets:
   ```
   SPOTIFY_CLIENT_ID = "tu_client_id"
   SPOTIFY_CLIENT_SECRET = "tu_client_secret"
   ```
4. Streamlit Cloud generará una URL pública automáticamente

---

## Estructura del proyecto

```
spotify-trends-dashboard/
├── app.py                  # Dashboard principal
├── utils/
│   └── spotify_client.py   # Funciones de consulta a la API
├── data/
│   └── kaggle_tracks.csv   # Dataset histórico (no versionado en git)
├── requirements.txt
├── .env.example            # Template de variables de entorno
├── .gitignore
├── PACE_strategy.md        # Documento de estrategia del proyecto
└── README.md
```

---

## Fuentes de datos

- **Spotify Web API** — datos actuales de artistas, tracks y audio features
- **Kaggle "Spotify Tracks Dataset"** (Maharshi Pandya) — histórico de ~600k canciones con audio features (1921–2020)

---

## Sobre la autora

Laura Blanco — Data Scientist con enfoque en music analytics y el mercado LATAM.

[LinkedIn](https://linkedin.com/in/tu-perfil) · [GitHub](https://github.com/tu-usuario) · [Portfolio completo](https://github.com/tu-usuario)
