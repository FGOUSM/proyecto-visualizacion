# Demanda de subidas en el Gran Santiago (abril 2026)
Avance 2 – Visualización (UTFSM). EDA + app Streamlit.

**Pregunta:** ¿cómo varían la intensidad y concentración de las subidas de pasajeros (Y) según comuna y modo (X), a través de franjas horarias y entre días laborales y fin de semana (T)?

**Alcance:** subidas promedio por paradero/estación en bloques de 30 min, abril 2026, sin evasión ni destinos de viaje.

## Ejecución
```bash
pip install -r requirements.txt
python src/limpieza.py      # opcional: regenera data/processed desde data/raw
streamlit run app.py
```

## Estructura
```
app.py                       # Página 1: Contexto y Datos
pages/1_Analisis_Exploratorio.py
pages/2_Analisis_de_la_Pregunta.py
src/limpieza.py, src/utils.py
notebooks/01_eda.ipynb       # exploración y decisiones de limpieza
data/raw/                    # Excel original (DTPM)
data/processed/              # parquet limpio + log_limpieza.json
```

## Limpieza (resumen)
Sin nulos ni duplicados. `Tren`→`Metrotren`, `BUS`→`Bus`; `Media_hora`→texto HH:MM y `Hora` numérica; se excluyen 6.551 filas de comunas fuera del Gran Santiago o sin comuna (Lampa, Padre Hurtado, Colina, Pirque, Buin, SIN_COMUNA). Los valores extremos se conservan (son demanda real de estaciones de Metro).