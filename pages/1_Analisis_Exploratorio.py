import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
import streamlit as st, plotly.express as px
from src.utils import *

st.set_page_config(page_title="Análisis Exploratorio", layout="wide")
d = cargar()
st.title("Análisis Exploratorio")

st.sidebar.header("Filtros")
dias = st.sidebar.multiselect("Tipo de día", ORDEN_DIA, default=ORDEN_DIA)
modos = st.sidebar.multiselect("Modo", list(COL_MODO), default=list(COL_MODO))
f = filtrar(d, dias, modos)
if f.empty:
    st.warning("Selecciona al menos un tipo de día y un modo."); st.stop()

st.header("Distribución de la demanda (𝑌)")
c1, c2 = st.columns([3, 2])
with c1:
    fig = px.histogram(f, x="Subidas_Promedio", color="Modo", color_discrete_map=COL_MODO, nbins=60,
                       log_x=True, log_y=True, barmode="overlay", opacity=.7,
                       labels={"Subidas_Promedio": "Subidas promedio por bloque de 30 min (log)", "count": "Registros (log)"})
    fig.update_layout(yaxis_title="Registros (log)", legend_title="Modo")
    st.plotly_chart(fig, width="stretch")
with c2:
    st.dataframe(f.groupby("Modo", observed=True)["Subidas_Promedio"].describe(percentiles=[.5, .9, .99]).round(1))
st.markdown("""
**Interpretación.** La demanda es extremadamente asimétrica: la mediana global es 2 subidas por bloque, pero el máximo llega a 7.516.
La mayoría de los paraderos de bus aporta pocas subidas por bloque; las estaciones de Metro y Metrotren
ocupan la cola derecha. Para comparar intensidad conviene usar **medianas y escala logarítmica**, no promedios simples.
""")

st.header("Relación modo – demanda (𝑋 vs 𝑌)")
fig = px.box(f, x="Modo", y="Subidas_Promedio", color="Modo", color_discrete_map=COL_MODO, log_y=True,
             labels={"Subidas_Promedio": "Subidas por bloque (log)"})
fig.update_layout(showlegend=False)
st.plotly_chart(fig, width="stretch")
st.markdown("""
**Interpretación.** La mediana de una estación de Metro (~140–360 subidas por bloque según el día) es **más de 70 veces** la de un
paradero de bus (2–3). Cada estación concentra un acceso masivo, mientras la demanda de bus se reparte en miles de paradas pequeñas
(≈11.900 paraderos). Esto ya anticipa que la presión sobre la red es muy desigual entre modos.
""")

st.header("Relación comuna – demanda (𝑋 vs 𝑌)")
n = st.slider("Número de comunas a mostrar", 5, 34, 15)
medida = st.radio("Medida", ["Subidas totales", "Subidas promedio por paradero/estación"], horizontal=True)
g = f.groupby(["Comuna", "Modo"], observed=True)["Subidas_Promedio"].sum().reset_index()
if medida != "Subidas totales":
    npar = f.groupby("Comuna", observed=True)["Paradero"].nunique()
    g["Subidas_Promedio"] = g["Subidas_Promedio"] / g["Comuna"].map(npar)
orden = g.groupby("Comuna", observed=True)["Subidas_Promedio"].sum().nlargest(n).index
g = g[g["Comuna"].isin(orden)]
fig = px.bar(g, y="Comuna", x="Subidas_Promedio", color="Modo", color_discrete_map=COL_MODO, orientation="h",
             category_orders={"Comuna": list(orden)}, labels={"Subidas_Promedio": medida})
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, width="stretch")
st.markdown("""
**Interpretación.** Santiago, Providencia y Las Condes lideran en subidas totales gracias a Metro; Maipú y Puente Alto destacan por
volumen de bus. Al medir por paradero, las comunas centrales y de oriente suben al tope: la demanda se concentra
geográficamente en el eje Metro, coherente con la segregación espacial planteada en el problema.
""")
