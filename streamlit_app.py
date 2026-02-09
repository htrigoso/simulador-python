import math
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Constantes
# -----------------------------
G = 9.81

def kmh_to_ms(v_kmh: float) -> float:
    return v_kmh / 3.6

# Ecuaciones del modelo (MCU + fricción + inclinación)
def ac(v_ms: float, r: float) -> float:
    # a_c = v^2 / r
    return (v_ms ** 2) / r

def Fc(m_total: float, v_ms: float, r: float) -> float:
    # F_c = m v^2 / r
    return m_total * (v_ms ** 2) / r

def mu_min(v_ms: float, r: float, g: float = G) -> float:
    # mu_min = v^2 / (r g)
    return (v_ms ** 2) / (r * g)

def theta_deg(v_ms: float, r: float, g: float = G) -> float:
    # theta = arctan(v^2/(r g))
    return math.degrees(math.atan((v_ms ** 2) / (r * g)))

def safe(mu_available: float, mu_required: float) -> bool:
    return mu_available >= mu_required


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Scooter en curvas (v constante) — Simulador", layout="wide")
st.title("🛴⚡ Simulador (Python 3): Estabilidad de scooter en curvas con velocidad constante")

st.markdown(
r"""
Este simulador aplica un modelo simplificado de **mecánica clásica** para el giro de un scooter en **movimiento circular uniforme** (velocidad constante).

**Fórmulas implementadas:**
- \(a_c=\frac{v^2}{r}\)
- \(F_c=m\frac{v^2}{r}\)
- \(\mu_{min}=\frac{v^2}{rg}\)
- \(\theta=\arctan\left(\frac{v^2}{rg}\right)\)
- Criterio: **Seguro si** \(\mu \ge \mu_{min}\)
"""
)

# -----------------------------
# Sidebar: parámetros y escenarios
# -----------------------------
st.sidebar.header("🔧 Parámetros del sistema (datos reales como referencia)")

# Masas: se incluyen por completitud del análisis (F_c, N, F_f,max)
m_rider = st.sidebar.number_input(
    "Masa del conductor (kg) [referencia ENDES 2023]",
    min_value=30.0, max_value=150.0, value=70.0, step=1.0
)
m_scooter = st.sidebar.number_input(
    "Masa del scooter (kg) [referencia comercial]",
    min_value=8.0, max_value=60.0, value=18.0, step=1.0
)
m_total = m_rider + m_scooter

st.sidebar.header("🎛️ Condición del estudio")
v_kmh = st.sidebar.slider("Velocidad constante v (km/h)", 5, 60, 25, 1)
v_ms = kmh_to_ms(v_kmh)

st.sidebar.header("🛣️ Radios de giro (r)")
r_min = st.sidebar.number_input("Radio mínimo (m)", min_value=2.0, max_value=200.0, value=5.0, step=1.0)
r_max = st.sidebar.number_input("Radio máximo (m)", min_value=3.0, max_value=300.0, value=40.0, step=1.0)
n_r = st.sidebar.slider("Cantidad de puntos (radios)", 20, 300, 80, 10)

st.sidebar.header("🧱 Coeficiente de fricción (μ)")
mu_presets = {
    "Pavimento seco (μ≈0.80)": 0.80,
    "Pavimento mojado (μ≈0.50)": 0.50,
    "Baja adherencia (μ≈0.40)": 0.40,
    "Muy resbaladizo/extremo (μ≈0.10)": 0.10,
}
mu_choice = st.sidebar.selectbox("Escenario de superficie", list(mu_presets.keys()))
mu_available = mu_presets[mu_choice]

use_custom_mu = st.sidebar.checkbox("Usar μ personalizado", value=False)
if use_custom_mu:
    mu_available = st.sidebar.slider("μ personalizado", 0.05, 1.20, float(mu_available), 0.01)

st.sidebar.header("📌 Caso puntual (para reporte)")
r_case = st.sidebar.slider("Radio del caso puntual (m)", float(r_min), float(r_max), float(min(max(15.0, r_min), r_max)), 1.0)

# -----------------------------
# Caso puntual: métricas claras
# -----------------------------
mu_req_case = mu_min(v_ms, r_case)
theta_case = theta_deg(v_ms, r_case)
ac_case = ac(v_ms, r_case)
Fc_case = Fc(m_total, v_ms, r_case)

N_case = m_total * G
Ff_max_case = mu_available * N_case
safe_case = safe(mu_available, mu_req_case)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("v (m/s)", f"{v_ms:.2f}")
c2.metric("m_total (kg)", f"{m_total:.1f}")
c3.metric("a_c = v²/r (m/s²)", f"{ac_case:.2f}")
c4.metric("θ requerido (°)", f"{theta_case:.1f}")
c5.metric("μ_min requerido", f"{mu_req_case:.2f}")
c6.metric("Estado", "✅ Seguro" if safe_case else "⚠️ Riesgo")

with st.expander("Ver detalle de fuerzas (caso puntual)"):
    st.write(f"- **Fuerza centrípeta**:  \(F_c = m v^2/r = {Fc_case:.1f}\) N")
    st.write(f"- **Normal** (aprox.): \(N \\approx m g = {N_case:.1f}\) N")
    st.write(f"- **Fricción máxima**: \(F_{{f,max}} = \\mu N \\approx {Ff_max_case:.1f}\) N")
    st.write("- **Criterio**: si \(F_c \\le F_{f,max}\) entonces no hay derrape (equivale a \(\\mu \\ge \\mu_{min}\)).")

st.divider()

# -----------------------------
# Barrido: radios (r) y cálculo de mu_min, theta
# -----------------------------
r_vals = np.linspace(r_min, r_max, int(n_r))
mu_min_vals = np.array([mu_min(v_ms, r) for r in r_vals])
theta_vals = np.array([theta_deg(v_ms, r) for r in r_vals])
safe_vals = (mu_available >= mu_min_vals)

df = pd.DataFrame({
    "r (m)": r_vals,
    "μ_min requerido": mu_min_vals,
    "θ requerido (°)": theta_vals,
    "Seguro con μ elegido": np.where(safe_vals, "Sí", "No")
})

# -----------------------------
# Gráfico 1: μ_min vs r + línea de μ disponible
# -----------------------------
st.subheader("📈 Gráfico 1: μ mínimo requerido vs radio (v constante)")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=r_vals, y=mu_min_vals,
    mode="lines", name="μ_min requerido"
))
fig1.add_hline(
    y=mu_available,
    line_dash="dash",
    annotation_text=f"μ disponible ({mu_choice})"
)
fig1.update_layout(
    xaxis_title="Radio r (m)",
    yaxis_title="μ_min requerido",
    title=f"μ_min requerido para no derrapar — v = {v_kmh} km/h (constante)"
)
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# Gráfico 2: θ requerido vs r
# -----------------------------
st.subheader("📉 Gráfico 2: Inclinación requerida θ vs radio (v constante)")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=r_vals, y=theta_vals,
    mode="lines", name="θ requerido (°)"
))
fig2.update_layout(
    xaxis_title="Radio r (m)",
    yaxis_title="θ requerido (°)",
    title=f"Ángulo de inclinación requerido — v = {v_kmh} km/h (constante)"
)
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Heatmap: zona segura / riesgo en plano (μ, r)
# -----------------------------
st.subheader("🗺️ Mapa: Zona segura/riesgo (μ vs r) para v constante")

mu_grid = np.linspace(0.05, 1.00, 70)
safe_matrix = np.zeros((len(mu_grid), len(r_vals)))

for i, mu_val in enumerate(mu_grid):
    safe_matrix[i, :] = (mu_val >= mu_min_vals).astype(int)

fig3 = px.imshow(
    safe_matrix,
    origin="lower",
    aspect="auto",
    x=r_vals,
    y=mu_grid,
    labels={"x": "Radio r (m)", "y": "Coeficiente de fricción μ", "color": "Seguro (1) / Riesgo (0)"},
)
st.plotly_chart(fig3, use_container_width=True)

st.caption("Interpretación: para la velocidad fija, existe una frontera μ_min(r). Por encima es seguro; por debajo hay riesgo de derrape.")

# -----------------------------
# Tabla + exportación
# -----------------------------
st.subheader("📋 Tabla de resultados (para anexos)")
st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Descargar tabla CSV",
    data=csv,
    file_name="resultados_scooter_curvas_v_constante.csv",
    mime="text/csv"
)
