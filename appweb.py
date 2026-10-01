import streamlit as st
import viga
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd


st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.card {
    background-color: #1c1f26;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 12px;
    border-left: 4px solid #1f77b4;
}
.card-title {
    font-size: 17px;
    font-weight: 600; 
    color: #c7d0db;
}
.card-value {
    font-size: 22px;
    font-weight: bold;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- FUNCIÓN CARD ----------
def card(titulo, valor):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{titulo}</div>
            <div class="card-value">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------- TITULO PRINCIPAL ----------
st.markdown("""
<h1 style='color:#4da3ff; margin-bottom: 0;'>DISEÑO A FLEXIÓN DE VIGAS - SIN Y CON ACERO A COMPRESION</h1>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:

    st.title("Propiedades Geométricas")
    b = st.number_input("Base (cm)", value=30.0)
    h = st.number_input("Altura (cm)", value=50.0)

    # ---------------------------------------------------------
    # DATOS DE DETALLADO
    # ---------------------------------------------------------

    st.markdown("### Datos de detallado")

    recubrimiento = st.number_input(
        "Recubrimiento (cm)",
        value=4.0,
        min_value=0.0,
        step=0.5
    )

    st.markdown("### Sistema estructural")

    sistema_estructural = st.selectbox(
        "Selecciona el sistema",
        [
            "Muros Estructurales",
            "Dual Tipo I",
            "Pórticos",
            "Dual Tipo II"
        ],
        index=0
    )


    st.title("Propiedades de los materiales")
    fc = st.number_input("$f'c \ (kg/cm^2)$", value=210.0)
    fy = st.number_input("$f_y \ (kg/cm^2)$", value=4200.0)
    Es = st.number_input("$E_s \ (kg/cm^2)$", value=2000000.0)
    ecu = st.number_input(
        "$\\varepsilon_{c \\mu}$",
        value=0.003,
        step=0.001,
        format="%.3f"
    )
    phiFlexion = st.number_input("$\\phi_{flexión}$", value=0.9)

    # =========================================================
    # GEOMETRÍA LONGITUDINAL
    # =========================================================

    st.title("Geometría longitudinal")

    L = st.number_input(
        "Longitud del tramo (m)",
        value=5.70,
        min_value=0.10,
        step=0.10
    )

    # =========================================================
    # SOLICITACIONES DE MOMENTO
    # =========================================================

    st.title("Solicitaciones de momento")

    st.markdown("**Sección izquierda**")

    Mu_neg_izq = st.number_input(
        "Mu (-) izquierda (ton·m)",
        value=27.10,
        min_value=0.0,
        step=0.10,
        key="Mu_neg_izq"
    )

    Mu_pos_izq = st.number_input(
        "Mu (+) izquierda (ton·m)",
        value=2.00,
        min_value=0.0,
        step=0.10,
        key="Mu_pos_izq"
    )

    st.markdown("**Sección central**")

    Mu_neg_cen = st.number_input(
        "Mu (-) central (ton·m)",
        value=1.29,
        min_value=0.0,
        step=0.10,
        key="Mu_neg_cen"
    )

    Mu_pos_cen = st.number_input(
        "Mu (+) central (ton·m)",
        value=27.00,
        min_value=0.0,
        step=0.10,
        key="Mu_pos_cen"
    )

    st.markdown("**Sección derecha**")

    Mu_neg_der = st.number_input(
        "Mu (-) derecha (ton·m)",
        value=27.00,
        min_value=0.0,
        step=0.10,
        key="Mu_neg_der"
    )

    Mu_pos_der = st.number_input(
        "Mu (+) derecha (ton·m)",
        value=2.00,
        min_value=0.0,
        step=0.10,
        key="Mu_pos_der"
    )

# =========================================================
# DIÁMETRO MÁXIMO DE ACERO LONGITUDINAL
# =========================================================

def diametro_maximo_barras(grupos_acero):

    diametros_validos = [
        diametro
        for numero, diametro in grupos_acero
        if numero > 0
    ]

    if not diametros_validos:
        return None

    return max(
        diametros_validos,
        key=lambda diametro: viga.tablaAceros.loc[
            viga.tablaAceros["Diametro"] == diametro,
            "Área(cm2)"
        ].iloc[0]
    )


# =========================================================
# DIÁMETRO MÍNIMO DE ESTRIBO SEGÚN SISTEMA ESTRUCTURAL
# =========================================================

# =========================================================
# DIÁMETRO MÍNIMO DE ESTRIBO SEGÚN SISTEMA ESTRUCTURAL
# =========================================================

def diametro_estribo_minimo(
    sistema_estructural,
    diametro_longitudinal
):

    if diametro_longitudinal is None:
        return None

    # -----------------------------------------------------
    # Diámetro nominal de las barras longitudinales
    # en cm.
    # -----------------------------------------------------

    diametros_nominales_cm = {
        "6mm": 0.60,
        "8mm": 0.80,
        "12mm": 1.20,
        '1/4"': 0.635,
        '3/8"': 0.9525,
        '1/2"': 1.27,
        '5/8"': 1.5875,
        '3/4"': 1.905,
        '1"': 2.54,
        '1 3/8"': 3.4925
    }

    db_cm = diametros_nominales_cm.get(
        diametro_longitudinal
    )

    if db_cm is None:
        raise ValueError(
            f"No se encontró el diámetro nominal "
            f"'{diametro_longitudinal}'."
        )

    # =====================================================
    # MUROS ESTRUCTURALES / DUAL TIPO I
    # E.060 - 21.4.4.4
    # =====================================================

    if sistema_estructural in [
        "Muros Estructurales",
        "Dual Tipo I"
    ]:

        if db_cm <= 1.5875:
            return "8 mm"

        elif db_cm <= 2.54:
            return '3/8"'

        else:
            return '1/2"'

    # =====================================================
    # PÓRTICOS / DUAL TIPO II
    # E.060 - 21.5.3.2
    # =====================================================

    elif sistema_estructural in [
        "Pórticos",
        "Dual Tipo II"
    ]:

        if db_cm <= 2.54:
            return '3/8"'

        else:
            return '1/2"'

    return None


# =========================================================
# DIAGRAMA DE MOMENTOS DEL TRAMO
# =========================================================

x = [0, L / 2, L]

# Para cada sección usamos los dos valores de la envolvente:
# negativo y positivo.
#
# La curva superior representa el momento positivo.
# La curva inferior representa el momento negativo.

M_pos = [
    Mu_pos_izq,
    Mu_pos_cen,
    Mu_pos_der
]

M_neg = [
    -Mu_neg_izq,
    -Mu_neg_cen,
    -Mu_neg_der
]

st.subheader("📊 Diagrama de momentos")

fig = go.Figure()

# ---------------------------------------------------------
# MOMENTO POSITIVO
# ---------------------------------------------------------

fig.add_trace(
    go.Scatter(
        x=x,
        y=M_pos,
        mode="lines+markers",
        name="Mu (+)",
        line=dict(width=3)
    )
)

# ---------------------------------------------------------
# MOMENTO NEGATIVO
# ---------------------------------------------------------

fig.add_trace(
    go.Scatter(
        x=x,
        y=M_neg,
        mode="lines+markers",
        name="Mu (-)",
        line=dict(width=3)
    )
)

# ---------------------------------------------------------
# CIERRE DE LA ENVOLVENTE EN LOS EXTREMOS
# ---------------------------------------------------------

fig.add_trace(
    go.Scatter(
        x=[0, 0],
        y=[Mu_pos_izq, -Mu_neg_izq],
        mode="lines",
        line=dict(
            width=3,
            color="#8ac6ff"
        ),
        showlegend=False,
        hoverinfo="skip"
    )
)

fig.add_trace(
    go.Scatter(
        x=[L, L],
        y=[Mu_pos_der, -Mu_neg_der],
        mode="lines",
        line=dict(
            width=3,
            color="#1f77b4"
        ),
        showlegend=False,
        hoverinfo="skip"
    )
)

# ---------------------------------------------------------
# EJE M = 0
# ---------------------------------------------------------

fig.add_hline(
    y=0,
    line_width=2,
    line_dash="dash"
)

# ---------------------------------------------------------
# FORMATO DEL GRÁFICO
# ---------------------------------------------------------

fig.update_layout(
    xaxis_title="Longitud del tramo (m)",
    yaxis_title="Momento último Mu (ton·m)",
    xaxis=dict(
        tickmode="array",
        tickvals=x,
        ticktext=[
            "Izquierda",
            "Centro",
            "Derecha"
        ]
    ),
    yaxis=dict(
        autorange="reversed"
    ),
    hovermode="x unified",
    height=500
)

st.plotly_chart(
    fig,
    width="stretch"
)

diametros_longitudinales = [
    "8mm",
    '3/8"',
    '1/2"',
    '5/8"',
    '3/4"',
    '1"'
]

# =========================================================
# ARMADURA LONGITUDINAL CORRIDA
# =========================================================

st.divider()
st.subheader("🧱 Armadura longitudinal corrida")

st.markdown(
    """
    La armadura corrida corresponde a las barras que se mantienen
    a lo largo de todo el tramo.
    """
)

col1, col2 = st.columns(2)

# ---------------------------------------------------------
# ACERO CORRIDO SUPERIOR
# ---------------------------------------------------------

with col1:

    st.markdown("### 🔺 Barras superiores continuas")

    n_corr_sup = 2

    st.write("**Número de barras:** 2")

    diam_corr_sup = st.selectbox(
        "Diámetro",
        diametros_longitudinales,
        index=0,
        key="diam_corr_sup"
    )

# ---------------------------------------------------------
# ACERO CORRIDO INFERIOR
# ---------------------------------------------------------

with col2:

    st.markdown("### 🔻 Barras inferiores continuas")

    n_corr_inf = 2

    st.write("**Número de barras:** 2")

    diam_corr_inf = st.selectbox(
        "Diámetro",
        diametros_longitudinales,
        index=0,
        key="diam_corr_inf"
    )

# =========================================================
# ARMADURA ADICIONAL / BASTONES
# =========================================================

st.divider()
st.subheader("➕ Armadura adicional / bastones")
st.markdown(
    """
    Estas barras adicionales se colocan únicamente en la zona
    seleccionada y se suman a las barras corridas.
    """
)

col_izq, col_cen, col_der = st.columns(3)

# =========================================================
# SECCIÓN IZQUIERDA
# =========================================================

with col_izq:

    st.markdown("### 📍 Sección izquierda")

    st.markdown("**▲ Barras superiores adicionales**")

    n_adic_sup_izq = st.number_input(
        "Número de barras",
        min_value=0,
        value=0,
        step=1,
        key="n_adic_sup_izq"
    )

    diam_adic_sup_izq = st.selectbox(
        "Diámetro",
        diametros_longitudinales,
        index=0,
        key="diam_adic_sup_izq"
    )

    st.markdown("**▼ Barras inferiores adicionales**")

    n_adic_inf_izq = st.number_input(
        "Número de barras",
        min_value=0,
        value=0,
        step=1,
        key="n_adic_inf_izq"
    )

    diam_adic_inf_izq = st.selectbox(
        "Diámetro",
        diametros_longitudinales,
        index=0,
        key="diam_adic_inf_izq"
    )


# =========================================================
# SECCIÓN CENTRAL
# =========================================================

with col_cen:

    st.markdown("### 📍 Sección central")

    st.markdown("**▲ Barras superiores adicionales**")

    n_adic_sup_cen = st.number_input(
        "Número de barras",
        min_value=0,
        value=0,
        step=1,
        key="n_adic_sup_cen"
    )

    diam_adic_sup_cen = st.selectbox(
        "Diámetro",
        diametros_longitudinales,
        index=0,
        key="diam_adic_sup_cen"
    )

    st.markdown("**▼ Barras inferiores adicionales**")

    n_adic_inf_cen = st.number_input(
        "Número de barras",
        min_value=0,
        value=0,
        step=1,
        key="n_adic_inf_cen"
    )

    diam_adic_inf_cen = st.selectbox(
        "Diámetro",
        diametros_longitudinales,
        index=0,
        key="diam_adic_inf_cen"
    )


# =========================================================
# SECCIÓN DERECHA
# =========================================================

with col_der:

    st.markdown("### 📍 Sección derecha")

    st.markdown("**▲ Barras superiores adicionales**")

    n_adic_sup_der = st.number_input(
        "Número de barras",
        min_value=0,
        value=0,
        step=1,
        key="n_adic_sup_der"
    )

    diam_adic_sup_der = st.selectbox(
        "Diámetro",
        diametros_longitudinales,
        index=0,
        key="diam_adic_sup_der"
    )

    st.markdown("**▼ Barras inferiores adicionales**")

    n_adic_inf_der = st.number_input(
        "Número de barras",
        min_value=0,
        value=0,
        step=1,
        key="n_adic_inf_der"
    )

    diam_adic_inf_der = st.selectbox(
        "Diámetro",
        diametros_longitudinales,
        index=0,
        key="diam_adic_inf_der"
    )

# =========================================================
# DISPOSICIÓN AUTOMÁTICA DEL ACERO POR CAPAS
# =========================================================

st.divider()
st.subheader("📐 Disposición automática del acero")

st.markdown(
    """
    Las 2 barras corridas de cada cara se mantienen siempre
    en la **capa exterior**. Las barras adicionales se van
    colocando automáticamente primero en esa misma capa,
    hasta que el ancho disponible ya no permite mantener la
    separación mínima requerida. El acero restante pasa a la
    **capa interior**.
    """
)


def configurar_distribucion_automatica(
    n_corr,
    diam_corr,
    n_adic,
    diam_adic,
    b,
    recubrimiento,
    diam_estribo,
    nombre,
    key_prefijo
):
    """
    Distribución automática de barras en hasta dos capas.

    Regla:
    1. Todas las barras corridas permanecen en la capa exterior.
    2. Las barras adicionales se agregan primero en la exterior.
    3. Se incrementan una a una hasta que la capa exterior ya
    no cumple el ancho mínimo.
    4. Las barras restantes pasan a la capa interior.
    """

    # -----------------------------------------------------
    # 1. CAPACIDAD DE LA CAPA EXTERIOR
    # -----------------------------------------------------

    n_adic_ext = 0

    for i in range(1, n_adic + 1):

        grupos_candidatos = [
            (n_corr, diam_corr),
            (i, diam_adic)
        ]

        b_min_candidato, _ = viga.ancho_minimo_acero(
            grupos_candidatos,
            recubrimiento=recubrimiento,
            diam_estribo=diam_estribo
        )

        if b_min_candidato <= b:
            n_adic_ext = i
        else:
            break

    # -----------------------------------------------------
    # 2. BARRAS RESTANTES → CAPA INTERIOR
    # -----------------------------------------------------

    n_adic_int = n_adic - n_adic_ext

    # Las corridas permanecen siempre en la exterior.
    n_corr_ext = n_corr
    n_corr_int = 0

    # -----------------------------------------------------
    # 3. VERIFICACIÓN DE LAS CORRIDAS
    # -----------------------------------------------------

    b_min_corridas, _ = viga.ancho_minimo_acero(
        [(n_corr, diam_corr)],
        recubrimiento=recubrimiento,
        diam_estribo=diam_estribo
    )

    if b_min_corridas > b:

        st.error(
            f"❌ {nombre}: las {n_corr} barras corridas "
            f"de {diam_corr} no caben siquiera en la "
            f"capa exterior. "
            f"Se requieren {b_min_corridas:.2f} cm "
            f"y la viga tiene {b:.2f} cm."
        )

    # -----------------------------------------------------
    # 4. VERIFICACIÓN DE LA CAPA INTERIOR
    # -----------------------------------------------------

    if n_adic_int > 0:

        b_min_interior, _ = viga.ancho_minimo_acero(
            [(n_adic_int, diam_adic)],
            recubrimiento=recubrimiento,
            diam_estribo=diam_estribo
        )

        if b_min_interior > b:

            st.warning(
                f"⚠️ {nombre}: las {n_adic_int} barras "
                f"adicionales restantes no caben en una "
                f"sola capa interior. "
                f"Se requieren {b_min_interior:.2f} cm "
                f"y la viga tiene {b:.2f} cm. "
                f"Por ahora el programa admite como máximo "
                f"2 capas."
            )

    # -----------------------------------------------------
    # 5. NÚMERO DE CAPAS
    # -----------------------------------------------------

    numero_capas = 2 if n_adic_int > 0 else 1

    n_ext = n_corr_ext + n_adic_ext
    n_int = n_corr_int + n_adic_int

    # -----------------------------------------------------
    # 6. INFORMACIÓN AL USUARIO
    # -----------------------------------------------------

    if numero_capas == 1:

        st.success(
            f"✅ {nombre}: todas las barras caben en "
            f"una sola capa exterior."
        )

        st.write(
            f"**Capa exterior:** {n_ext} barras "
            f"({n_corr_ext} corridas + {n_adic_ext} adicionales)"
        )

    else:

        st.info(
            f"ℹ️ {nombre}: se requieren 2 capas."
        )

        st.write(
            f"**Capa exterior:** {n_ext} barras "
            f"({n_corr_ext} corridas + {n_adic_ext} adicionales)"
        )

        st.write(
            f"**Capa interior:** {n_int} barras "
            f"({n_adic_int} adicionales)"
        )

    # -----------------------------------------------------
    # 7. RESULTADO
    # -----------------------------------------------------

    return {
        "n_corr_ext": n_corr_ext,
        "n_corr_int": n_corr_int,
        "n_adic_ext": n_adic_ext,
        "n_adic_int": n_adic_int
    }


# =========================================================
# DIÁMETROS DE ESTRIBO PARA LA DISTRIBUCIÓN
# =========================================================

# ---------------------------------------------------------
# SECCIÓN IZQUIERDA
# ---------------------------------------------------------

grupos_acero_izq_auto = [
    (n_corr_sup, diam_corr_sup),
    (n_adic_sup_izq, diam_adic_sup_izq),
    (n_corr_inf, diam_corr_inf),
    (n_adic_inf_izq, diam_adic_inf_izq)
]

diam_max_izq_auto = diametro_maximo_barras(
    grupos_acero_izq_auto
)

diam_estribo_izq_auto = diametro_estribo_minimo(
    sistema_estructural,
    diam_max_izq_auto
)


# ---------------------------------------------------------
# SECCIÓN CENTRAL
# ---------------------------------------------------------

grupos_acero_cen_auto = [
    (n_corr_sup, diam_corr_sup),
    (n_adic_sup_cen, diam_adic_sup_cen),
    (n_corr_inf, diam_corr_inf),
    (n_adic_inf_cen, diam_adic_inf_cen)
]

diam_max_cen_auto = diametro_maximo_barras(
    grupos_acero_cen_auto
)

diam_estribo_cen_auto = diametro_estribo_minimo(
    sistema_estructural,
    diam_max_cen_auto
)


# ---------------------------------------------------------
# SECCIÓN DERECHA
# ---------------------------------------------------------

grupos_acero_der_auto = [
    (n_corr_sup, diam_corr_sup),
    (n_adic_sup_der, diam_adic_sup_der),
    (n_corr_inf, diam_corr_inf),
    (n_adic_inf_der, diam_adic_inf_der)
]

diam_max_der_auto = diametro_maximo_barras(
    grupos_acero_der_auto
)

diam_estribo_der_auto = diametro_estribo_minimo(
    sistema_estructural,
    diam_max_der_auto
)


# =========================================================
# DISTRIBUCIÓN AUTOMÁTICA — IZQUIERDA
# =========================================================

st.markdown("### 📍 Sección izquierda")

dist_sup_izq = configurar_distribucion_automatica(
    n_corr=n_corr_sup,
    diam_corr=diam_corr_sup,
    n_adic=n_adic_sup_izq,
    diam_adic=diam_adic_sup_izq,
    b=b,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_izq_auto,
    nombre="Superior izquierda",
    key_prefijo="sup_izq"
)

dist_inf_izq = configurar_distribucion_automatica(
    n_corr=n_corr_inf,
    diam_corr=diam_corr_inf,
    n_adic=n_adic_inf_izq,
    diam_adic=diam_adic_inf_izq,
    b=b,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_izq_auto,
    nombre="Inferior izquierda",
    key_prefijo="inf_izq"
)


# =========================================================
# DISTRIBUCIÓN AUTOMÁTICA — CENTRO
# =========================================================

st.markdown("### 📍 Sección central")

dist_sup_cen = configurar_distribucion_automatica(
    n_corr=n_corr_sup,
    diam_corr=diam_corr_sup,
    n_adic=n_adic_sup_cen,
    diam_adic=diam_adic_sup_cen,
    b=b,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_cen_auto,
    nombre="Superior central",
    key_prefijo="sup_cen"
)

dist_inf_cen = configurar_distribucion_automatica(
    n_corr=n_corr_inf,
    diam_corr=diam_corr_inf,
    n_adic=n_adic_inf_cen,
    diam_adic=diam_adic_inf_cen,
    b=b,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_cen_auto,
    nombre="Inferior central",
    key_prefijo="inf_cen"
)


# =========================================================
# DISTRIBUCIÓN AUTOMÁTICA — DERECHA
# =========================================================

st.markdown("### 📍 Sección derecha")

dist_sup_der = configurar_distribucion_automatica(
    n_corr=n_corr_sup,
    diam_corr=diam_corr_sup,
    n_adic=n_adic_sup_der,
    diam_adic=diam_adic_sup_der,
    b=b,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_der_auto,
    nombre="Superior derecha",
    key_prefijo="sup_der"
)

dist_inf_der = configurar_distribucion_automatica(
    n_corr=n_corr_inf,
    diam_corr=diam_corr_inf,
    n_adic=n_adic_inf_der,
    diam_adic=diam_adic_inf_der,
    b=b,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_der_auto,
    nombre="Inferior derecha",
    key_prefijo="inf_der"
)


# =========================================================
# POSICIONES DE LAS CAPAS
# =========================================================

r_capa_exterior = 6.0
r_capa_interior = 8.0

# Para el diseño teórico se utiliza de momento la capa extrema.
r_sup_izq = r_capa_exterior
r_inf_izq = r_capa_exterior

r_sup_cen = r_capa_exterior
r_inf_cen = r_capa_exterior

r_sup_der = r_capa_exterior
r_inf_der = r_capa_exterior

# =========================================================
# DIÁMETRO MÁXIMO Y ESTRIBO MÍNIMO POR SECCIÓN
# =========================================================

grupos_acero_izq = [
    (n_corr_sup, diam_corr_sup),
    (n_adic_sup_izq, diam_adic_sup_izq),
    (n_corr_inf, diam_corr_inf),
    (n_adic_inf_izq, diam_adic_inf_izq)
]

grupos_acero_cen = [
    (n_corr_sup, diam_corr_sup),
    (n_adic_sup_cen, diam_adic_sup_cen),
    (n_corr_inf, diam_corr_inf),
    (n_adic_inf_cen, diam_adic_inf_cen)
]

grupos_acero_der = [
    (n_corr_sup, diam_corr_sup),
    (n_adic_sup_der, diam_adic_sup_der),
    (n_corr_inf, diam_corr_inf),
    (n_adic_inf_der, diam_adic_inf_der)
]


diam_max_izq = diametro_maximo_barras(grupos_acero_izq)
diam_max_cen = diametro_maximo_barras(grupos_acero_cen)
diam_max_der = diametro_maximo_barras(grupos_acero_der)


diam_estribo_min_izq = diametro_estribo_minimo(
    sistema_estructural,
    diam_max_izq
)

diam_estribo_min_cen = diametro_estribo_minimo(
    sistema_estructural,
    diam_max_cen
)

diam_estribo_min_der = diametro_estribo_minimo(
    sistema_estructural,
    diam_max_der
)

# =========================================================
# ANCHO MÍNIMO PARA ALOJAR EL ACERO LONGITUDINAL
# =========================================================

# ---------------------------------------------------------
# SECCIÓN IZQUIERDA
# ---------------------------------------------------------

grupos_sup_izq = [
    (n_corr_sup, diam_corr_sup),
    (n_adic_sup_izq, diam_adic_sup_izq)
]

grupos_inf_izq = [
    (n_corr_inf, diam_corr_inf),
    (n_adic_inf_izq, diam_adic_inf_izq)
]

bmin_sup_izq, n_barras_sup_izq = viga.ancho_minimo_acero(
    grupos_sup_izq,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_min_izq
)

bmin_inf_izq, n_barras_inf_izq = viga.ancho_minimo_acero(
    grupos_inf_izq,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_min_izq
)

# ---------------------------------------------------------
# SECCIÓN CENTRAL
# ---------------------------------------------------------

grupos_sup_cen = [
    (n_corr_sup, diam_corr_sup),
    (n_adic_sup_cen, diam_adic_sup_cen)
]

grupos_inf_cen = [
    (n_corr_inf, diam_corr_inf),
    (n_adic_inf_cen, diam_adic_inf_cen)
]

bmin_sup_cen, n_barras_sup_cen = viga.ancho_minimo_acero(
    grupos_sup_cen,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_min_cen
)

bmin_inf_cen, n_barras_inf_cen = viga.ancho_minimo_acero(
    grupos_inf_cen,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_min_cen
)

# ---------------------------------------------------------
# SECCIÓN DERECHA
# ---------------------------------------------------------

grupos_sup_der = [
    (n_corr_sup, diam_corr_sup),
    (n_adic_sup_der, diam_adic_sup_der)
]

grupos_inf_der = [
    (n_corr_inf, diam_corr_inf),
    (n_adic_inf_der, diam_adic_inf_der)
]

bmin_sup_der, n_barras_sup_der = viga.ancho_minimo_acero(
    grupos_sup_der,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_min_der
)

bmin_inf_der, n_barras_inf_der = viga.ancho_minimo_acero(
    grupos_inf_der,
    recubrimiento=recubrimiento,
    diam_estribo=diam_estribo_min_der
)


st.divider()
st.subheader("🔗 Diámetro mínimo de estribo")

if sistema_estructural in [
    "Muros Estructurales",
    "Dual Tipo I"
]:
    articulo_estribo = "E.060 21.4.4.4"

else:
    articulo_estribo = "E.060 21.5.3.2"

st.markdown(
    f"Según el sistema estructural seleccionado, se adopta "
    f"el criterio de **{articulo_estribo}**."
)

col1, col2, col3 = st.columns(3)

with col1:
    card(
        "Izquierda",
        f"Ø estribo mínimo: "
        f"{diam_estribo_min_izq if diam_estribo_min_izq else '—'}"
    )

with col2:
    card(
        "Centro",
        f"Ø estribo mínimo: "
        f"{diam_estribo_min_cen if diam_estribo_min_cen else '—'}"
    )

with col3:
    card(
        "Derecha",
        f"Ø estribo mínimo: "
        f"{diam_estribo_min_der if diam_estribo_min_der else '—'}"
    )

with st.expander("🔎 Ver detalle del cálculo del estribo mínimo"):

    datos_estribos = [
        {
            "Sección": "Izquierda",
            "Ø longitudinal máximo": (
                diam_max_izq if diam_max_izq else "—"
            ),
            "Ø estribo mínimo": (
                diam_estribo_min_izq
                if diam_estribo_min_izq
                else "—"
            ),
            "Artículo": articulo_estribo
        },
        {
            "Sección": "Centro",
            "Ø longitudinal máximo": (
                diam_max_cen if diam_max_cen else "—"
            ),
            "Ø estribo mínimo": (
                diam_estribo_min_cen
                if diam_estribo_min_cen
                else "—"
            ),
            "Artículo": articulo_estribo
        },
        {
            "Sección": "Derecha",
            "Ø longitudinal máximo": (
                diam_max_der if diam_max_der else "—"
            ),
            "Ø estribo mínimo": (
                diam_estribo_min_der
                if diam_estribo_min_der
                else "—"
            ),
            "Artículo": articulo_estribo
        }
    ]

    st.dataframe(
        datos_estribos,
        width="stretch",
        hide_index=True
    )

# =========================================================
# VERIFICACIÓN DEL ANCHO NECESARIO
# =========================================================

st.divider()
st.subheader("📏 Ancho requerido para una sola capa")

st.markdown(
    "Se verifica, como referencia, el ancho necesario para "
    "disponer todas las barras de cada cara en una sola capa, "
    "considerando recubrimiento, diámetro del estribo y "
    "separación libre mínima. La disposición automática "
    "puede distribuir las barras en hasta dos capas."
)

col1, col2, col3 = st.columns(3)

with col1:

    bmin_izq = max(bmin_sup_izq, bmin_inf_izq)

    card(
        "Izquierda",
        f"b mín. = {bmin_izq:.2f} cm"
    )

    if b >= bmin_izq:
        st.success("✅ CUMPLE EN 1 CAPA")
    else:
        st.warning("⚠️ NO CABE EN 1 CAPA")

with col2:

    bmin_cen = max(bmin_sup_cen, bmin_inf_cen)

    card(
        "Centro",
        f"b mín. = {bmin_cen:.2f} cm"
    )

    if b >= bmin_cen:
        st.success("✅ CUMPLE EN 1 CAPA")
    else:
        st.warning("⚠️ NO CABE EN 1 CAPA")

with col3:

    bmin_der = max(bmin_sup_der, bmin_inf_der)

    card(
        "Derecha",
        f"b mín. = {bmin_der:.2f} cm"
    )

    if b >= bmin_der:
        st.success("✅ CUMPLE EN 1 CAPA")
    else:
        st.warning("⚠️ NO CABE EN 1 CAPA")

with st.expander("🔎 Ver detalle de la verificación del ancho"):

    datos_ancho = [
        {
            "Sección": "Izquierda",
            "b disponible (cm)": round(b, 2),
            "b mín. superior (cm)": bmin_sup_izq,
            "b mín. inferior (cm)": bmin_inf_izq,
            "b mín. sección (cm)": round(
                max(bmin_sup_izq, bmin_inf_izq), 2
            ),
            "Resultado": (
                "✅ CUMPLE"
                if b >= max(bmin_sup_izq, bmin_inf_izq)
                else "❌ NO CUMPLE"
            )
        },
        {
            "Sección": "Centro",
            "b disponible (cm)": round(b, 2),
            "b mín. superior (cm)": bmin_sup_cen,
            "b mín. inferior (cm)": bmin_inf_cen,
            "b mín. sección (cm)": round(
                max(bmin_sup_cen, bmin_inf_cen), 2
            ),
            "Resultado": (
                "✅ CUMPLE"
                if b >= max(bmin_sup_cen, bmin_inf_cen)
                else "❌ NO CUMPLE"
            )
        },
        {
            "Sección": "Derecha",
            "b disponible (cm)": round(b, 2),
            "b mín. superior (cm)": bmin_sup_der,
            "b mín. inferior (cm)": bmin_inf_der,
            "b mín. sección (cm)": round(
                max(bmin_sup_der, bmin_inf_der), 2
            ),
            "Resultado": (
                "✅ CUMPLE"
                if b >= max(bmin_sup_der, bmin_inf_der)
                else "❌ NO CUMPLE"
            )
        }
    ]

    st.dataframe(
        datos_ancho,
        width="stretch",
        hide_index=True
    )

# =========================================================
# ÁREAS DE ACERO INSTALADAS POR SECCIÓN
# =========================================================

# ---------------------------------------------------------
# 1. ÁREAS DE LAS BARRAS CORRIDAS
# ---------------------------------------------------------

As_corr_sup = viga.areaAs(
    n_corr_sup,
    diam_corr_sup
)

As_corr_inf = viga.areaAs(
    n_corr_inf,
    diam_corr_inf
)

# ---------------------------------------------------------
# 2. ÁREAS ADICIONALES — IZQUIERDA
# ---------------------------------------------------------

As_adic_sup_izq = viga.areaAs(
    n_adic_sup_izq,
    diam_adic_sup_izq
)

As_adic_inf_izq = viga.areaAs(
    n_adic_inf_izq,
    diam_adic_inf_izq
)

# ---------------------------------------------------------
# 3. ÁREAS ADICIONALES — CENTRO
# ---------------------------------------------------------

As_adic_sup_cen = viga.areaAs(
    n_adic_sup_cen,
    diam_adic_sup_cen
)

As_adic_inf_cen = viga.areaAs(
    n_adic_inf_cen,
    diam_adic_inf_cen
)

# ---------------------------------------------------------
# 4. ÁREAS ADICIONALES — DERECHA
# ---------------------------------------------------------

As_adic_sup_der = viga.areaAs(
    n_adic_sup_der,
    diam_adic_sup_der
)

As_adic_inf_der = viga.areaAs(
    n_adic_inf_der,
    diam_adic_inf_der
)

# ---------------------------------------------------------
# 5. ACERO TOTAL INSTALADO EN CADA SECCIÓN
# ---------------------------------------------------------

# Sección izquierda
As_sup_izq = As_corr_sup + As_adic_sup_izq
As_inf_izq = As_corr_inf + As_adic_inf_izq

# Sección central
As_sup_cen = As_corr_sup + As_adic_sup_cen
As_inf_cen = As_corr_inf + As_adic_inf_cen

# Sección derecha
As_sup_der = As_corr_sup + As_adic_sup_der
As_inf_der = As_corr_inf + As_adic_inf_der

# Redondeo para presentación
As_sup_izq = round(As_sup_izq, 2)
As_inf_izq = round(As_inf_izq, 2)

As_sup_cen = round(As_sup_cen, 2)
As_inf_cen = round(As_inf_cen, 2)

As_sup_der = round(As_sup_der, 2)
As_inf_der = round(As_inf_der, 2)

# =========================================================
# ÁREAS DE ACERO POR CAPA
# =========================================================

def construir_capas_acero(
    n_corr,
    diam_corr,
    n_adic,
    diam_adic,
    distribucion
):

    As_ext = (
        viga.areaAs(
            distribucion["n_corr_ext"],
            diam_corr
        )
        +
        viga.areaAs(
            distribucion["n_adic_ext"],
            diam_adic
        )
    )

    As_int = (
        viga.areaAs(
            distribucion["n_corr_int"],
            diam_corr
        )
        +
        viga.areaAs(
            distribucion["n_adic_int"],
            diam_adic
        )
    )

    capas = []

    if As_ext > 0:

        capas.append(
            {
                "nombre": "Capa exterior",
                "r": 6.0,
                "As": As_ext
            }
        )

    if As_int > 0:

        capas.append(
            {
                "nombre": "Capa interior",
                "r": 8.0,
                "As": As_int
            }
        )

    return capas


# ---------------------------------------------------------
# IZQUIERDA
# ---------------------------------------------------------

capas_sup_izq = construir_capas_acero(
    n_corr_sup,
    diam_corr_sup,
    n_adic_sup_izq,
    diam_adic_sup_izq,
    dist_sup_izq
)

capas_inf_izq = construir_capas_acero(
    n_corr_inf,
    diam_corr_inf,
    n_adic_inf_izq,
    diam_adic_inf_izq,
    dist_inf_izq
)


# ---------------------------------------------------------
# CENTRO
# ---------------------------------------------------------

capas_sup_cen = construir_capas_acero(
    n_corr_sup,
    diam_corr_sup,
    n_adic_sup_cen,
    diam_adic_sup_cen,
    dist_sup_cen
)

capas_inf_cen = construir_capas_acero(
    n_corr_inf,
    diam_corr_inf,
    n_adic_inf_cen,
    diam_adic_inf_cen,
    dist_inf_cen
)


# ---------------------------------------------------------
# DERECHA
# ---------------------------------------------------------

capas_sup_der = construir_capas_acero(
    n_corr_sup,
    diam_corr_sup,
    n_adic_sup_der,
    diam_adic_sup_der,
    dist_sup_der
)

capas_inf_der = construir_capas_acero(
    n_corr_inf,
    diam_corr_inf,
    n_adic_inf_der,
    diam_adic_inf_der,
    dist_inf_der
)


# =========================================================
# RESUMEN DEL ACERO INSTALADO
# =========================================================

st.divider()
st.subheader("📋 Acero instalado por sección")

col1, col2, col3 = st.columns(3)

# ---------------------------------------------------------
# SECCIÓN IZQUIERDA
# ---------------------------------------------------------

with col1:

    st.markdown("### 📍 Izquierda")

    st.markdown(
        f"**Acero superior:**  \n"
        f"{As_sup_izq:.2f} cm²"
    )

    st.markdown(
        f"**Acero inferior:**  \n"
        f"{As_inf_izq:.2f} cm²"
    )

# ---------------------------------------------------------
# SECCIÓN CENTRAL
# ---------------------------------------------------------

with col2:

    st.markdown("### 📍 Centro")

    st.markdown(
        f"**Acero superior:**  \n"
        f"{As_sup_cen:.2f} cm²"
    )

    st.markdown(
        f"**Acero inferior:**  \n"
        f"{As_inf_cen:.2f} cm²"
    )

# ---------------------------------------------------------
# SECCIÓN DERECHA
# ---------------------------------------------------------

with col3:

    st.markdown("### 📍 Derecha")

    st.markdown(
        f"**Acero superior:**  \n"
        f"{As_sup_der:.2f} cm²"
    )

    st.markdown(
        f"**Acero inferior:**  \n"
        f"{As_inf_der:.2f} cm²"
    )


# =========================================================
# ESQUEMA DE ARMADURA LONGITUDINAL
# =========================================================

st.divider()
st.subheader("📐 Esquema de armadura longitudinal")

st.info(
    "Las 2 barras continuas superiores e inferiores se representan "
    "a lo largo de todo el tramo. Los bastones adicionales se muestran "
    "con longitudes provisionales únicamente para visualizar su "
    "disposición. Las longitudes de corte reales se determinarán "
    "posteriormente mediante el diagrama de momentos y las "
    "verificaciones de desarrollo y anclaje."
)

fig_arm = go.Figure()

# ---------------------------------------------------------
# 1. BARRAS CONTINUAS
# ---------------------------------------------------------

# Una sola línea representa las 2 barras corridas superiores
fig_arm.add_trace(
    go.Scatter(
        x=[0, L],
        y=[1.5, 1.5],
        mode="lines",
        name=f"2Ø{diam_corr_sup} superiores corridas",
        line=dict(width=6)
    )
)

# Una sola línea representa las 2 barras corridas inferiores
fig_arm.add_trace(
    go.Scatter(
        x=[0, L],
        y=[-1.5, -1.5],
        mode="lines",
        name=f"2Ø{diam_corr_inf} inferiores corridas",
        line=dict(width=6)
    )
)

# ---------------------------------------------------------
# 2. LONGITUDES PROVISIONALES DE BASTONES
# ---------------------------------------------------------

# Longitud provisional utilizada únicamente para el esquema
longitud_baston = L / 3

# ---------------------------------------------------------
# 3. BASTONES SUPERIORES
# ---------------------------------------------------------

if n_adic_sup_izq > 0:
    fig_arm.add_trace(
        go.Scatter(
            x=[0, longitud_baston],
            y=[1.2, 1.2],
            mode="lines",
            name=f"Sup. izq.: {n_adic_sup_izq}Ø{diam_adic_sup_izq}",
            line=dict(width=5),
            showlegend=True
        )
    )

if n_adic_sup_cen > 0:
    fig_arm.add_trace(
        go.Scatter(
            x=[
                L / 2 - longitud_baston / 2,
                L / 2 + longitud_baston / 2
            ],
            y=[1.2, 1.2],
            mode="lines",
            name=f"Sup. centro: {n_adic_sup_cen}Ø{diam_adic_sup_cen}",
            line=dict(width=5),
            showlegend=True
        )
    )

if n_adic_sup_der > 0:
    fig_arm.add_trace(
        go.Scatter(
            x=[L - longitud_baston, L],
            y=[1.2, 1.2],
            mode="lines",
            name=f"Sup. der.: {n_adic_sup_der}Ø{diam_adic_sup_der}",
            line=dict(width=5),
            showlegend=True
        )
    )

# ---------------------------------------------------------
# 4. BASTONES INFERIORES
# ---------------------------------------------------------

if n_adic_inf_izq > 0:
    fig_arm.add_trace(
        go.Scatter(
            x=[0, longitud_baston],
            y=[-1.2, -1.2],
            mode="lines",
            name=f"Inf. izq.: {n_adic_inf_izq}Ø{diam_adic_inf_izq}",
            line=dict(width=5),
            showlegend=True
        )
    )

if n_adic_inf_cen > 0:
    fig_arm.add_trace(
        go.Scatter(
            x=[
                L / 2 - longitud_baston / 2,
                L / 2 + longitud_baston / 2
            ],
            y=[-1.2, -1.2],
            mode="lines",
            name=f"Inf. centro: {n_adic_inf_cen}Ø{diam_adic_inf_cen}",
            line=dict(width=5),
            showlegend=True
        )
    )

if n_adic_inf_der > 0:
    fig_arm.add_trace(
        go.Scatter(
            x=[L - longitud_baston, L],
            y=[-1.2, -1.2],
            mode="lines",
            name=f"Inf. der.: {n_adic_inf_der}Ø{diam_adic_inf_der}",
            line=dict(width=5),
            showlegend=True
        )
    )

# ---------------------------------------------------------
# 5. SECCIONES DE CONTROL
# ---------------------------------------------------------

fig_arm.add_vline(
    x=0,
    line_dash="dash"
)

fig_arm.add_vline(
    x=L / 2,
    line_dash="dash"
)

fig_arm.add_vline(
    x=L,
    line_dash="dash"
)

# ---------------------------------------------------------
# 6. FORMATO
# ---------------------------------------------------------

fig_arm.update_layout(
    xaxis_title="Longitud del tramo (m)",
    yaxis=dict(
        showticklabels=False,
        range=[-2.4, 2.4]
    ),
    height=400,
    hovermode="x"
)

st.plotly_chart(
    fig_arm,
    width="stretch"
)



# =========================================================
# VERIFICACIÓN DE LAS 6 SOLICITACIONES
# =========================================================

# ---------------------------------------------------------
# SECCIÓN IZQUIERDA
# ---------------------------------------------------------

# Momento negativo:
# tracción arriba / compresión abajo
verif_neg_izq = viga.calculoFlexionDobleCapas(
    b=b,
    h=h,
    fc=fc,
    fy=fy,
    Es=Es,
    Ecu=ecu,
    phiFlexion=phiFlexion,
    capas_trac=capas_sup_izq,
    capas_comp=capas_inf_izq
)

# Momento positivo:
# tracción abajo / compresión arriba
verif_pos_izq = viga.calculoFlexionDobleCapas(
    b=b,
    h=h,
    fc=fc,
    fy=fy,
    Es=Es,
    Ecu=ecu,
    phiFlexion=phiFlexion,
    capas_trac=capas_inf_izq,
    capas_comp=capas_sup_izq
)

# ---------------------------------------------------------
# SECCIÓN CENTRAL
# ---------------------------------------------------------

# Momento negativo
verif_neg_cen = viga.calculoFlexionDobleCapas(
    b=b,
    h=h,
    fc=fc,
    fy=fy,
    Es=Es,
    Ecu=ecu,
    phiFlexion=phiFlexion,
    capas_trac=capas_sup_cen,
    capas_comp=capas_inf_cen
)

# Momento positivo
verif_pos_cen = viga.calculoFlexionDobleCapas(
    b=b,
    h=h,
    fc=fc,
    fy=fy,
    Es=Es,
    Ecu=ecu,
    phiFlexion=phiFlexion,
    capas_trac=capas_inf_cen,
    capas_comp=capas_sup_cen
)

# ---------------------------------------------------------
# SECCIÓN DERECHA
# ---------------------------------------------------------

# Momento negativo
verif_neg_der = viga.calculoFlexionDobleCapas(
    b=b,
    h=h,
    fc=fc,
    fy=fy,
    Es=Es,
    Ecu=ecu,
    phiFlexion=phiFlexion,
    capas_trac=capas_sup_der,
    capas_comp=capas_inf_der
)

# Momento positivo
verif_pos_der = viga.calculoFlexionDobleCapas(
    b=b,
    h=h,
    fc=fc,
    fy=fy,
    Es=Es,
    Ecu=ecu,
    phiFlexion=phiFlexion,
    capas_trac=capas_inf_der,
    capas_comp=capas_sup_der
)

# =========================================================
# DEMANDA VS CAPACIDAD
# =========================================================

st.divider()
st.subheader("🏗️ Capacidad resistente frente a las solicitaciones")

st.markdown(
    """
    Se compara el momento solicitado con la capacidad de diseño
    de la armadura realmente instalada en cada sección.
    """
)


# =========================================================
# FUNCIÓN PARA MOSTRAR UNA VERIFICACIÓN
# =========================================================

def mostrar_verificacion(
    titulo,
    Mu,
    resultado,
    As_traccion,
    As_compresion,
    r_trac,
    r_comp,
    capas_trac,
    capas_comp
):

    st.markdown(f"#### {titulo}")

    # -----------------------------------------------------
    # CLASIFICACIÓN DEL DISEÑO TEÓRICO
    # -----------------------------------------------------
    # Se determina independientemente de la armadura
    # realmente instalada:
    #   - Simplemente reforzada
    #   - Doblemente reforzada
    # -----------------------------------------------------

    resultado_simple_control = (
        viga.acero_requerido_flexion_simple_formula(
            b=b,
            h=h,
            r=r_trac,
            fc=fc,
            fy=fy,
            Es=Es,
            Ecu=ecu,
            phi=phiFlexion,
            Mu=Mu
        )
    )

    requiere_doble_control = resultado_simple_control.get(
        "requiere_doble",
        False
    )

    # -----------------------------------------------------
    # DISEÑO REQUERIDO CON O SIN ACERO A COMPRESIÓN
    # -----------------------------------------------------

    resultado_doble_control = None

    if requiere_doble_control:

        resultado_doble_control = (
            viga.disenoFlexionDoble(
                b=b,
                h=h,
                fc=fc,
                fy=fy,
                Es=Es,
                Ecu=ecu,
                phiFlexion=phiFlexion,
                Mu=Mu,
                r_trac=r_trac,
                r_comp=r_comp
            )
        )

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # INFORMACIÓN PRINCIPAL
    # -----------------------------------------------------

    with col1:

        card(
            "Mu",
            f"{Mu:.2f} ton·m"
        )

        card(
            "As tracción",
            f"{As_traccion:.2f} cm²"
        )

        card(
            "As compresión",
            f"{As_compresion:.2f} cm²"
        )

    # -----------------------------------------------------
    # CAPACIDAD
    # -----------------------------------------------------

    with col2:

        card(
            "Mn instalado",
            f"{resultado['Mn_val']:.2f} ton·m"
        )

        card(
            "φMn instalado",
            f"{resultado['phiMn_val']:.2f} ton·m"
        )

        if resultado["phiMn_val"] >= Mu:

            st.success(
                "✅ La sección RESISTE la solicitación."
            )

        else:

            st.error(
                "❌ La sección NO RESISTE la solicitación."
            )

        # -----------------------------------------------------
    # DEFORMACIÓN Y ESTADO DEL ACERO A TRACCIÓN
    # -----------------------------------------------------

    with st.expander("🔎 Ver deformaciones y estado del acero"):

        capas_traccion = resultado.get(
            "capas_traccion",
            []
        )

        if capas_traccion:

            datos_capas = []

            for capa in capas_traccion:

                if capa["fluye"]:
                    estado = "✅ FLUYE"
                else:
                    estado = "⚠️ NO FLUYE"

                datos_capas.append({
                    "Capa": capa["nombre"],
                    "As (cm²)": round(capa["As"], 2),
                    "d (cm)": round(capa["d"], 2),
                    "εs": round(capa["eps"], 6),
                    "εy": round(resultado["eps_y"], 6),
                    "fs (kg/cm²)": round(capa["fs"], 2),
                    "Estado": estado
                })

            df_capas = pd.DataFrame(datos_capas)

            st.dataframe(
                df_capas,
                width="stretch",
                hide_index=True
            )

            st.write(
                f"**εt extrema = {resultado['eps_s_val']:.6f}** "
                f"({resultado['capa_traccion_extrema']})"
            )

        else:

            st.info(
                "No se encontraron capas de acero a tracción."
            )
        
    # -----------------------------------------------------
    # ESTADO DEL ACERO A COMPRESIÓN
    # -----------------------------------------------------

    if resultado["fluye_compresion"]:

        st.success(
            f"✅ El acero a COMPRESIÓN FLUYE "
            f"(ε's = {resultado['eps_sp_val']:.6f} "
            f"≥ εy = {resultado['eps_y']:.6f})."
        )

    else:

        st.info(
            f"ℹ️ El acero a COMPRESIÓN NO FLUYE "
            f"(ε's = {resultado['eps_sp_val']:.6f} "
            f"< εy = {resultado['eps_y']:.6f})."
        )


    # -----------------------------------------------------
    # VERIFICACIÓN DE ACERO MÍNIMO
    # -----------------------------------------------------

    As_min = resultado["As_min_val"]

    if As_traccion >= As_min:

        st.success(
            f"✅ Acero mínimo: CUMPLE "
            f"({As_traccion:.2f} cm² ≥ {As_min:.2f} cm²)."
        )

    else:

        st.error(
            f"❌ Acero mínimo: NO CUMPLE "
            f"({As_traccion:.2f} cm² < {As_min:.2f} cm²)."
        )

            # -----------------------------------------------------
    # CONTROL DE ACERO MÁXIMO Y REQUISITOS SÍSMICOS
    # -----------------------------------------------------

    st.markdown(
        "**Control de acero máximo y requisitos sísmicos**"
    )

    # -----------------------------------------------------
    # DEFORMACIÓN DEL ACERO DE TRACCIÓN EXTREMO
    # -----------------------------------------------------

    eps_t = resultado["eps_s_val"]

    st.write(
        f"εt extrema = **{eps_t:.6f}**"
    )

    # -----------------------------------------------------
    # CUANTÍA DE ACERO EN TRACCIÓN
    # -----------------------------------------------------

    d_verif = resultado["d"]

    rho_t = (
        As_traccion
        / (b * d_verif)
    )

    # =====================================================
    # 1. CRITERIO GENERAL SEGÚN EL TIPO DE DISEÑO
    # =====================================================

    if not requiere_doble_control:

        # -------------------------------------------------
        # SECCIÓN SIMPLEMENTE REFORZADA
        # E.060 10.3.4
        # -------------------------------------------------

        st.markdown(
            "**Diseño requerido: sección simplemente reforzada**"
        )

        As_max_10_3_4 = (
            resultado_simple_control["As_max_val"]
        )

        st.write(
            "**E.060 10.3.4 — límite de acero "
            "a tracción**"
        )

        st.write(
            f"As máximo = "
            f"0.75 As₍bal₎ = "
            f"**{As_max_10_3_4:.2f} cm²**"
        )

        st.write(
            f"As tracción instalado = "
            f"**{As_traccion:.2f} cm²**"
        )

        if As_traccion <= As_max_10_3_4:

            st.success(
                f"✅ E.060 10.3.4: CUMPLE "
                f"({As_traccion:.2f} ≤ "
                f"{As_max_10_3_4:.2f} cm²)."
            )

            cumple_criterio_general = True

        else:

            st.error(
                f"❌ E.060 10.3.4: NO CUMPLE "
                f"({As_traccion:.2f} > "
                f"{As_max_10_3_4:.2f} cm²)."
            )

            cumple_criterio_general = False

    else:

        # -------------------------------------------------
        # SECCIÓN DOBLEMENTE REFORZADA
        # E.060 10.3.5
        # -------------------------------------------------

        st.markdown(
            "**Diseño requerido: sección doblemente reforzada "
            "(con acero a compresión)**"
        )

        st.write(
            "La solicitación no puede resolverse "
            "teóricamente como sección simplemente "
            "reforzada."
        )

        st.write(
            "**E.060 10.3.5 — criterio alternativo "
            "para el límite de acero a tracción**"
        )

        st.write(
            f"εt extrema = **{eps_t:.6f}**"
        )

        st.write(
            "εt mínima requerida = **0.004**"
        )

        if eps_t >= 0.004:

            st.success(
                f"✅ E.060 10.3.5: CUMPLE "
                f"(εt = {eps_t:.6f} ≥ 0.004)."
            )

            cumple_criterio_general = True

        else:

            st.error(
                f"❌ E.060 10.3.5: NO CUMPLE "
                f"(εt = {eps_t:.6f} < 0.004)."
            )

            cumple_criterio_general = False

    # =====================================================
    # 2. REQUISITO SÍSMICO 21.5.2.1
    #    SOLO PÓRTICOS / DUAL TIPO II
    # =====================================================

    cumple_criterio_sismico = True

    if sistema_estructural in [
        "Pórticos",
        "Dual Tipo II"
    ]:

        st.markdown(
            "**E.060 21.5.2.1 — requisitos sísmicos "
            "de deformación y cuantía**"
        )

        # -------------------------------------------------
        # εt ≥ 0.005
        # -------------------------------------------------

        st.write(
            f"εt extrema = **{eps_t:.6f}**"
        )

        st.write(
            "εt mínima requerida = **0.005**"
        )

        if eps_t >= 0.005:

            st.success(
                f"✅ Requisito εt: CUMPLE "
                f"(εt = {eps_t:.6f} ≥ 0.005)."
            )

            cumple_eps_sismico = True

        else:

            st.error(
                f"❌ Requisito εt: NO CUMPLE "
                f"(εt = {eps_t:.6f} < 0.005)."
            )

            cumple_eps_sismico = False

        # -------------------------------------------------
        # ρt ≤ 0.025
        # -------------------------------------------------

        rho_max = 0.025

        As_max_rho = (
            rho_max
            * b
            * d_verif
        )

        st.write(
            f"ρt = As / (b·d) = "
            f"**{rho_t:.4f}**"
        )

        st.write(
            "ρt máximo = **0.025**"
        )

        st.write(
            f"As máximo por cuantía = "
            f"0.025 × {b:.2f} × {d_verif:.2f} "
            f"= **{As_max_rho:.2f} cm²**"
        )

        if rho_t <= rho_max:

            st.success(
                f"✅ Cuantía máxima: CUMPLE "
                f"(ρt = {rho_t:.4f} ≤ 0.025)."
            )

            cumple_rho_sismico = True

        else:

            st.error(
                f"❌ Cuantía máxima: NO CUMPLE "
                f"(ρt = {rho_t:.4f} > 0.025)."
            )

            cumple_rho_sismico = False

        cumple_criterio_sismico = (
            cumple_eps_sismico
            and cumple_rho_sismico
        )

    # =====================================================
    # 3. RESULTADO GLOBAL DE ESTOS CONTROLES
    # =====================================================

    cumple_controles_acero = (
        cumple_criterio_general
        and cumple_criterio_sismico
    )

    if cumple_controles_acero:

        st.success(
            "✅ La sección cumple los criterios de "
            "acero máximo aplicables y los requisitos "
            "sísmicos que corresponden a su sistema."
        )

    else:

        st.error(
            "❌ La sección NO cumple todos los "
            "criterios normativos aplicables."
        )

    # =====================================================
    # DISEÑO REQUERIDO
    # =====================================================

    st.markdown("### 📐 Diseño requerido")

    st.info(
        "ℹ️ El diseño requerido determina una solución teórica "
        "para resistir el momento Mu, mediante una sección "
        "simplemente o doblemente reforzada. "
        "La suficiencia de las barras realmente ingresadas "
        "se verifica de forma independiente en "
        "'Verificación de la armadura instalada', "
        "considerando el acero a tracción, el acero a compresión "
        "y su distribución por capas."
    )

    if not requiere_doble_control:

        st.success(
            "✅ Sección simplemente reforzada"
        )

        col_req1, col_req2 = st.columns(2)

        with col_req1:
            card(
                "As requerido",
                f"{resultado_simple_control['As_diseno_val']:.2f} cm²"
            )

        with col_req2:
            card(
                "As máximo E.060 10.3.4",
                f"{resultado_simple_control['As_max_val']:.2f} cm²"
            )

    else:

        if (
            resultado_doble_control is not None
            and resultado_doble_control["valido"]
        ):

            st.warning(
                "⚠️ Sección doblemente reforzada "
                "(con acero a compresión)"
            )

            # ---------------------------------------------
            # PRIMERA FILA
            # ---------------------------------------------

            col_req1, col_req2, col_req3 = st.columns(3)

            with col_req1:
                card(
                    "φMn₁",
                    f"{resultado_doble_control['phiMn1_val']:.2f} ton·m"
                )

            with col_req2:
                card(
                    "Mu₂ residual",
                    f"{resultado_doble_control['Mu2_val']:.2f} ton·m"
                )

            with col_req3:
                card(
                    "As' requerido",
                    f"{resultado_doble_control['As_comp_val']:.2f} cm²"
                )

            # ---------------------------------------------
            # SEGUNDA FILA
            # ---------------------------------------------

            col_req4, col_req5, col_req6 = st.columns(3)

            with col_req4:
                card(
                    "As₁",
                    f"{resultado_doble_control['As1_val']:.2f} cm²"
                )

            with col_req5:
                card(
                    "As₂",
                    f"{resultado_doble_control['As2_val']:.2f} cm²"
                )

            with col_req6:
                card(
                    "As total requerido",
                    f"{resultado_doble_control['As_total_val']:.2f} cm²"
                )

    # =====================================================
    # CÁLCULO DETALLADO
    # =====================================================

    with st.expander("🔎 Ver cálculo detallado"):

        # =====================================================
        # 1. DATOS DE LA SECCIÓN
        # =====================================================

        st.markdown("##### 1. Datos de la sección")

        st.write(f"**b:** {b:.2f} cm")
        st.write(f"**h:** {h:.2f} cm")
        st.write(
            f"**r del acero a tracción:** "
            f"{r_trac:.2f} cm"
        )
        st.write(
            f"**r del acero a compresión:** "
            f"{r_comp:.2f} cm"
        )

        st.latex(r"d=h-r")

        st.write(
            f"d = {h:.2f} - {r_trac:.2f} "
            f"= **{resultado['d']:.2f} cm**"
        )

        st.latex(r"d'=r'")

        st.write(
            f"d' = **{resultado['d_comp']:.2f} cm**"
        )

        st.write(f"**f'c:** {fc:.2f} kg/cm²")
        st.write(f"**fy:** {fy:.2f} kg/cm²")
        st.write(f"**Es:** {Es:.2f} kg/cm²")
        st.write(f"**εcu:** {ecu:.6f}")
        st.write(f"**φ:** {phiFlexion:.2f}")

        st.divider()

        # =====================================================
        # 2. PROPIEDADES DEL ACERO
        # =====================================================

        st.markdown(
            "##### 2. Propiedades del acero"
        )

        st.latex(
            r"\varepsilon_y=\frac{f_y}{E_s}"
        )

        st.write(
            f"εy = {fy:.2f} / {Es:.2f} "
            f"= **{resultado['eps_y']:.6f}**"
        )

        st.divider()

        # =====================================================
        # 2.1. VERIFICACIÓN DEL ACERO MÍNIMO
        # =====================================================

        st.markdown(
            "##### Verificación del acero mínimo"
        )

        st.latex(
            r"I_g=\frac{bh^3}{12}"
        )

        st.write(
            f"Ig = **{resultado['Ig_val']:.2f} cm⁴**"
        )

        st.latex(
            r"Y_t=\frac{h}{2}"
        )

        st.write(
            f"Yt = **{resultado['yt_val']:.2f} cm**"
        )

        st.latex(
            r"f_r=2\sqrt{f'_c}"
        )

        st.write(
            f"fr = **{resultado['fr_val']:.2f} kg/cm²**"
        )

        st.latex(
            r"M_{cr}=\frac{f_r I_g}{Y_t}"
        )

        st.write(
            f"Mcr = **{resultado['Mcr_val']:.2f} ton·m**"
        )

        st.latex(
            r"1.2M_{cr}"
        )

        st.write(
            f"1.2 Mcr = **{resultado['1_2Mcr_val']:.2f} ton·m**"
        )

        st.latex(
            r"A_{s,\min,10.5.2}=0.7\frac{\sqrt{f'_c}}{f_y}b_wd"
        )

        st.write(
            f"As mínimo según E.060 10.5.2 = "
            f"**{resultado['As_min_10_5_2_val']:.2f} cm²**"
        )


        st.write(
            f"Acero necesario para φMn ≥ 1.2Mcr = "
            f"**{resultado['As_1_2Mcr_val']:.2f} cm²**"
            if resultado["As_1_2Mcr_val"] is not None
            else
            "Acero necesario para φMn ≥ 1.2Mcr: "
            "no existe solución simple con este peralte."
        )

        st.write(
            f"**As mínimo adoptado = "
            f"{resultado['As_min_val']:.2f} cm²**"
        )

        st.divider()



        # =====================================================
        # 3. EVALUACIÓN PRELIMINAR — SECCIÓN SIMPLEMENTE REFORZADA
        # =====================================================

        st.markdown(
            "##### 3. Evaluación preliminar — sección simplemente reforzada"
        )

        resultado_simple = (
            viga.acero_requerido_flexion_simple_formula(
                b=b,
                h=h,
                r=r_trac,
                fc=fc,
                fy=fy,
                Es=Es,
                Ecu=ecu,
                phi=phiFlexion,
                Mu=Mu
            )
        )

        requiere_doble = resultado_simple.get(
            "requiere_doble",
            False
        )

        st.write(
            f"**Momento solicitado:** "
            f"{Mu:.2f} ton·m"
        )

        st.latex(
            r"M_n^{req}=\frac{M_u}{\phi}"
        )

        st.write(
            f"Mn requerido = {Mu:.2f} / "
            f"{phiFlexion:.2f} "
            f"= **{resultado_simple['Mn_req_val']:.2f} ton·m**"
        )

        st.write(
            f"**Peralte efectivo utilizado:** "
            f"d = {resultado_simple['d']:.2f} cm"
        )

        # -----------------------------------------------------
        # PARÁMETRO Ku
        # -----------------------------------------------------

        st.latex(
            r"K_u=\frac{M_n^{req}}{0.85f'_cbd^2}"
        )

        st.write(
            f"Ku = **{resultado_simple['Ku_val']:.5f}**"
        )

        # -----------------------------------------------------
        # ACERO BALANCEADO Y LÍMITE DE LA PRIMERA PARTE
        # -----------------------------------------------------

        st.write(
            f"Acero balanceado = "
            f"**{resultado_simple['As_bal_val']:.2f} cm²**"
        )

        st.write(
            f"Acero máximo para la primera parte = "
            f"0.75 As₍bal₎ = "
            f"**{resultado_simple['As_max_val']:.2f} cm²**"
        )

        Ku_max = (
            resultado_simple["As_max_val"] * fy
            / (
                0.85
                * fc
                * b
                * resultado_simple["d"] ** 2
            )
        )

        st.write(
            f"Ku máximo asociado a 0.75 As₍bal₎ = "
            f"**{Ku_max:.5f}**"
        )

        if resultado_simple["Ku_val"] <= Ku_max:

            st.success(
                f"✅ Ku = {resultado_simple['Ku_val']:.5f} "
                f"≤ Ku máximo = {Ku_max:.5f}: "
                "la solicitación puede resolverse como "
                "sección simplemente reforzada."
            )

        else:

            st.warning(
                f"⚠️ Ku = {resultado_simple['Ku_val']:.5f} "
                f"> Ku máximo = {Ku_max:.5f}: "
                "la sección simplemente reforzada no es "
                "suficiente bajo el límite de acero adoptado."
            )

        # -----------------------------------------------------
        # INTENTO DE SOLUCIÓN SIMPLE
        # -----------------------------------------------------

        if resultado_simple.get("radicando_val") is not None:

            if resultado_simple["radicando_val"] >= 0:

                st.markdown(
                    "**Intento de solución simple "
                    "(sin considerar todavía el límite de acero máximo)**"
                )

                st.latex(
                    r"a=d-\sqrt{d^2-\frac{2M_n^{req}}{0.85f'_cb}}"
                )

                st.write(
                    f"Radicando = "
                    f"**{resultado_simple['radicando_val']:.4f}**"
                )

                st.write(
                    f"a = **{resultado_simple['a_val']:.2f} cm**"
                )

                st.latex(
                    r"c=\frac{a}{\beta_1}"
                )

                st.write(
                    f"c = {resultado_simple['a_val']:.2f} / "
                    f"{resultado_simple['beta1']:.3f} "
                    f"= **{resultado_simple['c_val']:.2f} cm**"
                )

                st.latex(
                    r"\varepsilon_s=\varepsilon_{cu}\frac{d-c}{c}"
                )

                st.write(
                    f"εs = {ecu:.6f} × "
                    f"({resultado_simple['d']:.2f} - "
                    f"{resultado_simple['c_val']:.2f}) / "
                    f"{resultado_simple['c_val']:.2f} "
                    f"= **{resultado_simple['eps_s']:.6f}**"
                )

        # -----------------------------------------------------
        # ACERO QUE NECESITARÍA LA SOLUCIÓN SIMPLE
        # -----------------------------------------------------

        if resultado_simple.get("As_flexion_val") is not None:

            st.latex(
                r"A_s^{simple}=\frac{M_u}{\phi f_y(d-a/2)}"
            )

            st.write(
                f"Acero requerido si se resolviera "
                f"como sección simplemente reforzada = "
                f"**{resultado_simple['As_flexion_val']:.2f} cm²**"
            )

            st.write(
                f"Acero mínimo = "
                f"**{resultado_simple['As_min_val']:.2f} cm²**"
            )

            if requiere_doble:

                st.write(
                    f"Este acero requerido supera el límite "
                    f"de la primera parte: "
                    f"**{resultado_simple['As_max_val']:.2f} cm²**."
                )

            else:

                st.write(
                    f"As de diseño = "
                    f"max(As simple, As mínimo) = "
                    f"**{resultado_simple['As_diseno_val']:.2f} cm²**"
                )

        # -----------------------------------------------------
        # CAPACIDAD DE LA SOLUCIÓN SIMPLE
        # -----------------------------------------------------

        if not requiere_doble:

            st.markdown(
                "**Capacidad de la sección simplemente reforzada**"
            )

            st.latex(
                r"M_n=A_sf_y\left(d-\frac{a}{2}\right)"
            )

            st.write(
                f"Mn = "
                f"**{resultado_simple['Mn_calculado_val']:.2f} ton·m**"
            )

            st.latex(
                r"\phi M_n=\phi\cdot M_n"
            )

            st.write(
                f"φMn = {phiFlexion:.2f} × "
                f"{resultado_simple['Mn_calculado_val']:.2f} "
                f"= **{resultado_simple['phiMn_calculado_val']:.2f} ton·m**"
            )

    # =====================================================
    # 4. CASO SIMPLE
    # =====================================================

        if not requiere_doble:

            st.success(
                "✅ La solicitación puede resolverse "
                "como sección simplemente reforzada."
            )

            As_req_simple = (
                resultado_simple["As_diseno_val"]
            )

            st.write(
                f"**As requerido por el modelo simple:** "
                f"{As_req_simple:.2f} cm²"
            )

            st.write(
                f"**As tracción instalado:** "
                f"{As_traccion:.2f} cm²"
            )

            st.info(
                "ℹ️ Esta comparación corresponde únicamente "
                "al diseño de referencia como sección "
                "simplemente reforzada. "
                "La suficiencia del armado realmente instalado "
                "se determina mediante la capacidad φMn de "
                "la sección instalada, mostrada en el apartado 5."
            )

        # =====================================================
        # 5. CASO DOBLEMENTE REFORZADO
        # =====================================================

        else:

            st.warning(
                "⚠️ El momento solicitado no puede resolverse "
                "como sección simplemente reforzada; "
                "se requiere una solución con acero a compresión."
            )

            st.markdown(
                "##### 4. Diseño requerido — sección doblemente reforzada"
            )

            st.write(
                "La solicitación requiere una sección "
                "doblemente reforzada, es decir, con acero "
                "a compresión, porque una sección simplemente "
                "reforzada no es suficiente."
            )

            resultado_doble = viga.disenoFlexionDoble(
                b=b,
                h=h,
                fc=fc,
                fy=fy,
                Es=Es,
                Ecu=ecu,
                phiFlexion=phiFlexion,
                Mu=Mu,
                r_trac=r_trac,
                r_comp=r_comp
            )

            if resultado_doble["valido"]:

                # -------------------------------------------------
                # PRIMERA PARTE — ACERO BALANCEADO
                # -------------------------------------------------

                st.markdown(
                    "**Primera parte de la resistencia — "
                    "sección simplemente reforzada limitada**"
                )

                st.latex(
                    r"A_{s1}=0.75A_{s,bal}"
                )

                st.write(
                    f"Acero balanceado = "
                    f"**{resultado_doble['As_bal_val']:.2f} cm²**"
                )

                st.write(
                    f"As₁ = 0.75 × "
                    f"{resultado_doble['As_bal_val']:.2f} "
                    f"= **{resultado_doble['As1_val']:.2f} cm²**"
                )

                # -------------------------------------------------
                # BLOQUE DE COMPRESIÓN
                # -------------------------------------------------

                st.latex(
                    r"a_1=\frac{A_{s1}f_y}{0.85f'_cb}"
                )

                st.write(
                    f"a₁ = **{resultado_doble['a1_val']:.2f} cm**"
                )

                st.latex(
                    r"c_1=\frac{a_1}{\beta_1}"
                )

                st.write(
                    f"c₁ = **{resultado_doble['c1_val']:.2f} cm**"
                )

                # -------------------------------------------------
                # CAPACIDAD DE LA PRIMERA PARTE
                # -------------------------------------------------

                st.latex(
                    r"M_{n1}=A_{s1}f_y\left(d-\frac{a_1}{2}\right)"
                )

                st.write(
                    f"Mn₁ = **{resultado_doble['Mn1_val']:.2f} ton·m**"
                )

                st.latex(
                    r"\phi M_{n1}=\phi\cdot M_{n1}"
                )

                st.write(
                    f"φMn₁ = {phiFlexion:.2f} × "
                    f"{resultado_doble['Mn1_val']:.2f} "
                    f"= **{resultado_doble['phiMn1_val']:.2f} ton·m**"
                )

                # -------------------------------------------------
                # MOMENTO RESIDUAL
                # -------------------------------------------------

                st.markdown(
                    "##### Momento residual — segunda contribución"
                )

                st.write(
                    "La primera parte de la resistencia "
                    "proporciona φMn₁. El momento que todavía "
                    "debe resistirse mediante el par adicional "
                    "acero de tracción–acero de compresión es Mu₂."
                )

                st.latex(
                    r"M_{u2}=M_u-\phi M_{n1}"
                )

                st.write(
                    f"Mu₂ = {Mu:.2f} - "
                    f"{resultado_doble['phiMn1_val']:.2f}"
                    f" = **{resultado_doble['Mu2_val']:.2f} ton·m**"
                )

                # -------------------------------------------------
                # ACERO ADICIONAL DE TRACCIÓN
                # -------------------------------------------------

                st.markdown(
                    "**Acero adicional de tracción**"
                )

                st.latex(
                    r"A_{s2}="
                    r"\frac{M_{u2}}{\phi f_y(d-d')}"
                )

                st.write(
                    f"As₂ = "
                    f"{resultado_doble['Mu2_val']:.2f} × 1000 × 100 "
                    f"/ ["
                    f"{phiFlexion:.2f} × "
                    f"{fy:.2f} × ("
                    f"{resultado_doble['d']:.2f} - "
                    f"{resultado_doble['d_comp']:.2f}"
                    f")]"
                )

                st.write(
                    f"**As₂ = {resultado_doble['As2_val']:.2f} cm²**"
                )

                st.info(
                    "As₂ corresponde únicamente al acero adicional "
                    "de tracción necesario para resistir Mu₂. "
                    "Este acero trabaja en pareja con el acero "
                    "de compresión A's."
                )

                # -------------------------------------------------
                # SEGUNDA PARTE DE LA RESISTENCIA
                # -------------------------------------------------

                st.markdown(
                    "**Segunda contribución de resistencia**"
                )

                Mn2 = (
                    resultado_doble["Mu2_val"]
                    / phiFlexion
                )

                phiMn2 = resultado_doble["Mu2_val"]


                st.latex(
                    r"M_{n2}=\frac{M_{u2}}{\phi}"
                )

                st.write(
                    f"Mn₂ = {resultado_doble['Mu2_val']:.2f} / "
                    f"{phiFlexion:.2f} "
                    f"= **{Mn2:.2f} ton·m**"
                )

                st.latex(
                    r"\phi M_{n2}=\phi\cdot M_{n2}=M_{u2}"
                )

                st.write(
                    f"φMn₂ = {phiFlexion:.2f} × "
                    f"{Mn2:.2f} "
                    f"= **{phiMn2:.2f} ton·m**"
                )

                st.info(
                    "Por tratarse del diseño del refuerzo adicional, "
                    "φMn₂ se determina para igualar el momento residual Mu₂."
                )

                # -------------------------------------------------
                # RESISTENCIA TOTAL DE LA SECCIÓN
                # -------------------------------------------------

                Mn_total = resultado_doble["Mn1_val"] + Mn2
                phiMn_total = resultado_doble["phiMn1_val"] + phiMn2

                st.markdown("##### Resistencia total")

                st.latex(
                    r"M_n=M_{n1}+M_{n2}"
                )

                st.write(
                    f"Mn = {resultado_doble['Mn1_val']:.2f} + "
                    f"{Mn2:.2f} "
                    f"= **{Mn_total:.2f} ton·m**"
                )

                st.latex(
                    r"\phi M_n=\phi M_{n1}+\phi M_{n2}"
                )

                st.write(
                    f"φMn = {resultado_doble['phiMn1_val']:.2f} + "
                    f"{phiMn2:.2f} "
                    f"= **{phiMn_total:.2f} ton·m**"
                )

                # -------------------------------------------------
                # ACERO DE COMPRESIÓN
                # -------------------------------------------------

                st.markdown(
                    "##### Acero de compresión requerido"
                )

                st.latex(
                    r"\varepsilon'_s=\varepsilon_{cu}\frac{c_1-d'}{c_1}"
                )

                st.write(
                    f"ε's = "
                    f"**{resultado_doble['eps_sp_val']:.6f}**"
                )

                st.latex(
                    r"f'_s=\min(E_s\varepsilon'_s,f_y)"
                )

                st.write(
                    f"f's = "
                    f"**{resultado_doble['fs_p_val']:.2f} kg/cm²**"
                )

                if resultado_doble["fluye_compresion"]:

                    st.success(
                        "✅ El acero de compresión "
                        "requerido fluye."
                    )

                else:

                    st.info(
                        "ℹ️ El acero de compresión "
                        "requerido no fluye."
                    )

                st.latex(
                    r"A'_s=\frac{A_{s2}f_y}{f'_s}"
                )

                st.write(
                    f"As' requerido = "
                    f"**{resultado_doble['As_comp_val']:.2f} cm²**"
                )

                # -------------------------------------------------
                # ACERO TOTAL DE TRACCIÓN
                # -------------------------------------------------

                st.markdown(
                    "##### Acero total de tracción requerido"
                )

                st.latex(
                    r"A_s=A_{s1}+A_{s2}"
                )

                st.write(
                    f"As total requerido = "
                    f"{resultado_doble['As1_val']:.2f} + "
                    f"{resultado_doble['As2_val']:.2f}"
                    f" = **{resultado_doble['As_total_val']:.2f} cm²**"
                )

                # -------------------------------------------------
                # COMPARACIÓN CON LA ARMADURA INSTALADA
                # -------------------------------------------------

                st.markdown(
                    "##### Referencia frente a la armadura instalada"
                )

                st.write(
                    f"As total requerido por el diseño doble = "
                    f"**{resultado_doble['As_total_val']:.2f} cm²**"
                )

                st.write(
                    f"As tracción instalado = "
                    f"**{As_traccion:.2f} cm²**"
                )

                st.write(
                    f"As' requerido por el diseño doble = "
                    f"**{resultado_doble['As_comp_val']:.2f} cm²**"
                )

                st.write(
                    f"As' instalado = "
                    f"**{As_compresion:.2f} cm²**"
                )

                st.info(
                    "ℹ️ Estos valores corresponden a una "
                    "comparación con el detalle teórico "
                    "doblemente reforzado. La suficiencia "
                    "del armado realmente instalado se "
                    "determina de forma independiente "
                    "mediante φMn de la sección instalada."
                )

        st.divider()

        # =====================================================
        # 6. VERIFICACIÓN DE LA ARMADURA REALMENTE INSTALADA
        # =====================================================

        st.markdown(
            "##### 5. Verificación de la armadura instalada"
        )

        st.info(
            "Aquí se evalúan las barras realmente ingresadas "
            "(tracción y compresión), incluyendo su distribución "
            "por capas. Esta es la verificación que determina "
            "si la armadura instalada resiste el momento Mu."
        )

        # -----------------------------------------------------
        # 5.1 ACERO INSTALADO
        # -----------------------------------------------------

        st.markdown("**5.1 Acero instalado**")

        col_inst1, col_inst2 = st.columns(2)

        with col_inst1:
            card(
                "As tracción instalado",
                f"{As_traccion:.2f} cm²"
            )

        with col_inst2:
            card(
                "As compresión instalado",
                f"{As_compresion:.2f} cm²"
            )

        # -----------------------------------------------------
        # 5.2 EJE NEUTRO REAL
        # -----------------------------------------------------

        st.markdown("**5.2 Eje neutro real de la sección instalada**")

        c_real = resultado["c_val"]
        a_real = resultado["a_val"]
        beta1_real = resultado["beta1"]

        col_c1, col_c2 = st.columns(2)

        with col_c1:

            st.latex(
                r"a=\beta_1 c"
            )

            st.write(
                f"a = {resultado['beta1']:.3f} × "
                f"{c_real:.2f} "
                f"= **{a_real:.2f} cm**"
            )

        with col_c2:

            card(
                "c real",
                f"{c_real:.2f} cm"
            )

        st.write(
            f"β₁ = **{beta1_real:.3f}**"
        )

        # -----------------------------------------------------
        # 5.3 COMPATIBILIDAD DE DEFORMACIONES
        # -----------------------------------------------------

        st.markdown(
            "**5.3 Compatibilidad de deformaciones**"
        )

        st.latex(
            r"\varepsilon_{s,i}"
            r"=\varepsilon_{cu}"
            r"\frac{d_i-c}{c}"
        )

        st.latex(
            r"\varepsilon'_{s,i}"
            r"=\varepsilon_{cu}"
            r"\frac{c-d'_i}{c}"
        )

        st.write(
            f"εcu = **{ecu:.6f}**"
        )

        # -----------------------------------------------------
        # 5.4 ACERO A TRACCIÓN POR CAPA
        # -----------------------------------------------------

        capas_traccion_instaladas = resultado.get(
            "capas_traccion",
            []
        )

        if capas_traccion_instaladas:

            st.markdown(
                "**Deformaciones y esfuerzos — acero a tracción**"
            )

            datos_traccion = []

            for capa in capas_traccion_instaladas:

                estado = (
                    "✅ FLUYE"
                    if capa["fluye"]
                    else "⚠️ NO FLUYE"
                )

                datos_traccion.append({
                    "Capa": capa["nombre"],
                    "As (cm²)": round(capa["As"], 2),
                    "d (cm)": round(capa["d"], 2),
                    "εs": round(capa["eps"], 6),
                    "εy": round(resultado["eps_y"], 6),
                    "fs (kg/cm²)": round(capa["fs"], 2),
                    "T (tonf)": round(capa["T"] / 1000, 2),
                    "Estado": estado
                })

            df_traccion_instalada = pd.DataFrame(
                datos_traccion
            )

            st.dataframe(
                df_traccion_instalada,
                width="stretch",
                hide_index=True
            )

        # -----------------------------------------------------
        # 5.5 ACERO A COMPRESIÓN POR CAPA
        # -----------------------------------------------------

        capas_compresion_instaladas = resultado.get(
            "capas_compresion",
            []
        )

        if capas_compresion_instaladas:

            st.markdown(
                "**Deformaciones y esfuerzos — acero a compresión**"
            )

            datos_compresion = []

            for capa in capas_compresion_instaladas:

                estado = (
                    "✅ FLUYE"
                    if capa["fluye"]
                    else "⚠️ NO FLUYE"
                )

                datos_compresion.append({
                    "Capa": capa["nombre"],
                    "As (cm²)": round(capa["As"], 2),
                    "d' (cm)": round(capa["d"], 2),
                    "ε's": round(capa["eps"], 6),
                    "εy": round(resultado["eps_y"], 6),
                    "fs' (kg/cm²)": round(capa["fs"], 2),
                    "C (tonf)": round(capa["C"] / 1000, 2),
                    "Estado": estado
                })

            df_compresion_instalada = pd.DataFrame(
                datos_compresion
            )

            st.dataframe(
                df_compresion_instalada,
                width="stretch",
                hide_index=True
            )

        # -----------------------------------------------------
        # 5.6 FUERZAS INTERNAS Y EQUILIBRIO
        # -----------------------------------------------------

        st.markdown(
            "**5.6 Fuerzas internas y equilibrio**"
        )

        st.latex(
            r"C_c=0.85f'_cba"
        )

        st.write(
            f"Cc = **{resultado['Cc_val']:.2f} tonf**"
        )

        st.write(
            f"T total = **{resultado['T_val']:.2f} tonf**"
        )

        st.write(
            f"C acero = **{resultado['Cs_val']:.2f} tonf**"
        )

        st.latex(
            r"C_c+C_s-T\approx0"
        )

        st.write(
            f"Error de equilibrio = "
            f"**{resultado['error_equilibrio_val']:.6f} tonf**"
        )

        # -----------------------------------------------------
        # 5.7 MOMENTO NOMINAL Y CAPACIDAD
        # -----------------------------------------------------

        st.markdown(
            "**5.7 Momento resistente de la armadura instalada**"
        )

        st.write(
            f"Mn instalado = "
            f"**{resultado['Mn_val']:.2f} ton·m**"
        )

        st.latex(
            r"\phi M_n=\phi\cdot M_n"
        )

        st.write(
            f"φMn instalado = {phiFlexion:.2f} × "
            f"{resultado['Mn_val']:.2f} "
            f"= **{resultado['phiMn_val']:.2f} ton·m**"
        )

        # -----------------------------------------------------
        # 5.8 VERIFICACIÓN FINAL
        # -----------------------------------------------------

        if resultado["phiMn_val"] >= Mu:

            st.success(
                f"✅ La armadura instalada RESISTE la "
                f"solicitación: φMn = "
                f"{resultado['phiMn_val']:.2f} ≥ "
                f"Mu = {Mu:.2f} ton·m."
            )

        else:

            st.error(
                f"❌ La armadura instalada NO RESISTE la "
                f"solicitación: φMn = "
                f"{resultado['phiMn_val']:.2f} < "
                f"Mu = {Mu:.2f} ton·m."
            )


    # -----------------------------------------------------
    # DIAGNÓSTICO DE DISEÑO
    # -----------------------------------------------------

    if resultado["phiMn_val"] < Mu:

        st.markdown("##### ⚠️ La armadura instalada es insuficiente")

        # -------------------------------------------------
        # PRIMER INTENTO: SECCIÓN SIMPLEMENTE REFORZADA
        # -------------------------------------------------

        resultado_simple = viga.acero_requerido_flexion_simple_formula(
            b=b,
            h=h,
            r=r_trac,
            fc=fc,
            fy=fy,
            Es=Es,
            Ecu=ecu,
            phi=phiFlexion,
            Mu=Mu
        )

        # -------------------------------------------------
        # CASO 1: PUEDE RESOLVERSE COMO SIMPLE
        # -------------------------------------------------

        if not resultado_simple.get("requiere_doble", False):

            As_req_simple = resultado_simple["As_diseno_val"]

            st.info(
                "La solicitación puede resolverse "
                "teóricamente como sección simplemente reforzada."
            )

            col1, col2 = st.columns(2)

            with col1:

                card(
                    "As requerido",
                    f"{As_req_simple:.2f} cm²"
                )

            with col2:

                card(
                    "As instalado",
                    f"{As_traccion:.2f} cm²"
                )

            As_adicional = max(
                As_req_simple - As_traccion,
                0.0
            )

            if As_adicional > 0:

                st.warning(
                    f"⚠️ Falta aproximadamente "
                    f"{As_adicional:.2f} cm² de acero a TRACCIÓN."
                )

            else:

                st.success(
                    "✅ El acero de tracción instalado "
                    "es suficiente según el diseño teórico."
                )

        # -------------------------------------------------
        # CASO 2: REQUIERE DOBLE REFUERZO
        # -------------------------------------------------

        else:

            st.warning(
                "⚠️ La solicitación requiere una sección "
                "DOBLEMENTE REFORZADA."
            )

            resultado_doble = viga.disenoFlexionDoble(
                b=b,
                h=h,
                fc=fc,
                fy=fy,
                Es=Es,
                Ecu=ecu,
                phiFlexion=phiFlexion,
                Mu=Mu,
                r_trac=r_trac,
                r_comp=r_comp
            )

            if resultado_doble["valido"]:

                As_req_doble = resultado_doble["As_total_val"]
                As_comp_req = resultado_doble["As_comp_val"]

                st.markdown(
                    "##### Diseño teórico requerido"
                )

                col1, col2 = st.columns(2)

                with col1:

                    card(
                        "As total requerido",
                        f"{As_req_doble:.2f} cm²"
                    )

                    card(
                        "As tracción instalado",
                        f"{As_traccion:.2f} cm²"
                    )

                with col2:

                    card(
                        "As' requerido",
                        f"{As_comp_req:.2f} cm²"
                    )

                    card(
                        "As' instalado",
                        f"{As_compresion:.2f} cm²"
                    )

                # -----------------------------------------
                # ACERO ADICIONAL DE TRACCIÓN
                # -----------------------------------------

                falta_traccion = max(
                    As_req_doble - As_traccion,
                    0.0
                )

                # -----------------------------------------
                # ACERO ADICIONAL DE COMPRESIÓN
                # -----------------------------------------

                falta_compresion = max(
                    As_comp_req - As_compresion,
                    0.0
                )

                if falta_traccion > 0:

                    st.warning(
                        f"⚠️ Se requieren "
                        f"{falta_traccion:.2f} cm² adicionales "
                        f"de acero a TRACCIÓN."
                    )

                else:

                    st.success(
                        "✅ El acero de tracción instalado "
                        "es suficiente."
                    )

                if falta_compresion > 0:

                    st.warning(
                        f"⚠️ Se requieren "
                        f"{falta_compresion:.2f} cm² adicionales "
                        f"de acero a COMPRESIÓN."
                    )

                else:

                    st.success(
                        "✅ El acero de compresión instalado "
                        "es suficiente."
                    )

                # -----------------------------------------
                # MOMENTO RESIDUAL
                # -----------------------------------------

                st.markdown("##### Momento residual")

                card(
                    "Mu₂",
                    f"{resultado_doble['Mu2_val']:.2f} ton·m"
                )



# =========================================================
# SECCIÓN IZQUIERDA
# =========================================================

st.markdown("## 📍 Sección izquierda")

col_neg, col_pos = st.columns(2)

with col_neg:
    mostrar_verificacion(
        titulo="Momento negativo",
        Mu=Mu_neg_izq,
        resultado=verif_neg_izq,
        As_traccion=As_sup_izq,
        As_compresion=As_inf_izq,
        r_trac=r_sup_izq,
        r_comp=r_inf_izq,
        capas_trac=capas_sup_izq,
        capas_comp=capas_inf_izq
    )

with col_pos:
    mostrar_verificacion(
        titulo="Momento positivo",
        Mu=Mu_pos_izq,
        resultado=verif_pos_izq,
        As_traccion=As_inf_izq,
        As_compresion=As_sup_izq,
        r_trac=r_inf_izq,
        r_comp=r_sup_izq,
        capas_trac=capas_inf_izq,
        capas_comp=capas_sup_izq
    )


# =========================================================
# SECCIÓN CENTRAL
# =========================================================

st.markdown("## 📍 Sección central")

col_neg, col_pos = st.columns(2)

with col_neg:
    mostrar_verificacion(
        titulo="Momento negativo",
        Mu=Mu_neg_cen,
        resultado=verif_neg_cen,
        As_traccion=As_sup_cen,
        As_compresion=As_inf_cen,
        r_trac=r_sup_cen,
        r_comp=r_inf_cen,
        capas_trac=capas_sup_cen,
        capas_comp=capas_inf_cen
    )

with col_pos:
    mostrar_verificacion(
        titulo="Momento positivo",
        Mu=Mu_pos_cen,
        resultado=verif_pos_cen,
        As_traccion=As_inf_cen,
        As_compresion=As_sup_cen,
        r_trac=r_inf_cen,
        r_comp=r_sup_cen,
        capas_trac=capas_inf_cen,
        capas_comp=capas_sup_cen
    )

# =========================================================
# SECCIÓN DERECHA
# =========================================================

st.markdown("## 📍 Sección derecha")

col_neg, col_pos = st.columns(2)

with col_neg:
    mostrar_verificacion(
        titulo="Momento negativo",
        Mu=Mu_neg_der,
        resultado=verif_neg_der,
        As_traccion=As_sup_der,
        As_compresion=As_inf_der,
        r_trac=r_sup_der,
        r_comp=r_inf_der,
        capas_trac=capas_sup_der,
        capas_comp=capas_inf_der
    )

with col_pos:
    mostrar_verificacion(
        titulo="Momento positivo",
        Mu=Mu_pos_der,
        resultado=verif_pos_der,
        As_traccion=As_inf_der,
        As_compresion=As_sup_der,
        r_trac=r_inf_der,
        r_comp=r_sup_der,
        capas_trac=capas_inf_der,
        capas_comp=capas_sup_der
    )


# =========================================================
# VERIFICACIÓN SÍSMICA DE RESISTENCIA A FLEXIÓN
# E.060 21.4.4.3 / 21.5.2.2
# =========================================================

st.divider()
st.subheader("🛡️ Verificación sísmica de resistencia a flexión")

# ---------------------------------------------------------
# Capacidades de diseño φMn
# ---------------------------------------------------------

phiMn_neg_izq = verif_neg_izq["phiMn_val"]
phiMn_pos_izq = verif_pos_izq["phiMn_val"]

phiMn_neg_cen = verif_neg_cen["phiMn_val"]
phiMn_pos_cen = verif_pos_cen["phiMn_val"]

phiMn_neg_der = verif_neg_der["phiMn_val"]
phiMn_pos_der = verif_pos_der["phiMn_val"]


# ---------------------------------------------------------
# Criterio según sistema estructural
# ---------------------------------------------------------

if sistema_estructural in [
    "Muros Estructurales",
    "Dual Tipo I"
]:
    factor_pos_neg = 1 / 3
    referencia_sismica = "E.060 21.4.4.3"
    texto_criterio = "φMn+ ≥ 1/3 · φMn−"

elif sistema_estructural in [
    "Pórticos",
    "Dual Tipo II"
]:
    factor_pos_neg = 1 / 2
    referencia_sismica = "E.060 21.5.2.2"
    texto_criterio = "φMn+ ≥ 1/2 · φMn−"

else:
    factor_pos_neg = None
    referencia_sismica = ""
    texto_criterio = ""


st.markdown(
    f"**Sistema estructural:** {sistema_estructural}"
)

st.write(
    f"**Criterio en las caras de los nudos:** "
    f"{texto_criterio} ({referencia_sismica})"
)


# ---------------------------------------------------------
# 1. Criterio en las caras de los nudos
# ---------------------------------------------------------

st.markdown("##### 1. Resistencia positiva respecto a la negativa")

phiMn_pos_req_izq = factor_pos_neg * phiMn_neg_izq
phiMn_pos_req_der = factor_pos_neg * phiMn_neg_der

cumple_izq = phiMn_pos_izq >= phiMn_pos_req_izq
cumple_der = phiMn_pos_der >= phiMn_pos_req_der

col_izq, col_der = st.columns(2)

with col_izq:

    st.write("**Cara del nudo izquierda**")

    st.write(
        f"φMn− = **{phiMn_neg_izq:.2f} ton·m**"
    )

    st.write(
        f"φMn+ = **{phiMn_pos_izq:.2f} ton·m**"
    )

    st.write(
        f"φMn+ requerido = "
        f"{factor_pos_neg:.3f} × {phiMn_neg_izq:.2f} "
        f"= **{phiMn_pos_req_izq:.2f} ton·m**"
    )

    if cumple_izq:
        st.success("✅ Cara izquierda: CUMPLE")
    else:
        st.error("❌ Cara izquierda: NO CUMPLE")


with col_der:

    st.write("**Cara del nudo derecha**")

    st.write(
        f"φMn− = **{phiMn_neg_der:.2f} ton·m**"
    )

    st.write(
        f"φMn+ = **{phiMn_pos_der:.2f} ton·m**"
    )

    st.write(
        f"φMn+ requerido = "
        f"{factor_pos_neg:.3f} × {phiMn_neg_der:.2f} "
        f"= **{phiMn_pos_req_der:.2f} ton·m**"
    )

    if cumple_der:
        st.success("✅ Cara derecha: CUMPLE")
    else:
        st.error("❌ Cara derecha: NO CUMPLE")


# ---------------------------------------------------------
# 2. Criterio de 1/4 de la máxima resistencia en los nudos
# ---------------------------------------------------------

st.markdown(
    "##### 2. Resistencia mínima en cualquier sección"
)

phiMn_max_nudos = max(
    phiMn_neg_izq,
    phiMn_pos_izq,
    phiMn_neg_der,
    phiMn_pos_der
)

phiMn_min_1_4 = 0.25 * phiMn_max_nudos

st.write(
    f"Máxima resistencia en caras de nudo = "
    f"**{phiMn_max_nudos:.2f} ton·m**"
)

st.write(
    f"1/4 de la máxima resistencia = "
    f"0.25 × {phiMn_max_nudos:.2f} "
    f"= **{phiMn_min_1_4:.2f} ton·m**"
)


# ---------------------------------------------------------
# Verificación de las seis capacidades
# ---------------------------------------------------------

verificaciones_1_4 = {
    "Izquierda −": phiMn_neg_izq,
    "Izquierda +": phiMn_pos_izq,
    "Centro −": phiMn_neg_cen,
    "Centro +": phiMn_pos_cen,
    "Derecha −": phiMn_neg_der,
    "Derecha +": phiMn_pos_der,
}

cumple_todas_1_4 = True

for nombre, phiMn in verificaciones_1_4.items():

    if phiMn >= phiMn_min_1_4:

        st.success(
            f"✅ {nombre}: "
            f"φMn = {phiMn:.2f} ton·m ≥ "
            f"{phiMn_min_1_4:.2f} ton·m"
        )

    else:

        st.error(
            f"❌ {nombre}: "
            f"φMn = {phiMn:.2f} ton·m < "
            f"{phiMn_min_1_4:.2f} ton·m"
        )

        cumple_todas_1_4 = False


# ---------------------------------------------------------
# RESULTADO FINAL
# ---------------------------------------------------------

if cumple_izq and cumple_der and cumple_todas_1_4:

    st.success(
        f"✅ La viga CUMPLE los requisitos de "
        f"resistencia sísmica a flexión de {referencia_sismica}."
    )

else:

    st.error(
        f"❌ La viga NO CUMPLE todos los requisitos de "
        f"resistencia sísmica a flexión de {referencia_sismica}."
    )


# =========================================================
# RESUMEN GLOBAL DE LAS 6 VERIFICACIONES
# =========================================================

resumen_verificaciones = {
    "Izquierda - Mu (-)": verif_neg_izq,
    "Izquierda - Mu (+)": verif_pos_izq,
    "Centro - Mu (-)": verif_neg_cen,
    "Centro - Mu (+)": verif_pos_cen,
    "Derecha - Mu (-)": verif_neg_der,
    "Derecha - Mu (+)": verif_pos_der,
}

datos_resumen = []

for nombre, resultado in resumen_verificaciones.items():

    if "Izquierda" in nombre:
        if "(-)" in nombre:
            Mu_resumen = Mu_neg_izq
            As_trac_resumen = As_sup_izq
            As_comp_resumen = As_inf_izq
        else:
            Mu_resumen = Mu_pos_izq
            As_trac_resumen = As_inf_izq
            As_comp_resumen = As_sup_izq

    elif "Centro" in nombre:
        if "(-)" in nombre:
            Mu_resumen = Mu_neg_cen
            As_trac_resumen = As_sup_cen
            As_comp_resumen = As_inf_cen
        else:
            Mu_resumen = Mu_pos_cen
            As_trac_resumen = As_inf_cen
            As_comp_resumen = As_sup_cen

    else:
        if "(-)" in nombre:
            Mu_resumen = Mu_neg_der
            As_trac_resumen = As_sup_der
            As_comp_resumen = As_inf_der
        else:
            Mu_resumen = Mu_pos_der
            As_trac_resumen = As_inf_der
            As_comp_resumen = As_sup_der

    phiMn_resumen = resultado["phiMn_val"]
    cumple_resumen = phiMn_resumen >= Mu_resumen

    datos_resumen.append({
        "Sección": nombre,
        "Mu (ton·m)": round(Mu_resumen, 2),
        "As tracción (cm²)": round(As_trac_resumen, 2),
        "As compresión (cm²)": round(As_comp_resumen, 2),
        "φMn (ton·m)": round(phiMn_resumen, 2),
        "Resultado": "✅ CUMPLE" if cumple_resumen else "❌ NO CUMPLE",
    })

st.divider()
st.subheader("📊 Resumen global de verificaciones")

st.dataframe(
    datos_resumen,
    width="stretch",
    hide_index=True
)

# =========================================================
# GRÁFICO DE DEMANDA VS CAPACIDAD
# =========================================================

st.divider()
st.subheader("📈 Demanda vs capacidad de diseño")

st.markdown(
    """
    Se compara el momento último solicitado $M_u$ con la
    capacidad de diseño $\\phi M_n$ de la armadura realmente instalada.
    """
)

# ---------------------------------------------------------
# DEMANDA
# ---------------------------------------------------------

Mu_pos_graf = [
    Mu_pos_izq,
    Mu_pos_cen,
    Mu_pos_der
]

Mu_neg_graf = [
    -Mu_neg_izq,
    -Mu_neg_cen,
    -Mu_neg_der
]

# ---------------------------------------------------------
# CAPACIDAD
# ---------------------------------------------------------

phiMn_pos_graf = [
    verif_pos_izq["phiMn_val"],
    verif_pos_cen["phiMn_val"],
    verif_pos_der["phiMn_val"]
]

phiMn_neg_graf = [
    -verif_neg_izq["phiMn_val"],
    -verif_neg_cen["phiMn_val"],
    -verif_neg_der["phiMn_val"]
]

# ---------------------------------------------------------
# CREACIÓN DEL GRÁFICO
# ---------------------------------------------------------

fig_cap = go.Figure()

# DEMANDA POSITIVA
fig_cap.add_trace(
    go.Scatter(
        x=x,
        y=Mu_pos_graf,
        mode="lines+markers",
        name="Mu (+)",
        line=dict(
            width=3
        ),
        marker=dict(
            size=8
        )
    )
)

# DEMANDA NEGATIVA
fig_cap.add_trace(
    go.Scatter(
        x=x,
        y=Mu_neg_graf,
        mode="lines+markers",
        name="Mu (-)",
        line=dict(
            width=3
        ),
        marker=dict(
            size=8
        )
    )
)

# CAPACIDAD POSITIVA
fig_cap.add_trace(
    go.Scatter(
        x=x,
        y=phiMn_pos_graf,
        mode="lines+markers",
        name="φMn (+)",
        line=dict(
            width=2,
            dash="dash"
        ),
        marker=dict(
            size=7
        )
    )
)

# CAPACIDAD NEGATIVA
fig_cap.add_trace(
    go.Scatter(
        x=x,
        y=phiMn_neg_graf,
        mode="lines+markers",
        name="φMn (-)",
        line=dict(
            width=2,
            dash="dash"
        ),
        marker=dict(
            size=7
        )
    )
)

# ---------------------------------------------------------
# EJE M = 0
# ---------------------------------------------------------

fig_cap.add_hline(
    y=0,
    line_width=2,
    line_dash="dash"
)

# ---------------------------------------------------------
# FORMATO
# ---------------------------------------------------------

fig_cap.update_layout(
    xaxis_title="Longitud del tramo (m)",
    yaxis_title="Momento (ton·m)",
    xaxis=dict(
        tickmode="array",
        tickvals=x,
        ticktext=[
            "Izquierda",
            "Centro",
            "Derecha"
        ]
    ),
    yaxis=dict(
        autorange="reversed"
    ),
    hovermode="x unified",
    height=550
)

st.plotly_chart(
    fig_cap,
    width="stretch"
)


