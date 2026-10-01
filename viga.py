import math
import pandas as pd

def calculoFlexion(
    b,
    h,
    fc,
    fy,
    Es,
    Ecu,
    phiFlexion,
    acero,
    r
):
    """
    Análisis de una sección rectangular simplemente reforzada.

    Metodología:
    1. Se asume inicialmente que el acero a tracción fluye:
    fs = fy
    2. Se obtiene el bloque de compresión y la posición del eje neutro.
    3. Se calcula Mn y phiMn.
    4. Finalmente se verifica la fluencia real del acero a tracción
    mediante compatibilidad de deformaciones.
    """

    # ---------------------------------------------------------
    # 1. FACTOR BETA1
    # ---------------------------------------------------------
    if fc <= 280:
        beta1 = 0.85
    elif fc <= 560:
        beta1 = round(1.05 - 0.714 * (fc / 1000), 3)
    else:
        beta1 = 0.65

    # ---------------------------------------------------------
    # 2. PERALTE EFECTIVO
    # ---------------------------------------------------------
    d = h - r

    # ---------------------------------------------------------
    # 3. DEFORMACIÓN DE FLUENCIA DEL ACERO
    # ---------------------------------------------------------
    eps_y = fy / Es

    # ---------------------------------------------------------
    # 4. EJE NEUTRO BALANCEADO
    # ---------------------------------------------------------
    cb = d * Ecu / (Ecu + eps_y)
    ab = beta1 * cb

    # ---------------------------------------------------------
    # 5. ACERO MÍNIMO, BALANCEADO Y MÁXIMO
    # ---------------------------------------------------------
    aceroMinimo = (
        0.7 * math.sqrt(fc) / fy * b * d
    )

    aceroBalanceado = (
        0.85 * fc * b * ab / fy
    )

    aceroMaximo = 0.75 * aceroBalanceado

    # ---------------------------------------------------------
    # 6. DISEÑO / ANÁLISIS ASUMIENDO QUE EL ACERO FLUYE
    # ---------------------------------------------------------
    #
    # Hipótesis inicial:
    #     fs = fy
    #
    T = acero * fy

    # Equilibrio:
    #
    #     Cc = T
    #
    #     0.85 fc b a = As fy
    #
    a = T / (0.85 * fc * b)

    c = a / beta1

    # ---------------------------------------------------------
    # 7. VERIFICACIÓN DE COMPATIBILIDAD
    # ---------------------------------------------------------
    #
    # Deformación del acero a tracción:
    #
    #     eps_s = Ecu (d-c)/c
    #
    if c > 0:
        eps_s = Ecu * (d - c) / c
    else:
        eps_s = 0.0

    # Esfuerzo real del acero según modelo elastoplástico
    fs = min(Es * eps_s, fy)

    # Verificación de fluencia
    fluye_traccion = eps_s >= eps_y

    # ---------------------------------------------------------
    # 8. FUERZAS INTERNAS
    # ---------------------------------------------------------
    #
    # Si la hipótesis fs = fy fue correcta:
    #
    #     T = As fy
    #
    # En caso contrario, la fuerza real de acero es As fs.
    #
    T_real = acero * fs

    Cc = 0.85 * fc * b * a

    # ---------------------------------------------------------
    # 9. MOMENTO NOMINAL
    # ---------------------------------------------------------
    #
    # Para el diseño bajo la hipótesis de fluencia:
    #
    #     Mn = T(d-a/2)
    #
    Mn = T * (d - a / 2) / (1000 * 100)

    phiMn = phiFlexion * Mn

    # ---------------------------------------------------------
    # 10. TIPO DE FALLA
    # ---------------------------------------------------------
    #
    # La clasificación se hace con la deformación del acero.
    #
    if eps_s >= 0.005:
        tipoFalla = "Tracción"
    elif eps_s > eps_y:
        tipoFalla = "Tracción (fluye)"
    elif eps_s >= 0:
        tipoFalla = "Compresión"
    else:
        tipoFalla = "Compresión"

    # ---------------------------------------------------------
    # 11. RESULTADOS
    # ---------------------------------------------------------
    resultado = {
        # Parámetros geométricos
        "beta1": beta1,
        "d": d,
        "a_val": a,
        "c_val": c,
        "cb_val": cb,

        # Aceros
        "aceroMinimo_val": aceroMinimo,
        "aceroBalanceado_val": aceroBalanceado,
        "aceroMaximo_val": aceroMaximo,

        # Deformaciones y esfuerzos
        "eps_y": eps_y,
        "defAs": eps_s,
        "fs_val": fs,
        "fluye_traccion": fluye_traccion,

        # Fuerzas
        "T_val": T_real,
        "Cc_val": Cc / 1000,   # tonf

        # Momentos
        "Mn_val": Mn,
        "phiMn_val": phiMn,

        # Texto formateado
        "cb": f"{cb:.2f} cm",
        "aceroMinimo": f"{aceroMinimo:.2f} cm²",
        "aceroBalanceado": f"{aceroBalanceado:.2f} cm²",
        "aceroMaximo": f"{aceroMaximo:.2f} cm²",
        "a": f"{a:.2f} cm",
        "c": f"{c:.2f} cm",
        "Mn": f"{Mn:.2f} ton·m",
        "phiMn": f"{phiMn:.2f} ton·m",
        "tipoFalla": tipoFalla,
        "Cc": f"{Cc / 1000:.2f} tonf",
        "eps_y_text": f"{eps_y:.6f}",
        "eps_s_text": f"{eps_s:.6f}",
        "fs": f"{fs:.2f} kg/cm²"
    }

    return resultado

def propiedades_minimo_flexion(
    b,
    h,
    fc,
    fy,
    d,
    phi
):
    """
    Verificaciones asociadas al acero mínimo de flexión
    según E.060 10.5.1 y 10.5.2.

    Unidades:
        b, h, d : cm
        fc, fy  : kg/cm²
        momentos: ton·m
    """

    # =========================================================
    # 1. PROPIEDADES DE LA SECCIÓN BRUTA
    # =========================================================

    Ig = b * h**3 / 12.0

    yt = h / 2.0

    # =========================================================
    # 2. RESISTENCIA A TRACCIÓN POR FLEXIÓN DEL CONCRETO
    # =========================================================

    fr = 2 * math.sqrt(fc)

    # =========================================================
    # 3. MOMENTO DE AGRIETAMIENTO
    # =========================================================

    Mcr_kgcm = (
        fr * Ig / yt
    )

    Mcr = Mcr_kgcm / (1000 * 100)

    # =========================================================
    # 4. MOMENTO MÍNIMO REQUERIDO
    # =========================================================

    Mcr_12 = 1.2 * Mcr

    Mn_objetivo = Mcr_12 / phi

    Mn_objetivo_kgcm = (
        Mn_objetivo
        * 1000
        * 100
    )

    # =========================================================
    # 5. ACERO MÍNIMO SEGÚN E.060 10.5.2
    # =========================================================

    As_min_10_5_2 = (
        0.7
        * math.sqrt(fc)
        / fy
        * b
        * d
    )

    # =========================================================
    # 6. ACERO NECESARIO PARA φMn ≥ 1.2 Mcr
    # =========================================================

    radicando = (
        d**2
        - (
            2.0
            * Mn_objetivo_kgcm
            / (0.85 * fc * b)
        )
    )

    if radicando >= 0:

        a_mcr = (
            d
            - math.sqrt(radicando)
        )

        As_1_2Mcr = (
            Mn_objetivo_kgcm
            / (
                fy
                * (d - a_mcr / 2.0)
            )
        )

    else:

        a_mcr = None
        As_1_2Mcr = None

    # =========================================================
    # 7. ACERO MÍNIMO FINAL
    # =========================================================

    if As_1_2Mcr is not None:

        As_min_final = max(
            As_min_10_5_2,
            As_1_2Mcr
        )

    else:

        As_min_final = As_min_10_5_2

    return {
        "Ig_val": Ig,
        "yt_val": yt,
        "fr_val": fr,
        "Mcr_val": Mcr,
        "1_2Mcr_val": Mcr_12,
        "Mn_objetivo_val": Mn_objetivo,
        "As_min_10_5_2_val": As_min_10_5_2,
        "As_1_2Mcr_val": As_1_2Mcr,
        "As_min_final_val": As_min_final,
        "a_mcr_val": a_mcr
    }


def acero_requerido_flexion_simple_formula(
    b,
    h,
    r,
    fc,
    fy,
    Es,
    Ecu,
    phi,
    Mu
):
    """
    Diseño de una sección rectangular simplemente reforzada
    siguiendo la secuencia de diseño utilizada por Ottazzi:

            Mu
            ↓
            Ku
            ↓
            a
            ↓
            As
            ↓
    As_min / As_max
            ↓
    verificación de fluencia del acero a tracción

    Se asume inicialmente que el acero de tracción fluye:
        fs = fy

    Posteriormente se verifica mediante compatibilidad:
        eps_s >= eps_y
    """

    # =========================================================
    # 1. BETA 1
    # =========================================================

    if fc <= 280:
        beta1 = 0.85

    elif fc <= 560:
        beta1 = round(
            1.05 - 0.714 * (fc / 1000),
            3
        )

    else:
        beta1 = 0.65

    # =========================================================
    # 2. PERALTE EFECTIVO
    # =========================================================

    d = h - r

    # =========================================================
    # 3. DEFORMACIÓN DE FLUENCIA
    # =========================================================

    eps_y = fy / Es

    # =========================================================
    # 4. MOMENTO NOMINAL REQUERIDO
    # =========================================================

    Mn_req = Mu / phi

    # =========================================================
    # 5. CONVERSIÓN DE UNIDADES
    # =========================================================
    #
    # ton·m → kgf·cm
    #

    Mn_req_kgcm = Mn_req * 1000 * 100

    # =========================================================
    # 6. PARÁMETRO Ku
    # =========================================================
    #
    # Ku =
    #
    # Mu
    # ----------------------------
    # phi 0.85 fc b d²
    #
    # usando Mn = Mu / phi
    #

    Ku = (
        Mn_req_kgcm
        / (0.85 * fc * b * d**2)
    )

    # =========================================================
    # 7. RADICANDO
    # =========================================================
    #
    # a = d - sqrt(
    #         d² -
    #         2Mn/(0.85 fc b)
    #     )
    #

    radicando = (
        d**2
        - (
            2 * Mn_req_kgcm
            / (0.85 * fc * b)
        )
    )

    # =========================================================
    # 8. ACERO MÍNIMO DE FLEXIÓN
    # =========================================================

    minimo_flexion = propiedades_minimo_flexion(
        b=b,
        h=h,
        fc=fc,
        fy=fy,
        d=d,
        phi=phi
    )

    As_min_10_5_2 = (
        minimo_flexion["As_min_10_5_2_val"]
    )

    As_1_2Mcr = (
        minimo_flexion["As_1_2Mcr_val"]
    )

    As_min = (
        minimo_flexion["As_min_final_val"]
    )
    # =========================================================
    # 9. ACERO BALANCEADO
    # =========================================================

    cb = (
        d
        * Ecu
        / (Ecu + eps_y)
    )

    ab = beta1 * cb

    As_bal = (
        0.85
        * fc
        * b
        * ab
        / fy
    )

    # =========================================================
    # 10. ACERO MÁXIMO
    # =========================================================

    As_max = 0.75 * As_bal

    # =========================================================
    # 11. SI NO EXISTE SOLUCIÓN REAL
    # =========================================================

    if radicando < 0:

        return {

            "valido": True,
            "requiere_doble": True,
            "supera_As_max": True,

            "mensaje": (
                "La ecuación de diseño simple no tiene "
                "solución real para el momento solicitado. "
                "Se requiere diseño doblemente reforzado."
            ),

            # Geometría
            "beta1": beta1,
            "d": d,
            "cb_val": cb,
            "ab_val": ab,

            # Diseño
            "Ku_val": Ku,
            "radicando_val": radicando,

            # Momentos
            "Mu_val": Mu,
            "Mn_req_val": Mn_req,

            # Aceros de referencia
            "As_min_val": As_min,
            "As_bal_val": As_bal,
            "As_max_val": As_max,

            # No existe As simple
            "As_flexion_val": None,
            "As_diseno_val": None,

            # Fluencia no evaluable todavía
            "fluye_traccion": None,

            # Textos
            "d_text": f"{d:.2f} cm",
            "cb_text": f"{cb:.2f} cm",

            "Ku_text": f"{Ku:.5f}",

            "As_min_text": (
                f"{As_min:.2f} cm²"
            ),

            "As_bal_text": (
                f"{As_bal:.2f} cm²"
            ),

            "As_max_text": (
                f"{As_max:.2f} cm²"
            ),

            "mensaje_detallado": (
                f"El radicando de la ecuación para "
                f"el bloque de compresión es negativo "
                f"({radicando:.4f})."
            )
        }

    # =========================================================
    # 12. PROFUNDIDAD DEL BLOQUE DE COMPRESIÓN
    # =========================================================

    a = (
        d
        - math.sqrt(radicando)
    )

    # =========================================================
    # 13. ÁREA DE ACERO REQUERIDA
    # =========================================================
    #
    # As =
    #
    # Mu
    # -----------------------
    # phi fy (d - a/2)
    #

    As_flexion = (
        Mu * 1000 * 100
        /
        (
            phi
            * fy
            * (d - a / 2)
        )
    )

    # =========================================================
    # 14. ACERO DE DISEÑO
    # =========================================================

    As_diseno = max(
        As_flexion,
        As_min
    )

    # =========================================================
    # 15. EJE NEUTRO
    # =========================================================

    c = a / beta1

    # =========================================================
    # 16. DEFORMACIÓN DEL ACERO
    # =========================================================

    eps_s = (
        Ecu
        * (d - c)
        / c
    )

    # =========================================================
    # 17. ESFUERZO DEL ACERO
    # =========================================================

    fs = min(
        Es * eps_s,
        fy
    )

    # =========================================================
    # 18. VERIFICACIÓN DE FLUENCIA
    # =========================================================

    fluye_traccion = (
        eps_s >= eps_y
    )

    # =========================================================
    # 19. VERIFICACIÓN As MÁXIMO
    # =========================================================

    supera_As_max = (
        As_diseno > As_max
    )

    # =========================================================
    # 20. MOMENTO CALCULADO
    # =========================================================

    Mn_calculado = (
        As_flexion
        * fy
        * (d - a / 2)
        / (1000 * 100)
    )

    phiMn_calculado = (
        phi
        * Mn_calculado
    )

    # =========================================================
    # 21. ESTADO DEL DISEÑO
    # =========================================================

    if supera_As_max:

        tipo_diseno = (
            "Doble refuerzo requerido"
        )

        requiere_doble = True

    elif not fluye_traccion:

        tipo_diseno = (
            "Verificar hipótesis de fluencia"
        )

        requiere_doble = False

    else:

        tipo_diseno = (
            "Simplemente reforzada"
        )

        requiere_doble = False

    # =========================================================
    # 22. RESULTADOS
    # =========================================================

    return {

        # -----------------------------------------------------
        # Estado
        # -----------------------------------------------------

        "valido": True,

        "requiere_doble": requiere_doble,

        "tipo_diseno": tipo_diseno,

        "supera_As_max": supera_As_max,

        # -----------------------------------------------------
        # Geometría
        # -----------------------------------------------------

        "beta1": beta1,

        "d": d,

        "a_val": a,

        "c_val": c,

        "cb_val": cb,

        # -----------------------------------------------------
        # Parámetros de diseño
        # -----------------------------------------------------

        "Ku_val": Ku,

        "radicando_val": radicando,

        # -----------------------------------------------------
        # Momentos
        # -----------------------------------------------------

        "Mu_val": Mu,

        "Mn_req_val": Mn_req,

        "Mn_calculado_val": Mn_calculado,

        "phiMn_calculado_val": phiMn_calculado,

        # -----------------------------------------------------
        # Aceros
        # -----------------------------------------------------

        "As_flexion_val": As_flexion,

        "As_diseno_val": As_diseno,

        "As_min_val": As_min,

        "Ig_val": minimo_flexion["Ig_val"],
        "yt_val": minimo_flexion["yt_val"],
        "fr_val": minimo_flexion["fr_val"],
        "Mcr_val": minimo_flexion["Mcr_val"],
        "1_2Mcr_val": minimo_flexion["1_2Mcr_val"],
        "Mn_objetivo_1_2Mcr_val": minimo_flexion["Mn_objetivo_val"],
        "As_min_10_5_2_val": minimo_flexion["As_min_10_5_2_val"],
        "As_1_2Mcr_val": minimo_flexion["As_1_2Mcr_val"],

        "As_bal_val": As_bal,

        "As_max_val": As_max,

        # -----------------------------------------------------
        # Deformaciones
        # -----------------------------------------------------

        "eps_y": eps_y,

        "eps_s": eps_s,

        # -----------------------------------------------------
        # Esfuerzo
        # -----------------------------------------------------

        "fs_val": fs,

        # -----------------------------------------------------
        # Fluencia
        # -----------------------------------------------------

        "fluye_traccion": fluye_traccion,

        # -----------------------------------------------------
        # Formato
        # -----------------------------------------------------

        "d_text": f"{d:.2f} cm",

        "a_text": f"{a:.2f} cm",

        "c_text": f"{c:.2f} cm",

        "cb_text": f"{cb:.2f} cm",

        "Ku_text": f"{Ku:.5f}",

        "Mn_req_text": (
            f"{Mn_req:.2f} ton·m"
        ),

        "As_flexion_text": (
            f"{As_flexion:.2f} cm²"
        ),

        "As_diseno_text": (
            f"{As_diseno:.2f} cm²"
        ),

        "As_min_text": (
            f"{As_min:.2f} cm²"
        ),

        "As_bal_text": (
            f"{As_bal:.2f} cm²"
        ),

        "As_max_text": (
            f"{As_max:.2f} cm²"
        ),

        "eps_y_text": (
            f"{eps_y:.6f}"
        ),

        "eps_s_text": (
            f"{eps_s:.6f}"
        ),

        "fs_text": (
            f"{fs:.2f} kg/cm²"
        )
    }


tablaAceros = pd.DataFrame(
    {
        "Diametro": [
            "6mm",
            '1/4"',
            "8mm",
            '3/8"',
            "12mm",
            '1/2"',
            '5/8"',
            '3/4"',
            '1"',
            '1 3/8"',
        ],
        "Área(cm2)": [0.28, 0.32, 0.5, 0.71, 1.13, 1.29, 2, 2.84, 5.1, 10.06],
    }
)
#tablaAceros = tablaAceros.set_index("Diametro")

def areaAs (numero, diametro):
    return numero * tablaAceros.loc[tablaAceros['Diametro'] == diametro, "Área(cm2)"].values[0] 


def ancho_minimo_acero(
    grupos_acero,
    recubrimiento=4.0,
    diam_estribo='3/8"',
    sep_min_aci=2.54
):
    """
    Calcula el ancho mínimo necesario para alojar las barras
    de una capa, siguiendo:

        b_min =
        2(recubrimiento + d_estribo)
        + (n - 1) sep_min
        + suma(n_i * db_i)

    grupos_acero:
        lista de tuplas (n_barras, diametro_str)

    recubrimiento:
        recubrimiento libre en cm.

    diam_estribo:
        diámetro nominal del estribo.

    sep_min_aci:
        separación libre mínima entre barras en cm.
    """

    # ---------------------------------------------------------
    # DIÁMETROS NOMINALES DE BARRAS EN cm
    # ---------------------------------------------------------

    diametros_nominales_cm = {
        "8mm": 0.80,
        "8 mm": 0.80,
        '3/8"': 0.95,
        '1/2"': 1.27,
        '5/8"': 1.59,
        '3/4"': 1.91,
        '1"': 2.54,
        '1 3/8"': 3.58
    }

    # ---------------------------------------------------------
    # VALIDAR DIÁMETRO DEL ESTRIBO
    # ---------------------------------------------------------

    if diam_estribo not in diametros_nominales_cm:
        raise ValueError(
            f"No se encontró el diámetro del estribo "
            f"'{diam_estribo}'."
        )

    db_estribo = diametros_nominales_cm[diam_estribo]

    # ---------------------------------------------------------
    # SUMAR BARRAS Y DIÁMETROS
    # ---------------------------------------------------------

    n_total = 0
    suma_diametros = 0.0

    for numero, diametro_str in grupos_acero:

        if numero <= 0:
            continue

        if diametro_str not in diametros_nominales_cm:
            raise ValueError(
                f"No se encontró el diámetro "
                f"'{diametro_str}'."
            )

        db = diametros_nominales_cm[diametro_str]

        n_total += numero
        suma_diametros += numero * db

    # ---------------------------------------------------------
    # SI NO HAY BARRAS
    # ---------------------------------------------------------

    if n_total == 0:
        return 0.0, 0

    # ---------------------------------------------------------
    # ANCHO MÍNIMO NECESARIO
    # ---------------------------------------------------------

    ancho_recubrimiento_estribo = (
        2 * (recubrimiento + db_estribo)
    )

    ancho_separaciones = (
        (n_total - 1) * sep_min_aci
    )

    b_min = (
        ancho_recubrimiento_estribo
        + ancho_separaciones
        + suma_diametros
    )

    return round(b_min, 2), n_total


def calculoFlexionDoble(
    b,
    h,
    fc,
    fy,
    Es,
    Ecu,
    phiFlexion,
    As_trac,
    As_comp,
    r_trac,
    r_comp
):
    """
    VERIFICACIÓN de una sección rectangular doblemente reforzada.

    Se conocen:
        As_trac = acero total a tracción
        As_comp = acero a compresión

    Se determina c mediante equilibrio de fuerzas y compatibilidad
    de deformaciones.

    Para ambos aceros se usa un modelo elastoplástico:

        fs = min(Es * eps_s, fy)

        fs' = min(Es * eps_s', fy)

    Por lo tanto, la fluencia de cada acero se VERIFICA después
    de obtener la posición del eje neutro.

    Esta función NO diseña el acero.
    Su función es verificar la sección finalmente seleccionada.
    """

    # =========================================================
    # 1. FACTOR BETA1
    # =========================================================
    if fc <= 280:
        beta1 = 0.85
    elif fc <= 560:
        beta1 = round(1.05 - 0.714 * (fc / 1000), 3)
    else:
        beta1 = 0.65

    # =========================================================
    # 2. PERALTES EFECTIVOS
    # =========================================================
    d = h - r_trac
    d_comp = r_comp

    # =========================================================
    # 3. DEFORMACIÓN DE FLUENCIA
    # =========================================================
    eps_y = fy / Es

    # =========================================================
    # 4. FUNCIONES INTERNAS
    # =========================================================

    def esfuerzo_traccion(eps_s):
        """
        Esfuerzo del acero a tracción.
        Modelo elastoplástico.
        """
        if eps_s <= 0:
            return 0.0

        return min(Es * eps_s, fy)

    def esfuerzo_compresion(eps_sp):
        """
        Esfuerzo del acero a compresión.
        Modelo elastoplástico.
        """
        if eps_sp <= 0:
            return 0.0

        return min(Es * eps_sp, fy)

    def equilibrio(c):
        """
        Función de equilibrio:

            Cc + Cs - T = 0

        donde:

            Cc = compresión del concreto
            Cs = compresión del acero superior
            T  = tracción del acero inferior
        """

        if c <= 0:
            return -As_trac * fy

        # ---------------------------------------------
        # Deformación acero de tracción
        # ---------------------------------------------
        eps_s = Ecu * (d - c) / c

        if eps_s > 0:
            fs = esfuerzo_traccion(eps_s)
        else:
            fs = 0.0

        # ---------------------------------------------
        # Deformación acero de compresión
        # ---------------------------------------------
        if c > d_comp:

            eps_sp = Ecu * (c - d_comp) / c

            fsp = esfuerzo_compresion(eps_sp)

        else:

            eps_sp = 0.0
            fsp = 0.0

        # ---------------------------------------------
        # Fuerzas
        # ---------------------------------------------
        T = As_trac * fs

        a = beta1 * c

        Cc = 0.85 * fc * b * a

        Cs = As_comp * fsp

        return Cc + Cs - T

    # =========================================================
    # 5. BUSCAR INTERVALO PARA c
    # =========================================================
    #
    # Para c -> 0:
    #     C < T
    #
    # Para c grande:
    #     C > T
    #
    # por lo que buscamos un cambio de signo.
    #

    c_min = 1e-6
    c_max = max(d * 2.0, h * 2.0)

    f_min = equilibrio(c_min)
    f_max = equilibrio(c_max)

    # Ampliar intervalo si fuese necesario
    contador = 0

    while f_min * f_max > 0 and contador < 20:

        c_max *= 2.0
        f_max = equilibrio(c_max)
        contador += 1

    if f_min * f_max > 0:

        return {
            "valido": False,
            "mensaje": (
                "No se pudo encontrar una posición del eje neutro "
                "que satisfaga el equilibrio de fuerzas."
            )
        }

    # =========================================================
    # 6. SOLUCIÓN NUMÉRICA DE c
    # =========================================================
    #
    # Método de bisección.
    #
    # No requiere librerías externas y es muy estable para
    # esta ecuación de equilibrio.
    #

    for _ in range(200):

        c = (c_min + c_max) / 2.0

        f_c = equilibrio(c)

        if abs(f_c) < 1e-7:
            break

        if f_min * f_c < 0:

            c_max = c
            f_max = f_c

        else:

            c_min = c
            f_min = f_c

    # =========================================================
    # 7. BLOQUE DE COMPRESIÓN
    # =========================================================
    a = beta1 * c

    # =========================================================
    # 8. DEFORMACIÓN DEL ACERO A TRACCIÓN
    # =========================================================
    eps_s = Ecu * (d - c) / c

    if eps_s > 0:
        fs = esfuerzo_traccion(eps_s)
    else:
        fs = 0.0

    # =========================================================
    # 9. DEFORMACIÓN DEL ACERO A COMPRESIÓN
    # =========================================================
    if c > d_comp:

        eps_sp = Ecu * (c - d_comp) / c

        fsp = esfuerzo_compresion(eps_sp)

    else:

        eps_sp = 0.0
        fsp = 0.0

    # =========================================================
    # 10. VERIFICACIÓN DE FLUENCIA
    # =========================================================

    fluye_traccion = eps_s >= eps_y
    fluye_compresion = eps_sp >= eps_y

    # =========================================================
    # 11. FUERZAS INTERNAS
    # =========================================================

    T = As_trac * fs

    Cc = 0.85 * fc * b * a

    Cs = As_comp * fsp

    # =========================================================
    # 12. VERIFICACIÓN DEL EQUILIBRIO
    # =========================================================

    error_equilibrio = (Cc + Cs) - T

    # =========================================================
    # 13. MOMENTO NOMINAL
    # =========================================================
    #
    # Momento respecto al centroide del acero de tracción:
    #
    # Mn = Cc(d-a/2) + Cs(d-d')
    #

    Mn = (
        Cc * (d - a / 2)
        + Cs * (d - d_comp)
    ) / (1000 * 100)

    phiMn = phiFlexion * Mn

    # =========================================================
    # 14. PROPIEDADES DE ACERO MÍNIMO
    # =========================================================

    minimo_flexion = propiedades_minimo_flexion(
        b=b,
        h=h,
        fc=fc,
        fy=fy,
        d=d,
        phi=phiFlexion
    )

    As_min = minimo_flexion["As_min_final_val"]

    # =========================================================
    # 15. ACERO BALANCEADO
    # =========================================================

    cb = d * Ecu / (Ecu + eps_y)

    ab = beta1 * cb

    As_bal = (
        0.85 * fc * b * ab / fy
    )

    # =========================================================
    # 16. LÍMITE DE ACERO MÁXIMO PARA DOBLE REFUERZO
    # =========================================================
    #
    # Expresión:
    #
    # As,max = 0.75 As_bal + As' fs'/fy
    #
    As_max_doble = (
        0.75 * As_bal
        + As_comp * fsp / fy
    )

    # =========================================================
    # 17. ESTADO GENERAL DE LA SECCIÓN
    # =========================================================

    if fluye_traccion:

        estado_traccion = "El acero a TRACCIÓN FLUYE"

    else:

        estado_traccion = "El acero a TRACCIÓN NO FLUYE"

    if fluye_compresion:

        estado_compresion = "El acero a COMPRESIÓN FLUYE"

    else:

        estado_compresion = "El acero a COMPRESIÓN NO FLUYE"

    # =========================================================
    # 18. RESULTADO
    # =========================================================

    resultado = {

        # -----------------------------------------------------
        # Estado
        # -----------------------------------------------------

        "valido": True,

        "mensaje_traccion": estado_traccion,

        "mensaje_compresion": estado_compresion,

        # -----------------------------------------------------
        # Geometría
        # -----------------------------------------------------

        "beta1": beta1,

        "d": d,

        "d_comp": d_comp,

        "a_val": a,

        "c_val": c,

        "cb_val": cb,

        # -----------------------------------------------------
        # Deformaciones
        # -----------------------------------------------------

        "eps_y": eps_y,

        "eps_s_val": eps_s,

        "eps_sp_val": eps_sp,

        # -----------------------------------------------------
        # Esfuerzos
        # -----------------------------------------------------

        "fs_val": fs,

        "fs_p_val": fsp,

        # -----------------------------------------------------
        # Fluencia
        # -----------------------------------------------------

        "fluye_traccion": fluye_traccion,

        "fluye_compresion": fluye_compresion,

        # -----------------------------------------------------
        # Fuerzas
        # -----------------------------------------------------

        "T_val": T,

        "Cc_val": Cc / 1000,

        "Cs_val": Cs / 1000,

        "error_equilibrio_val": error_equilibrio / 1000,

        # -----------------------------------------------------
        # Momentos
        # -----------------------------------------------------

        "Mn_val": Mn,

        "phiMn_val": phiMn,

        # -----------------------------------------------------
        # Aceros de referencia
        # -----------------------------------------------------

        "As_min_val": As_min,

        "As_bal_val": As_bal,

        "As_max_doble_val": As_max_doble,

        # -----------------------------------------------------
        # Formato para interfaz
        # -----------------------------------------------------

        "d_text": f"{d:.2f} cm",

        "d_comp_text": f"{d_comp:.2f} cm",

        "a_text": f"{a:.2f} cm",

        "c_text": f"{c:.2f} cm",

        "cb_text": f"{cb:.2f} cm",

        "eps_y_text": f"{eps_y:.6f}",

        "eps_s_text": f"{eps_s:.6f}",

        "eps_sp_text": f"{eps_sp:.6f}",

        "fs_text": f"{fs:.2f} kg/cm²",

        "fs_p_text": f"{fsp:.2f} kg/cm²",

        "T_text": f"{T / 1000:.2f} tonf",

        "Cc_text": f"{Cc / 1000:.2f} tonf",

        "Cs_text": f"{Cs / 1000:.2f} tonf",

        "Mn_text": f"{Mn:.2f} ton·m",

        "phiMn_text": f"{phiMn:.2f} ton·m",

        "As_min_text": f"{As_min:.2f} cm²",

        "As_bal_text": f"{As_bal:.2f} cm²",

        "As_max_doble_text": f"{As_max_doble:.2f} cm²",
    }

    return resultado

def calculoFlexionDobleCapas(
    b,
    h,
    fc,
    fy,
    Es,
    Ecu,
    phiFlexion,
    capas_trac,
    capas_comp
):
    """
    Verificación de flexión con una o dos capas reales
    de acero a tracción y compresión.

    Cada capa se define como:
        {
            "nombre": ...,
            "r": ...,
            "As": ...
        }

    r se mide desde la cara correspondiente.
    """

    # =========================================================
    # 1. FACTOR BETA 1
    # =========================================================

    if fc <= 280:
        beta1 = 0.85

    elif fc <= 560:
        beta1 = round(
            1.05 - 0.714 * (fc / 1000),
            3
        )

    else:
        beta1 = 0.65

    # =========================================================
    # 2. DEFORMACIÓN DE FLUENCIA
    # =========================================================

    eps_y = fy / Es

    # =========================================================
    # 3. PROFUNDIDADES DE LAS CAPAS
    # =========================================================

    capas_trac_calc = []

    for capa in capas_trac:

        d_i = h - capa["r"]

        capas_trac_calc.append(
            {
                "nombre": capa["nombre"],
                "r": capa["r"],
                "As": capa["As"],
                "d": d_i
            }
        )

    capas_comp_calc = []

    for capa in capas_comp:

        d_i = capa["r"]

        capas_comp_calc.append(
            {
                "nombre": capa["nombre"],
                "r": capa["r"],
                "As": capa["As"],
                "d": d_i
            }
        )

    # Capa de tracción más alejada del borde comprimido
    d_extremo = max(
        capa["d"]
        for capa in capas_trac_calc
    )

    # Capa de compresión más cercana al borde comprimido
    d_comp_extremo = min(
        capa["d"]
        for capa in capas_comp_calc
    )

    # =========================================================
    # 4. FUNCIONES CONSTITUTIVAS
    # =========================================================

    def esfuerzo_acero(eps):

        if eps <= 0:
            return 0.0

        return min(
            Es * eps,
            fy
        )

    # =========================================================
    # 5. EQUILIBRIO
    # =========================================================

    def equilibrio(c):

        if c <= 0:
            return -fy * sum(
                capa["As"]
                for capa in capas_trac_calc
            )

        a = beta1 * c

        Cc = 0.85 * fc * b * a

        T_total = 0.0
        C_total = 0.0

        # -----------------------------------------------------
        # TRACCIÓN
        # -----------------------------------------------------

        for capa in capas_trac_calc:

            eps_s = Ecu * (
                capa["d"] - c
            ) / c

            fs = esfuerzo_acero(eps_s)

            T_total += capa["As"] * fs

        # -----------------------------------------------------
        # COMPRESIÓN
        # -----------------------------------------------------

        for capa in capas_comp_calc:

            if c > capa["d"]:

                eps_sp = Ecu * (
                    c - capa["d"]
                ) / c

                fs_p = esfuerzo_acero(eps_sp)

            else:

                fs_p = 0.0

            C_total += capa["As"] * fs_p

        return Cc + C_total - T_total

    # =========================================================
    # 6. INTERVALO PARA c
    # =========================================================

    c_min = 1e-6
    c_max = max(
        2.0 * d_extremo,
        2.0 * h
    )

    f_min = equilibrio(c_min)
    f_max = equilibrio(c_max)

    contador = 0

    while (
        f_min * f_max > 0
        and contador < 20
    ):

        c_max *= 2.0
        f_max = equilibrio(c_max)
        contador += 1

    if f_min * f_max > 0:

        return {
            "valido": False,
            "mensaje": (
                "No se pudo encontrar una posición "
                "del eje neutro que satisfaga "
                "el equilibrio."
            )
        }

    # =========================================================
    # 7. BISECCIÓN
    # =========================================================

    c = None

    for _ in range(200):

        c = (
            c_min
            + c_max
        ) / 2.0

        f_c = equilibrio(c)

        if abs(f_c) < 1e-7:
            break

        if f_min * f_c < 0:

            c_max = c
            f_max = f_c

        else:

            c_min = c
            f_min = f_c

    # =========================================================
    # 8. BLOQUE DE COMPRESIÓN
    # =========================================================

    a = beta1 * c

    Cc = 0.85 * fc * b * a

    # =========================================================
    # 9. DEFORMACIONES Y FUERZAS POR CAPA
    # =========================================================

    T_total = 0.0
    C_total = 0.0

    capas_traccion_resultado = []
    capas_compresion_resultado = []

    # ---------------------------------------------------------
    # TRACCIÓN
    # ---------------------------------------------------------

    for capa in capas_trac_calc:

        eps_s = (
            Ecu
            * (capa["d"] - c)
            / c
        )

        if eps_s > 0:

            fs = esfuerzo_acero(eps_s)

        else:

            fs = 0.0

        T_i = capa["As"] * fs

        T_total += T_i

        capas_traccion_resultado.append(
            {
                "nombre": capa["nombre"],
                "As": capa["As"],
                "r": capa["r"],
                "d": capa["d"],
                "eps": eps_s,
                "fs": fs,
                "T": T_i,
                "fluye": eps_s >= eps_y
            }
        )

    # ---------------------------------------------------------
    # COMPRESIÓN
    # ---------------------------------------------------------

    for capa in capas_comp_calc:

        if c > capa["d"]:

            eps_sp = (
                Ecu
                * (c - capa["d"])
                / c
            )

            fs_p = esfuerzo_acero(eps_sp)

        else:

            eps_sp = 0.0
            fs_p = 0.0

        C_i = capa["As"] * fs_p

        C_total += C_i

        capas_compresion_resultado.append(
            {
                "nombre": capa["nombre"],
                "As": capa["As"],
                "r": capa["r"],
                "d": capa["d"],
                "eps": eps_sp,
                "fs": fs_p,
                "C": C_i,
                "fluye": eps_sp >= eps_y
            }
        )

    # =========================================================
    # 10. DEFORMACIÓN EXTREMA DE TRACCIÓN
    # =========================================================

    capa_extrema = max(
        capas_traccion_resultado,
        key=lambda capa: capa["d"]
    )

    eps_t = capa_extrema["eps"]

    fluye_traccion = (
        eps_t >= eps_y
    )

    fluye_compresion = any(
        capa["fluye"]
        for capa in capas_compresion_resultado
    )

    # =========================================================
    # 11. EQUILIBRIO
    # =========================================================

    error_equilibrio = (
        Cc
        + C_total
        - T_total
    )

    # =========================================================
    # 12. MOMENTO NOMINAL
    # =========================================================
    #
    # Se toman momentos respecto a la fibra comprimida.
    #
    # Tracciones:
    #     Ti * di
    #
    # Compresión del concreto:
    #     Cc * a/2
    #
    # Acero a compresión:
    #     Ci * di
    #
    # =========================================================

    momento_traccion = sum(
        capa["T"] * capa["d"]
        for capa in capas_traccion_resultado
    )

    momento_concreto = (
        Cc * (a / 2.0)
    )

    momento_compresion_acero = sum(
        capa["C"] * capa["d"]
        for capa in capas_compresion_resultado
    )

    Mn_kgcm = (
        momento_traccion
        - momento_concreto
        - momento_compresion_acero
    )

    Mn = Mn_kgcm / (
        1000 * 100
    )

    phiMn = (
        phiFlexion * Mn
    )

    # =========================================================
    # 13. PROPIEDADES DE REFERENCIA
    # =========================================================

    As_total = sum(
        capa["As"]
        for capa in capas_trac_calc
    )

    As_comp_total = sum(
        capa["As"]
        for capa in capas_comp_calc
    )

    minimo_flexion = propiedades_minimo_flexion(
        b=b,
        h=h,
        fc=fc,
        fy=fy,
        d=d_extremo,
        phi=phiFlexion
    )

    As_min = minimo_flexion["As_min_final_val"]

    cb = (
        d_extremo
        * Ecu
        / (Ecu + eps_y)
    )

    ab = beta1 * cb

    As_bal = (
        0.85
        * fc
        * b
        * ab
        / fy
    )

    # =========================================================
    # 14. RESULTADO
    # =========================================================

    return {

        "valido": True,

        "beta1": beta1,

        "d": d_extremo,

        "d_comp": d_comp_extremo,

        "a_val": a,

        "c_val": c,

        "cb_val": cb,

        "eps_y": eps_y,

        "eps_s_val": eps_t,

        "eps_sp_val": max(
            [
                capa["eps"]
                for capa in capas_compresion_resultado
            ],
            default=0.0
        ),

        "fs_val": capa_extrema["fs"],

        "fs_p_val": max(
            [
                capa["fs"]
                for capa in capas_compresion_resultado
            ],
            default=0.0
        ),

        "fluye_traccion": fluye_traccion,

        "fluye_compresion": fluye_compresion,

        "T_val": T_total,

        "Cc_val": Cc / 1000,

        "Cs_val": C_total / 1000,

        "error_equilibrio_val": (
            error_equilibrio / 1000
        ),

        "Mn_val": Mn,

        "phiMn_val": phiMn,

        "As_min_val": As_min,

        "Ig_val": minimo_flexion["Ig_val"],
        "yt_val": minimo_flexion["yt_val"],
        "fr_val": minimo_flexion["fr_val"],
        "Mcr_val": minimo_flexion["Mcr_val"],
        "1_2Mcr_val": minimo_flexion["1_2Mcr_val"],
        "Mn_objetivo_1_2Mcr_val": minimo_flexion["Mn_objetivo_val"],
        "As_min_10_5_2_val": minimo_flexion["As_min_10_5_2_val"],
        "As_1_2Mcr_val": minimo_flexion["As_1_2Mcr_val"],

        "As_bal_val": As_bal,

        "As_max_doble_val": (
            0.75 * As_bal
            + C_total / fy
        ),

        "As_traccion_total": As_total,

        "As_compresion_total": As_comp_total,

        "capas_traccion": (
            capas_traccion_resultado
        ),

        "capas_compresion": (
            capas_compresion_resultado
        ),

        "capa_traccion_extrema": (
            capa_extrema["nombre"]
        )
    }



def disenoFlexionDoble(
    b,
    h,
    fc,
    fy,
    Es,
    Ecu,
    phiFlexion,
    Mu,
    r_trac,
    r_comp
):
    """
    Diseño de una sección rectangular doblemente reforzada
    siguiendo la metodología de diseño utilizada por Ottazzi.

    Procedimiento:

    1. Se calcula As_bal.
    2. Se limita la primera parte del acero de tracción a:
    As1 = 0.75 As_bal
    3. Se calcula la resistencia de diseño asociada:
    phiMn1
    4. Se obtiene el momento residual:
    Mu2 = Mu - phiMn1
    5. Se calcula el acero de tracción adicional As2.
    6. Se calcula la deformación del acero de compresión.
    7. Se verifica si el acero de compresión fluye.
    8. Se calcula As' necesario.
    9. Se obtiene el acero total de tracción:
    As = As1 + As2

    NOTA:
    La función realiza el diseño teórico. La sección final con las
    barras comerciales realmente seleccionadas se verificará posteriormente
    mediante calculoFlexionDoble().
    """

    # =========================================================
    # 1. FACTOR BETA1
    # =========================================================
    if fc <= 280:
        beta1 = 0.85
    elif fc <= 560:
        beta1 = round(1.05 - 0.714 * (fc / 1000), 3)
    else:
        beta1 = 0.65

    # =========================================================
    # 2. PERALTES EFECTIVOS
    # =========================================================
    d = h - r_trac
    d_comp = r_comp

    # =========================================================
    # 3. DEFORMACIÓN DE FLUENCIA
    # =========================================================
    eps_y = fy / Es

    # =========================================================
    # 4. EJE NEUTRO BALANCEADO
    # =========================================================
    cb = d * Ecu / (Ecu + eps_y)
    ab = beta1 * cb

    # =========================================================
    # 5. ACERO BALANCEADO
    # =========================================================
    As_bal = (
        0.85 * fc * b * ab / fy
    )

    # =========================================================
    # 6. ACERO MÁXIMO PARA LA PARTE DE CONCRETO
    # =========================================================
    #
    # Este es el máximo acero de tracción permitido para la
    # primera etapa del procedimiento.
    #
    As1 = 0.75 * As_bal

    # =========================================================
    # 7. BLOQUE DE COMPRESIÓN PARA As1
    # =========================================================
    a1 = (
        As1 * fy
        / (0.85 * fc * b)
    )

    c1 = a1 / beta1

    # =========================================================
    # 8. RESISTENCIA DE LA PRIMERA PARTE
    # =========================================================
    #
    # Mn1 en kgf-cm
    #
    Mn1_kgcm = (
        As1
        * fy
        * (d - a1 / 2)
    )

    # Convertir a ton·m
    Mn1 = Mn1_kgcm / (1000 * 100)

    phiMn1 = phiFlexion * Mn1

    # =========================================================
    # 9. MOMENTO RESIDUAL
    # =========================================================
    #
    # Mu = phiMn1 + Mu2
    #
    Mu2 = Mu - phiMn1

    # =========================================================
    # 10. SI NO HAY MOMENTO RESIDUAL
    # =========================================================
    if Mu2 <= 0:

        return {
            "valido": True,
            "requiere_doble": False,

            "mensaje": (
                "La sección con 0.75 As_bal es suficiente "
                "para resistir el momento solicitado."
            ),

            "beta1": beta1,
            "d": d,
            "d_comp": d_comp,

            "eps_y": eps_y,

            "cb_val": cb,
            "ab_val": ab,

            "As_bal_val": As_bal,
            "As1_val": As1,

            "a1_val": a1,
            "c1_val": c1,

            "Mn1_val": Mn1,
            "phiMn1_val": phiMn1,

            "Mu2_val": 0.0,
            "As2_val": 0.0,
            "As_comp_val": 0.0,

            "eps_sp_val": 0.0,
            "fs_p_val": 0.0,

            "fluye_compresion": False,

            "As_total_val": As1,

            "As_bal_text": f"{As_bal:.2f} cm²",
            "As1_text": f"{As1:.2f} cm²",
            "a1_text": f"{a1:.2f} cm",
            "c1_text": f"{c1:.2f} cm",
            "Mn1_text": f"{Mn1:.2f} ton·m",
            "phiMn1_text": f"{phiMn1:.2f} ton·m",
            "Mu2_text": "0.00 ton·m",
            "As2_text": "0.00 cm²",
            "As_comp_text": "0.00 cm²",
            "eps_sp_text": "0.000000",
            "fs_p_text": "0.00 kg/cm²",
            "As_total_text": f"{As1:.2f} cm²",
        }

    # =========================================================
    # 11. ACERO DE TRACCIÓN ADICIONAL
    # =========================================================
    #
    # Mu2 = phi As2 fy (d - d')
    #
    # Mu2 está en ton-m, por lo que se convierte a kgf-cm.
    #
    Mu2_kgcm = Mu2 * 1000 * 100

    brazo_acero = d - d_comp

    if brazo_acero <= 0:
        return {
            "valido": False,
            "mensaje": (
                "El peralte efectivo del acero de tracción "
                "debe ser mayor que la posición del acero de compresión."
            )
        }

    As2 = (
        Mu2_kgcm
        / (
            phiFlexion
            * fy
            * brazo_acero
        )
    )

    # =========================================================
    # 12. VERIFICACIÓN DEL ACERO DE COMPRESIÓN
    # =========================================================
    #
    # El eje neutro se toma aproximadamente igual al obtenido
    # con As1 = 0.75 As_bal.
    #
    if c1 > d_comp:

        eps_sp = (
            Ecu
            * (c1 - d_comp)
            / c1
        )

    else:
        eps_sp = 0.0

    # Esfuerzo elástico calculado
    fs_p_elastico = Es * eps_sp

    # Esfuerzo limitado por fluencia
    fs_p = min(fs_p_elastico, fy)

    # Verificación de fluencia
    fluye_compresion = eps_sp >= eps_y

    # =========================================================
    # 13. ÁREA DE ACERO DE COMPRESIÓN
    # =========================================================
    #
    # Equilibrio del par adicional:
    #
    # As2 fy = As' fs'
    #
    if fs_p > 0:

        As_comp = (
            As2 * fy / fs_p
        )

    else:

        return {
            "valido": False,
            "mensaje": (
                "La deformación del acero de compresión "
                "no permite determinar un esfuerzo de acero válido."
            )
        }

    # =========================================================
    # 14. ACERO TOTAL DE TRACCIÓN
    # =========================================================
    As_total = As1 + As2

    # =========================================================
    # 15. PROPIEDADES DE ACERO MÍNIMO
    # =========================================================

    minimo_flexion = propiedades_minimo_flexion(
        b=b,
        h=h,
        fc=fc,
        fy=fy,
        d=d,
        phi=phiFlexion
    )

    As_min = minimo_flexion["As_min_final_val"]

    # =========================================================
    # 16. ACERO TOTAL DE TRACCIÓN REQUERIDO
    # =========================================================
    #
    # El acero total requerido en tracción es:
    #
    #     As = As1 + As2
    #
    # Aquí NO lo llamamos As_max porque todavía no conocemos
    # el acero de compresión realmente seleccionado.
    #
    As_total_requerido = As1 + As2

    # =========================================================
    # 17. RESULTADOS
    # =========================================================
    resultado = {

        # ---------- Estado ----------
        "valido": True,
        "requiere_doble": True,

        "mensaje": (
            "El momento solicitado supera la resistencia "
            "de la sección simplemente reforzada con 0.75 As_bal. "
            "Se requiere acero de compresión."
        ),

        # ---------- Geometría ----------
        "beta1": beta1,
        "d": d,
        "d_comp": d_comp,

        # ---------- Deformación de fluencia ----------
        "eps_y": eps_y,

        # ---------- Balanceado ----------
        "cb_val": cb,
        "ab_val": ab,
        "As_bal_val": As_bal,

        # ---------- Primera parte ----------
        "As1_val": As1,
        "a1_val": a1,
        "c1_val": c1,
        "Mn1_val": Mn1,
        "phiMn1_val": phiMn1,

        # ---------- Momento residual ----------
        "Mu2_val": Mu2,

        # ---------- Acero adicional ----------
        "As2_val": As2,

        # ---------- Acero compresión ----------
        "eps_sp_val": eps_sp,
        "fs_p_elastico_val": fs_p_elastico,
        "fs_p_val": fs_p,
        "fluye_compresion": fluye_compresion,
        "As_comp_val": As_comp,

        # ---------- Acero total ----------
        "As_total_val": As_total,
        "As_total_requerido_val": As_total_requerido,

        # ---------- Acero mínimo ----------
        "As_min_val": As_min,

        # ---------- Textos ----------
        "As_bal_text": f"{As_bal:.2f} cm²",
        "As1_text": f"{As1:.2f} cm²",
        "a1_text": f"{a1:.2f} cm",
        "c1_text": f"{c1:.2f} cm",

        "Mn1_text": f"{Mn1:.2f} ton·m",
        "phiMn1_text": f"{phiMn1:.2f} ton·m",

        "Mu2_text": f"{Mu2:.2f} ton·m",

        "As2_text": f"{As2:.2f} cm²",

        "eps_sp_text": f"{eps_sp:.6f}",
        "fs_p_text": f"{fs_p:.2f} kg/cm²",

        "As_comp_text": f"{As_comp:.2f} cm²",

        "As_total_text": f"{As_total:.2f} cm²",
        "As_min_text": f"{As_min:.2f} cm²",
        "As_total_requerido_text": f"{As_total_requerido:.2f} cm²",
    }

    return resultado



def sugerir_acero(As_req, As_min=None, As_max=None):
    """
    Busca combinaciones de barras comerciales que cumplan:

        As_provisto >= As_req

    y, si se especifica As_max:

        As_provisto <= As_max

    Se prioriza:
        1. Cumplir As_req.
        2. Menor exceso de acero.
        3. Menor número total de barras.
    """

    opciones = []

    for _, fila in tablaAceros.iterrows():

        diametro = fila["Diametro"]
        area = fila["Área(cm2)"]

        for n in range(2, 13):

            As_provisto = n * area

            # Debe superar al acero requerido
            if As_provisto < As_req:
                continue

            # Debe cumplir máximo si se proporciona
            if As_max is not None and As_provisto > As_max:
                continue

            exceso = As_provisto - As_req

            opciones.append(
                {
                    "numero": n,
                    "diametro": diametro,
                    "As": As_provisto,
                    "exceso": exceso,
                }
            )

    if not opciones:

        return None

    # Orden:
    # 1. menor exceso
    # 2. menor número de barras
    # 3. menor área individual
    opciones.sort(
        key=lambda x: (
            x["exceso"],
            x["numero"],
            x["As"]
        )
    )

    return opciones[0]
