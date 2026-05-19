# Spotify Streaming Trends Dashboard

🌐 [Read in English](README.md)

**Autor:** Laura Blanco | **Stack:** Python · pylast · Pandas · Plotly · Streamlit · statsmodels
**Demo en vivo:** [spotify-trends-dashboard.streamlit.app](https://spotify-trends-dashboard-2kzwefkozz5grasp5w5yjp.streamlit.app/)

Un dashboard interactivo que combina dos perspectivas complementarias sobre la música: la **estructura sonora** de las canciones (audio features de un dataset estático de Kaggle) y el **comportamiento real de la audiencia** por país (datos en vivo de la API de Last.fm). El dashboard está organizado en dos pestañas con metodologías claramente separadas.

---

## Estructura del dashboard

### 🎵 Pestaña 1 — Audio DNA
*Fuente: Kaggle Spotify Tracks Dataset · Snapshot estático (~2023)*

| Sección | Descripción |
|---------|-------------|
| Relación entre features | Scatter entre cualquier par de audio features, coloreado por género |
| Correlación de features | Heatmap de Pearson entre todas las audio features |
| Perfil sonoro por género | Radar comparativo de audio features promedio entre géneros seleccionados |

### 📊 Pestaña 2 — Market Pulse
*Fuente: Last.fm API · Datos en vivo, se refresca cada hora*

| Sección | Descripción |
|---------|-------------|
| KPIs en vivo | Oyentes totales, género dominante, artista #1 y track #1 en el país seleccionado |
| Índice de popularidad por género | Share de audiencia (%) por género |
| Distribución de audiencia | Treemap del share de cada género sobre el total de oyentes |
| Top artistas | Artistas ordenados por su % del total de oyentes |
| Top tracks | Canciones más escuchadas con su share de audiencia |
| Heatmap multi-país | Qué artistas aparecen en el top de múltiples países LATAM |
| Audio features × Popularidad | Correlación cruzada: ¿los géneros con más energy atraen más audiencia? |

---

## Metodología

### Fuentes de datos y actualización

| Fuente | Período | Actualización |
|--------|---------|---------------|
| Kaggle Spotify Tracks Dataset | Snapshot ~2023 | Estático — solo cambia si se reemplaza el CSV manualmente |
| Last.fm API — top artistas por país | Actualidad | En vivo — se refresca cada hora |
| Last.fm API — top tracks por país | Actualidad | En vivo — se refresca cada hora |
| Last.fm API — comparativa multi-país | Actualidad | En vivo — se refresca cada 3 horas |

### Índice de popularidad

Los conteos brutos de oyentes son difíciles de comparar entre países y momentos en el tiempo (un artista top en Colombia puede tener 5M oyentes, mientras que uno en Uruguay tiene 300K). Para hacer la métrica significativa y comparable, todos los datos de audiencia se normalizan a un **porcentaje del mercado observado**:

```
popularity_pct = (oyentes_entidad / total_oyentes) × 100
```

Aplicado en tres niveles:

| Nivel | Numerador | Denominador |
|-------|-----------|-------------|
| **Artista** | Oyentes mensuales de ese artista | Suma de oyentes de todos los artistas top en el país |
| **Género** | Suma de oyentes de los artistas etiquetados con ese género | Total de oyentes entre todos los artistas |
| **Track** | Oyentes de esa canción | Suma de oyentes de todos los tracks top en el país |

Un género con `popularity_pct = 35%` significa que 35 de cada 100 sesiones de escucha entre el top de ese país corresponden a artistas de ese género.

### Análisis cruzado entre fuentes

La última sección de la Pestaña 2 cruza ambos datasets: toma el **índice de popularidad Last.fm por género** (en vivo) y lo une con las **audio features promedio por género** de Kaggle (estático). El resultado responde: *¿qué características sonoras se correlacionan con el share de audiencia real en LATAM ahora mismo?*

Como el índice de Last.fm se refresca cada hora, esta correlación evoluciona con el tiempo a medida que cambian las tendencias de escucha — es la sección más dinámica del dashboard.

---

## Cómo interpretar los resultados

### 🎵 Pestaña Audio DNA

**Relación entre features (scatter)**
Cada punto es una canción. Si los puntos del mismo color (género) se agrupan, ese género tiene una identidad sonora consistente. Puntos dispersos indican que el género es sonicamente diverso. Busca géneros que ocupan esquinas únicas del gráfico — esos son los más distintos sonicamente.

**Correlación de features (heatmap)**
- Valores cercanos a **+1**: los features tienden a aparecer juntos (ej. alta energy = alta loudness)
- Valores cercanos a **−1**: los features son inversamente relacionados (ej. más acousticness = menos energy)
- Valores cercanos a **0**: no hay relación lineal entre los dos features

Consejo: `valence` (positividad musical) frecuentemente muestra correlaciones sorpresivas — revisa si las canciones más "felices" también son más bailables en el dataset.

**Perfil sonoro por género (radar)**
Un polígono más grande indica valores promedio más altos en esas dimensiones. Polígonos superpuestos señalan géneros con identidades sonoras similares; formas divergentes revelan géneros claramente distintos. Usa esto para entender *qué hace que un género suene como tal* — más allá de su nombre.

---

### 📊 Pestaña Market Pulse

**KPIs en vivo**
Se actualizan cada hora. El género dominante refleja lo que está impulsando el mercado *ahora mismo* en el país seleccionado. Compara entre países usando el selector del sidebar para detectar diferencias regionales.

**Índice de popularidad por género**
Es una métrica relativa — mide *share de atención*, no tamaño absoluto. Si reggaeton muestra 40%, significa que 4 de cada 10 sesiones de escucha entre los artistas top van a actos de reggaeton. Un cambio en el tiempo señala un mercado en movimiento, no necesariamente más o menos oyentes en total.

**Distribución de audiencia (treemap)**
El tamaño del bloque = share de audiencia. Pocos bloques dominantes sugieren un mercado concentrado (el ganador se lo lleva todo); muchos bloques de tamaño similar sugieren un mercado fragmentado. Compara países LATAM para ver qué tan concentrado está cada mercado.

**Top artistas / top tracks**
El porcentaje mostrado es el share de ese artista o canción sobre el total de oyentes observados. Un artista que captura el 15% en un país es significativamente dominante — la mayoría de los mercados son muy fragmentados, con artistas por debajo del 5%.

**Heatmap multi-país**
Los números indican la posición en el top local de cada país (1 = más escuchado). Las celdas vacías significan que el artista no aparece en el chart de ese país. Los artistas con muchas celdas coloreadas están logrando alcance trans-fronterizo — una señal clave para sellos y distribuidoras que buscan expandirse.

**Audio features × Popularidad (análisis cruzado)**
- El **gráfico de barras** muestra la correlación de Pearson entre cada audio feature y la popularidad del género. Positivo = los géneros con más de ese feature tienden a tener mayor audiencia; negativo = menos de ese feature se correlaciona con más oyentes.
- El **scatter** muestra la relación más fuerte. Cada punto es un género. La línea de tendencia indica la dirección — pero siempre observa cuántos géneros hay en la muestra antes de sacar conclusiones fuertes.
- Como el índice de Last.fm se refresca cada hora, esta sección refleja las tendencias de escucha *actuales*, no promedios históricos.

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
├── app.py                      # App principal (tabs, sidebar, orquestación de datos)
├── utils/
│   ├── data_load.py            # Ingesta Kaggle + Last.fm, cálculo del índice de popularidad
│   └── statistics.py           # Todas las secciones visuales (Pestaña 1 y Pestaña 2)
├── data/
│   └── kaggle_tracks.csv       # Dataset histórico (~18MB, versionado en git)
├── requirements.txt
├── .env.example                # Template de variables de entorno
├── .gitignore
├── PACE_strategy.md            # Documento de estrategia del proyecto
├── README.md                   # Versión en inglés (default)
└── README.es.md                # Este archivo
```

---

## Sobre la autora

Laura Blanco — Data Scientist con enfoque en music analytics y el mercado LATAM.

[LinkedIn](https://linkedin.com/in/tu-perfil) · [GitHub](https://github.com/tu-usuario) · [Portfolio completo](https://github.com/tu-usuario)
