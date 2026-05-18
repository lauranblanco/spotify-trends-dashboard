# Spotify Streaming Trends Dashboard

**Autor:** Laura Blanco | **Stack:** Python · pylast · Pandas · Plotly · Streamlit |
**Demo:** *https://spotify-trends-dashboard-2kzwefkozz5grasp5w5yjp.streamlit.app/*

Un dashboard interactivo que analiza tendencias de streaming musical combinando dos fuentes: el Kaggle Spotify Tracks Dataset (~600k canciones con audio features) y la Last.fm API para datos de artistas en tiempo real por país LATAM.

---

## Análisis incluidos

| Sección | Fuente | Descripción |
|---------|--------|-------------|
| Visión general | Kaggle | KPIs: total canciones, géneros, popularidad promedio, track #1 |
| Popularidad por género | Kaggle | Bar chart: top N géneros por popularidad promedio + nº de tracks |
| Audio features vs. popularidad | Kaggle | Scatter interactivo entre cualquier par de features |
| Matriz de correlación | Kaggle | Correlación de Pearson entre audio features y popularidad |
| Top artistas LATAM | Last.fm API | Artistas más escuchados por país (Colombia, México, Argentina…) |
| Distribución de popularidad | Kaggle | Box plot: spread de popularidad por género (mediana, IQR, outliers) |
| Radar de audio features | Kaggle | Perfil comparativo de features promedio entre géneros |

---

## Hallazgos clave

> *Esta sección se completa al finalizar el análisis. Se documentarán 3 hallazgos concretos con visualizaciones de soporte.*

**Hallazgo 1 — Géneros y popularidad en el dataset:**
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

### 3. Configurar API key de Last.fm
Crea un archivo `.env` en la raíz del proyecto (nunca lo subas a GitHub):
```
LASTFM_API_KEY=tu_api_key_aqui
```

Para obtener la API key (es gratuita):
1. Crea una cuenta en [last.fm](https://www.last.fm/join)
2. Ve a [last.fm/api/account/create](https://www.last.fm/api/account/create)
3. Completa el formulario (nombre de app: cualquiera, ej. "music-portfolio")
4. Copia el `API Key` generado

### 4. Descargar el dataset
- Busca en Kaggle: **"Spotify Tracks Dataset"** (https://www.kaggle.com/datasets/saichaitanyareddyai/spotify-tracks-dataset-audio-features) y descarga el CSV
- Colócalo en `data/kaggle_tracks.csv`

### 5. Ejecutar el dashboard
```bash
streamlit run app.py
```

---

## Deploy en Streamlit Cloud

1. Haz push del repositorio a GitHub (`.env` y el CSV están en `.gitignore`)
2. Ve a [share.streamlit.io](https://share.streamlit.io) y conecta tu repositorio
3. En **Settings → Secrets**, agrega:
   ```toml
   LASTFM_API_KEY = "tu_api_key_aqui"
   ```
4. El dashboard con el CSV grande requiere subirlo a un lugar accesible o usar un subset. Ver nota abajo.

> **Nota sobre el dataset en Streamlit Cloud:** Si el CSV de Kaggle supera los 100MB y no puede subirse directamente a GitHub. Opciones: (1) subir un subset de 50k filas al repo, (2) hospedar el CSV en Google Drive y descargarlo al iniciar la app.

---

## Estructura del proyecto

```
spotify-trends-dashboard/
├── app.py                  # Dashboard principal (Streamlit)
├── data/
│   └── kaggle_tracks.csv   # Dataset histórico (no versionado en git)
├── utils/                  # Módulos auxiliares (en desarrollo)
├── requirements.txt
├── .env.example            # Template de variables de entorno
├── .gitignore
├── PACE_strategy.md        # Documento de estrategia del proyecto
└── README.md
```

---

## Fuentes de datos

- **Last.fm API** (via pylast) — top artistas por país LATAM en tiempo real, oyentes mensuales, géneros
- **Kaggle Spotify Tracks Dataset** — ~600k canciones con audio features completas (danceability, energy, valence, etc.) https://*www.kaggle.com/datasets/saichaitanyareddyai/spotify-tracks-dataset-audio-features*

---

## Sobre la autora

Laura Blanco — Data Scientist con enfoque en music analytics y el mercado LATAM.

[LinkedIn](https://linkedin.com/in/tu-perfil) · [GitHub](https://github.com/tu-usuario) · [Portfolio completo](https://github.com/tu-usuario)
