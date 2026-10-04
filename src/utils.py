import json, pathlib
import pandas as pd
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[1]
COL_DIA = {"Laboral": "#1f4e79", "Sábado": "#e08a1e", "Domingo": "#8a8a8a"}
COL_MODO = {"Bus": "#2a9d8f", "Metro": "#d62828", "Metrotren": "#6a4c93"}
ORDEN_DIA = ["Laboral", "Sábado", "Domingo"]

@st.cache_data(show_spinner="Cargando datos…")
def cargar():
    return pd.read_parquet(ROOT / "data/processed/subidas_limpio.parquet")

@st.cache_data
def log_limpieza():
    return json.load(open(ROOT / "data/processed/log_limpieza.json"))

def filtrar(d, dias=None, modos=None, comunas=None, horas=None):
    if dias: d = d[d["Tipo_dia"].isin(dias)]
    if modos: d = d[d["Modo"].isin(modos)]
    if comunas: d = d[d["Comuna"].isin(comunas)]
    if horas: d = d[(d["Hora"] >= horas[0]) & (d["Hora"] <= horas[1])]
    return d
