# Spotify Streaming Trends Dashboard

🌐 [Read in English](README.md)

**Autor:** Laura Blanco | **Stack:** Python · pylast · Pandas · Plotly · Streamlit
**Demo en vivo:** [spotify-trends-dashboard.streamlit.app](https://spotify-trends-dashboard-2kzwefkozz5grasp5w5yjp.streamlit.app/)

Un dashboard interactivo que analiza tendencias de streaming musical combinando dos fuentes: el Kaggle Spotify Tracks Dataset (~114k canciones con audio features) y la Last.fm API para datos de artistas en tiempo real por país LATAM.

---

## Análisis incluidos

| Sección | Fuente | Descripción |
|---------|--------|-------------|
| Visión general | Kaggle | KPIs: total canciones, géneros, popularidad promedio, track #1 |
| Popularidad por género | Kaggle | Bar chart horizontal: top N géneros por popularidad promedio + nº tracks |
| Audio features vs. popularidad | Kaggle | Scatter interactivo entre cualquier par de features, coloreado por popularidad |
| Matriz de correlación | Kaggle | Correlación de Pearson entre audio features y popularidad |
| Top artistas LATAM | Last.fm API | Artistas más escuchados por país (Colombia, México, Argentina…) |
| Distribución de popularidad | Kaggle | Box plot: spread de popularidad por género (mediana, IQR, outliers) |
| Radar de audio features | Kaggle | Perfil comparativo de features promedio entre géneros seleccionados |

---

## Hallazgos clave

> *Esta sección se completa al finalizar el análisis. Se documentarán 3 hallazgos concretos con visualizaciones de soporte.*

**Hallazgo 1 — Patrones de popularidad por género:**
*(próximamente)*

**Hallazgo 2 — Audio features y popularidad:**
*(próximamente)*

**Hallazgo 3 — Insight sorprendente del mercado LATAM:**
*(próximamente)*

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
3. Completa el formulario (nombre de app: cualquiera, ej. `music-portfolio`)
4. Copia el API Key generado

### 4. Dataset
El dataset ya está incluido en el repositorio en `data/kaggle_tracks.csv`.

Fuente: [Spotify Tracks Dataset — Audio Features](https://www.kaggle.com/datasets/saichaitanyareddyai/spotify-tracks-dataset-audio-features) en Kaggle.

### 5. Ejecutar el dashboard
```bash
streamlit run app.py
```

---

## Deploy en Streamlit Cloud

1. Haz push del repositorio a GitHub (`.env` está excluido via `.gitignore`)
2. Ve a [share.streamlit.io](https://share.streamlit.io) y conecta tu repositorio
3. En **Settings → Secrets**, agrega:
   ```toml
   LASTFM_API_KEY = "tu_api_key_aqui"
   ```
4. Streamlit Cloud generará una URL pública automáticamente

---

## Estructura del proyecto

```
spotify-trends-dashboard/
├── app.py                  # Dashboard principal (Streamlit)
├── data/
│   └── kaggle_tracks.csv   # Dataset histórico (~18MB, versionado en git)
├── utils/                  # Módulos auxiliares (en desarrollo)
├── requirements.txt
├── .env.example            # Template de variables de entorno
├── .gitignore
├── PACE_strategy.md        # Documento de estrategia del proyecto
├── README.md               # Versión en inglés (default)
└── README.es.md            # Este archivo
```

---

## Fuentes de datos

- **Last.fm API** (via pylast) — top artistas por país LATAM en tiempo real, oyentes mensuales, géneros
- **Kaggle Spotify Tracks Dataset** — ~114k canciones con audio features completas (danceability, energy, valence, tempo, etc.)

---

## Sobre la autora

Laura Blanco — Data Scientist con enfoque en music analytics y el mercado LATAM.

[LinkedIn](https://linkedin.com/in/tu-perfil) · [GitHub](https://github.com/tu-usuario) · [Portfolio completo](https://github.com/tu-usuario)
