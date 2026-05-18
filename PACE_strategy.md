# PACE Strategy — Spotify Streaming Trends Dashboard
**Proyecto:** Music Analytics Portfolio · Proyecto 1 de 5
**Responsable:** Laura Blanco
**Fecha de inicio:** Mayo 2026
**Duración estimada:** 2–3 semanas

---

## P — Plan

### Objetivo de negocio
Demostrar capacidad de analizar el mercado musical desde datos reales de streaming, usando la misma terminología y métricas que usan equipos de analytics en distribuidoras, sellos y plataformas de streaming.

### Audiencia objetivo del dashboard
- Recruiters técnicos en empresas de music tech (distribuidoras indie, startups, Spotify, Chartmetric)
- Equipos de A&R o marketing digital evaluando candidatos analíticos
- Peers de la industria que pueden compartir o referenciar el trabajo

### Preguntas de negocio a responder
1. ¿Qué géneros han ganado más popularidad en LATAM en los últimos 5 años vs. el mercado global?
2. ¿Existe correlación entre las audio features de una canción (energy, danceability, valence) y su popularidad?
3. ¿Qué artistas emergentes muestran mayor crecimiento en países LATAM clave (CO, MX, AR, CL, PE)?
4. ¿Hay patrones estacionales en los lanzamientos musicales exitosos?

### Stakeholders del proyecto
| Rol | Persona | Interés |
|-----|---------|---------|
| Dueña del proyecto | Laura Blanco | Completar el dashboard y publicarlo |
| Audiencia final | Recruiters/industria | Ver capacidades analíticas |

### Riesgos identificados
| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| Rate limits de Spotify API | Media | Cachear llamadas localmente con JSON/CSV |
| Datos históricos incompletos por región | Alta | Complementar con Kaggle dataset (600k canciones) |
| Streamlit Cloud limits de memoria | Baja | Pre-procesar datos en scripts separados, cargar CSVs limpios |

---

## A — Analyze

### Fuentes de datos
| Fuente | Tipo | Uso |
|--------|------|-----|
| Spotify Web API (via Spotipy) | API REST | Datos actuales: artistas, tracks, audio features |
| Kaggle "Spotify Tracks Dataset" | CSV histórico | ~600k canciones con features 1921–2020 |
| Kaggle "Spotify Charts" | CSV | Top 200 semanal por país |

### Variables clave
**Audio features (Spotify API):**
- `danceability` — qué tan bailable es la canción (0–1)
- `energy` — intensidad y actividad percibida (0–1)
- `valence` — positividad musical (0–1)
- `tempo` — BPM
- `acousticness`, `instrumentalness`, `speechiness`

**Métricas de popularidad:**
- `popularity` — score 0–100 calculado por Spotify
- `followers` — seguidores del artista
- Posición en charts semanales

### Metodología de análisis
1. **EDA inicial:** Distribución de audio features por género, outliers, missing values
2. **Análisis temporal:** Evolución de popularidad de géneros usando el histórico de Kaggle
3. **Correlaciones:** Heatmap de Pearson entre audio features y popularity
4. **Segmentación regional:** Filtrar charts por mercado (global vs. LATAM)
5. **Artistas emergentes:** Identificar artistas con mayor delta de followers en 12 meses

### Plan de limpieza de datos
- Estandarizar nombres de géneros (Spotify usa géneros anidados y granulares)
- Eliminar duplicados por track_id
- Tratar valores nulos en audio features (< 2% del dataset esperado)
- Normalizar fechas a formato YYYY-MM-DD

---

## C — Construct

### Arquitectura del proyecto
```
spotify-trends-dashboard/
├── app.py                  # App principal Streamlit
├── utils/
│   └── spotify_client.py   # Wrapper Spotipy + funciones de consulta
├── data/
│   ├── kaggle_tracks.csv   # Dataset histórico (no subir a GitHub si >100MB)
│   └── cached_api/         # JSONs cacheados de la API
├── notebooks/
│   └── 01_eda.ipynb        # Exploración inicial
├── requirements.txt
├── .env.example            # Template de credenciales (sin valores reales)
├── README.md
└── PACE_strategy.md
```

### Stack tecnológico
| Componente | Tecnología | Justificación |
|-----------|-----------|--------------|
| Interface | Streamlit | Deploy gratuito, rápido de construir |
| API wrapper | Spotipy | Abstrae OAuth y paginación de Spotify |
| Datos | Pandas | Manipulación estándar |
| Visualizaciones | Plotly Express | Interactividad nativa en Streamlit |
| Deployment | Streamlit Cloud | URL pública gratuita |
| Credenciales | python-dotenv | .env local, secrets en Streamlit Cloud |

### Secciones del dashboard (en orden)
1. **Visión general** — KPIs globales: total tracks analizados, géneros cubiertos, rango de fechas
2. **Evolución de géneros** — Line chart interactivo: popularidad promedio por género/año con selector
3. **Mapa de audio features** — Scatter plot: danceability vs. energy, coloreado por popularidad
4. **Correlación features × popularidad** — Heatmap de correlaciones
5. **Top emergentes LATAM** — Tabla filtrable: artistas con mayor crecimiento por país
6. **Heatmap de lanzamientos** — Calendario de actividad: cuántos hits salen por mes

### Milestones de construcción
| Semana | Entregable |
|--------|-----------|
| 1 | Setup: credenciales Spotify, descarga Kaggle dataset, EDA básico en notebook |
| 1–2 | Módulo `spotify_client.py` funcional + primeras 2 secciones del dashboard |
| 2–3 | Secciones 3–6 completas + README narrativo + deploy en Streamlit Cloud |

---

## E — Execute

### Criterios de éxito (KPIs)
- [ ] Dashboard deployado en Streamlit Cloud con URL pública
- [ ] Al menos 4 secciones de análisis funcionales
- [ ] README con narrativa de 3 hallazgos clave
- [ ] 1 insight sorprendente sobre el mercado LATAM documentado
- [ ] Código limpio en GitHub con commits descriptivos

### Plan de comunicación post-lanzamiento
1. **GitHub:** Repo público con README visual (GIF del dashboard)
2. **LinkedIn:** Post con 1 captura + 3 bullets de hallazgos + link al dashboard
3. **CV:** Actualizar sección "Music Analytics Portfolio" con URL

### Métricas de seguimiento
- Stars/forks del repositorio en GitHub
- Views del post de LinkedIn (objetivo: >500 en primera semana)
- Conversaciones generadas con recruiters a partir del post

### Próximos pasos inmediatos
1. Crear cuenta en [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) y obtener `CLIENT_ID` y `CLIENT_SECRET`
2. Descargar dataset desde Kaggle: buscar "Spotify Tracks Dataset" (Maharshi Pandya)
3. Instalar dependencias: `pip install spotipy pandas plotly streamlit python-dotenv`
4. Ejecutar el script `app.py` en modo local y verificar que carga datos correctamente

---

*Documento generado bajo el Plan de Portafolio Music Analytics — Laura Blanco, Mayo 2026*
