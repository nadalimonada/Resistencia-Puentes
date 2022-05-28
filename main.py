import math
import streamlit as st
import plotly.graph_objects as go


st.set_page_config(layout="wide")


resis_ele = {
    "Pilotes": dict(min=27, max=35),
    "Columnas": dict(min=32, max=36),
    "Tableros": dict(min=48, max=150)
}


elemento = st.sidebar.selectbox(
    "Seleccione el elemento estructural al cual desea revisar resistencia",
    (
        "Pilotes",
        "Columnas",
        "Tableros",
    ),
)

fc = st.sidebar.number_input("Resistencia de diseño", min_value=resis_ele[elemento]["min"], max_value=resis_ele[elemento]["max"])

capacidad_mixer = st.sidebar.slider(
    "Capacidad de las mixers",
    min_value=6,
    max_value=12,
    value=8,
    format="%f m3",
)

cantidad_mixers = st.sidebar.number_input(
    "Cantidad de mixers al día",
    0,
    value=10,
)


dim_cilindros = st.sidebar.selectbox(
    "Seleccione las dimensiones del cilindro de ensayo ",
    (
        "100 x 200 mm",
        "150 x 300 mm",
    ),
)

vol_concreto = capacidad_mixer * cantidad_mixers

if dim_cilindros == "100 x 200 mm":
    cant_cilindros = math.ceil(3 * vol_concreto / 40)
else:
    cant_cilindros = math.ceil(2 * vol_concreto / 40)

concreto_no_std = st.sidebar.checkbox("Concreto no estándar")
probetas_falladas = []

col1, col2 = st.columns(2)

with col1:

    if concreto_no_std:
        st.title(f"Ensayos")
        n_dias = st.number_input(
            "Ingrese la cantidad de días a los cuales va a hacer seguimiento de resistencia",
            step=1,
            min_value=1,
        )

        resis = {}

        for dia in range(n_dias):
            st.title(f"Ensayo {dia + 1}")
            n_dia = st.number_input(f"Dia del ensayo", key=dia, step=1, min_value=1)
            resis_dia = st.number_input(f"Resistencia deseada del ensayo", key=dia, min_value=0.0, max_value=1.0)
            resis[n_dia] = resis_dia

        lista_dias = list(resis.keys())

    else:
        lista_dias = (1, 3, 7, 14, 21, 28)
        resis = {
            1: 0.3,
            3: 0.4,
            7: 0.75,
            14: 0.85,
            21: 0.9,
            28: 1,
        }

    dias_fallo = st.sidebar.multiselect("Seleccione los días en los que realizará los ensayos", lista_dias, default=[lista_dias[-1]])

    st.title(f"Probetas")
    st.write(f"Se revisarán {len(dias_fallo) * cant_cilindros} probetas")

    dia_fallo = int(st.selectbox("Día de revisión de resistencia", dias_fallo))

    for probeta in range(cant_cilindros):
        st.title(f"Probeta {probeta + 1}")
        fuerza = st.number_input("Fuerza maxima (KN)", key=probeta)
        diametro = st.number_input("Diametro (mm)", key=probeta, min_value=10.0, step=0.1)
        area = (math.pi*(diametro / 1000)**2) / 4
        esfuerzo = (fuerza / 1000) / area
        probetas_falladas.append(dict(fuerza=fuerza, diametro=diametro, esfuerzo=esfuerzo))
    
    min_diametro = min(probeta["diametro"] for probeta in probetas_falladas)
    max_diametro = max(probeta["diametro"] for probeta in probetas_falladas)

    error_diam = (max_diametro - min_diametro) / max_diametro
    if error_diam > 0.02:
        st.error("Diferencia de diametro fuera de rango")

    esfuerzo_promedio = sum(probeta["esfuerzo"] for probeta in probetas_falladas) / cant_cilindros

    if esfuerzo_promedio < resis[dia_fallo] * fc:
        st.error(f"No cumple con la resistencia: {esfuerzo_promedio:.2f} MPa < {resis[dia_fallo] * fc} MPa")
    else:
        st.success(f"Cumple con la resistencia: {esfuerzo_promedio:.2f} MPa >= {resis[dia_fallo] * fc} MPa")

f = go.FigureWidget()
f.layout.title = "Curva de resistencia (MPa)"
f.add_scatter(
    x=list(resis.keys()),
    y=[x * fc for x in resis.values()],
    name="Resistencia",
)
f.add_scatter(
    x=[dia_fallo],
    y=[esfuerzo_promedio],
    name="Resistencia de laboratorio",
)

with col2:
    st.plotly_chart(f, use_container_width=True)
