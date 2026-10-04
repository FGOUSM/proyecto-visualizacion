import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
import numpy as np, pandas as pd, streamlit as st, plotly.express as px, plotly.graph_objects as go
from src.utils import *

st.set_page_config(page_title="Análisis de la Pregunta", layout="wide")
d = cargar()
st.title("Análisis de la Pregunta")
st.markdown("¿Cómo varían la **intensidad** y la **concentración** de las subidas según comuna, modo, franja horaria y tipo de día?")

st.sidebar.header("Filtros")
modos = st.sidebar.multiselect("Modo", list(COL_MODO), default=list(COL_MODO))
top = d.groupby("Comuna", observed=True)["Subidas_Promedio"].sum().nlargest(10).index.tolist()
comunas = st.sidebar.multiselect("Comunas (vacío = todas)", sorted(d["Comuna"].unique()), default=[])
horas = st.sidebar.slider("Franja horaria", 0.0, 23.5, (5.0, 23.5), 0.5)
f = filtrar(d, None, modos, comunas, horas)
if f.empty:
    st.warning("Los filtros no dejan datos."); st.stop()

# ---- T: perfil horario
st.header("1. Perfil horario por tipo de día (𝑇)")
p = f.groupby(["Tipo_dia", "Media_hora"], observed=True)["Subidas_Promedio"].sum().reset_index()
fig = px.line(p, x="Media_hora", y="Subidas_Promedio", color="Tipo_dia", color_discrete_map=COL_DIA,
              category_orders={"Tipo_dia": ORDEN_DIA}, labels={"Media_hora": "Bloque de 30 min", "Subidas_Promedio": "Subidas totales"})
fig.update_xaxes(tickangle=-60, dtick=2)
st.plotly_chart(fig, width="stretch")
pk = p.loc[p.groupby("Tipo_dia", observed=True)["Subidas_Promedio"].idxmax()]
st.caption("Peak en la selección: " + " · ".join(f"**{r.Tipo_dia}** {r.Media_hora}" for r in pk.itertuples()))
st.markdown("""
**Interpretación.** El día laboral muestra dos puntas pronunciadas (mañana ~07:30 y tarde), típicas del viaje por trabajo/estudio.
El sábado se aplana y se desplaza hacia el mediodía (~13:00), y el domingo es bajo y tardío (~18:30). La presión sobre la red es
máxima en horas punta laborales; el fin de semana cambia el **motivo** y la **hora** del viaje, no solo su volumen.
""")

# ---- X x T: heatmap comuna x hora
st.header("2. ¿Cuándo sube la gente en cada comuna? (𝑋 × 𝑇)")
dia = st.radio("Tipo de día", ORDEN_DIA, horizontal=True)
h = f[f["Tipo_dia"] == dia].pivot_table(index="Comuna", columns="Media_hora", values="Subidas_Promedio", aggfunc="sum", observed=True).fillna(0)
if len(h):
    h = h.loc[h.sum(axis=1).sort_values(ascending=False).index[:25]]
    h = h.div(h.sum(axis=1), axis=0) * 100
    fig = px.imshow(h, aspect="auto", color_continuous_scale="Blues",
                    labels=dict(x="Bloque de 30 min", y="Comuna", color="% del día"))
    st.plotly_chart(fig, width="stretch")
st.markdown("""
**Interpretación.** Cada fila suma 100 %, por lo que se compara la *forma* del día y no el volumen. Las comunas dormitorio
(Puente Alto, La Pintana, Maipú, El Bosque) concentran 32–39 % de sus subidas laborales entre 06:00 y 08:30, mientras que las comunas
centrales y de oriente (Santiago, Providencia, Las Condes, Vitacura) solo 13–18 % y concentran más de 29 % entre 17:00 y 19:30. Es la firma
del viaje pendular periferia → centro: la periferia presiona la red en la mañana y el centro en la tarde.
""")

# ---- Concentración
st.header("3. Concentración de la demanda entre paraderos (Lorenz)")
fig = go.Figure(go.Scatter(x=[0, 100], y=[0, 100], mode="lines", line=dict(color="#bbb", dash="dash"), name="Igualdad"))
res = []
for t in ORDEN_DIA:
    s = f[f["Tipo_dia"] == t].groupby("Paradero", observed=True)["Subidas_Promedio"].sum().sort_values().to_numpy()
    if len(s) == 0: continue
    cum = np.cumsum(s) / s.sum() * 100
    x = np.arange(1, len(s) + 1) / len(s) * 100
    idx = np.linspace(0, len(s) - 1, min(len(s), 400)).astype(int)
    fig.add_trace(go.Scatter(x=x[idx], y=cum[idx], mode="lines", name=t, line=dict(color=COL_DIA[t])))
    res.append((t, 100 - np.interp(90, x, cum)))
fig.update_layout(xaxis_title="% acumulado de paraderos (de menor a mayor demanda)", yaxis_title="% acumulado de subidas")
st.plotly_chart(fig, width="stretch")
st.caption("El 10 % de paraderos con más demanda captura: " + " · ".join(f"**{t}** {v:.0f} %" for t, v in res))
st.markdown("""
**Interpretación.** La concentración es muy alta: en día laboral, el 10 % de los paraderos/estaciones reúne ~78 % de las subidas y
el 1 % superior ~50 %. La red tiene pocos nodos críticos (casi todos de Metro) que sostienen la mayor parte de la demanda; la curva se mantiene
alta el fin de semana.
""")

# ---- Laboral vs fin de semana por comuna
st.header("4. Caída de la demanda en fin de semana por comuna")
t = f.groupby(["Comuna", "Tipo_dia"], observed=True)["Subidas_Promedio"].sum().unstack().dropna(subset=["Laboral"])
r = pd.DataFrame({"Sábado": t["Sábado"] / t["Laboral"] * 100, "Domingo": t["Domingo"] / t["Laboral"] * 100}).dropna().sort_values("Domingo")
fig = px.bar(r.reset_index().melt("Comuna", var_name="Tipo_dia", value_name="pct"), x="Comuna", y="pct", color="Tipo_dia",
             barmode="group", color_discrete_map=COL_DIA, labels={"pct": "% de la demanda laboral"})
fig.add_hline(y=100, line_dash="dash", line_color="#999")
st.plotly_chart(fig, width="stretch")
st.markdown("""
**Interpretación.** El domingo la demanda cae a 23–43 % de la laboral. Las mayores caídas ocurren en comunas de oficinas y comercio
(Vitacura, Las Condes, Providencia), y las menores en comunas residenciales y de comercio popular (Estación Central, Recoleta, Lo Espejo).
El fin de semana **reduce la brecha** entre zonas, aunque no la elimina.
""")

st.header("Conclusiones preliminares")
st.markdown("""
- **Intensidad:** el Metro (y Metrotren) concentra volúmenes por parada decenas de veces mayores que el bus.
- **Concentración:** pocos nodos reúnen la mayoría de las subidas (1 % de paraderos ≈ 50 % de la demanda laboral).
- **Temporalidad:** la presión máxima ocurre en la punta de la mañana laboral; el fin de semana es más plano, tardío y de menor volumen.
- **Espacial:** el centro y oriente (Santiago, Providencia, Las Condes) lideran; la periferia depende del bus y es más sensible a la hora punta.
""")
