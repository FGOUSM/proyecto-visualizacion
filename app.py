import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import streamlit as st
from src.utils import cargar, log_limpieza

st.set_page_config(page_title="Demanda de subidas – Gran Santiago", layout="wide")
d, log = cargar(), log_limpieza()

st.title("Demanda de subidas de pasajeros en el Gran Santiago")
st.caption("Abril 2026 · Subidas promedio por paradero/estación en bloques de 30 min · UTFSM – Visualización, Avance 2")

st.header("1. Contexto y pregunta")
st.markdown("""
La movilidad en el Gran Santiago presenta **alta segregación espacial** y presión desigual sobre la red según zona y día.

**Pregunta:** ¿cómo varían la **intensidad y concentración** de las subidas (𝑌) según **comuna y modo** (𝑋),
a través de las **franjas horarias** y entre **días laborales y fin de semana** (𝑇)?

**Alcance:** subidas promedio por paradero/estación (Bus, Metro, Metrotren), sin evasión ni destinos de viaje.
""")

c = st.columns(4)
c[0].metric("Registros analizados", f"{len(d):,}".replace(",", "."))
c[1].metric("Paraderos/estaciones", f"{d['Paradero'].nunique():,}".replace(",", "."))
c[2].metric("Comunas", d["Comuna"].nunique())
c[3].metric("Subidas promedio (día laboral)", f"{d.loc[d.Tipo_dia=='Laboral','Subidas_Promedio'].sum():,.0f}".replace(",", "."))

st.header("2. Datos")
st.markdown("""
| Variable | Rol | Descripción |
|---|---|---|
| `Subidas_Promedio` | **Y** | Abordajes promedio en el bloque de 30 min |
| `Comuna`, `Modo`, `Paradero`/`SIMIT` | **X** | Ubicación, modo (Bus, Metro, Metrotren) y código de parada |
| `Tipo_dia`, `Media_hora` | **T** | Laboral / Sábado / Domingo y bloque horario |

Fuente: transacciones Bip! y GPS de buses (DTPM). Día laboral = promedio de 13 al 17 de abril de 2026. No incluye evasión.
""")

st.header("3. Calidad y decisiones de limpieza")
st.table({
    "Revisión": ["Valores nulos", "Filas duplicadas", "Tipos de variable", "Etiquetas de `Modo`", "Etiquetas de `Tipo_dia`",
                 "Comunas fuera de alcance / sin comuna", "Valores extremos (hasta 7.516 subidas/bloque)", "Valores fraccionarios (mín. 0,2)"],
    "Hallazgo": [f"{log['nulos']}", f"{log['duplicados']}", "`Media_hora` es hora (time); resto texto",
                 "`BUS`/`Metro`/`Tren` inconsistentes con el enunciado", "Mayúsculas; no hay festivos",
                 f"{log['filas_fuera_alcance']:,} filas (Lampa, Padre Hurtado, Colina, Pirque, Buin, SIN_COMUNA)".replace(",", "."),
                 "Cola muy pesada (mediana 2, p99 = 215): corresponde a estaciones de Metro y paraderos troncales", "Son promedios de varios días, no errores"],
    "Decisión": ["Sin acción", "Sin acción", "`Media_hora` → texto HH:MM + variable numérica `Hora`; categóricas tipadas",
                 "`Tren` → `Metrotren`; `BUS` → `Bus`", "Se normalizan; se conservan los 3 tipos",
                 "Se excluyen (fuera del Gran Santiago o sin ubicación)", "**Se conservan** (son demanda real); se usa escala log y medianas", "Se conservan"],
})
st.info(f"Base final: **{log['filas_finales']:,}** de {log['filas_originales']:,} filas.".replace(",", "."))

with st.expander("Ver muestra de datos limpios"):
    st.dataframe(d.drop(columns="Hora").sample(200, random_state=1), width="stretch")
st.markdown("Navega con el menú lateral: **Análisis Exploratorio** → **Análisis de la Pregunta**.")
