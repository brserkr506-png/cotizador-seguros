import pandas as pd
import numpy as np

def cargar_tabla(ruta_excel, nombre_tabla):
    df = pd.read_excel(ruta_excel)
    if nombre_tabla not in df.columns:
        nombre_tabla = df.columns[1]
    q = df[nombre_tabla].values
    edad = df['qx'].values
    max_edad = len(q)
    l = np.zeros(max_edad + 1)
    l[0] = 100000.0
    for i in range(max_edad):
        l[i+1] = l[i] * (1 - q[i])
    d = np.zeros(max_edad)
    for i in range(max_edad):
        d[i] = l[i] - l[i+1]
    return edad, q, l[:-1], d

def calcular_conmutacion(edad, l, d, i):
    v = 1.0 / (1.0 + i)
    max_edad = len(edad)
    v_n = np.array([v**x for x in range(max_edad + 1)])
    D = v_n[:max_edad] * l
    C = v_n[1:max_edad+1] * d
    N = np.zeros(max_edad)
    M = np.zeros(max_edad)
    for idx in range(max_edad):
        N[idx] = np.sum(D[idx:])
        M[idx] = np.sum(C[idx:])
    return D, C, N, M

def calcular_seguro(x, n, modalidad, suma_asegurada, D, C, M, edad_min):
    idx = x - edad_min
    if modalidad == "Temporal":
        M_diff = M[idx] - M[idx+n]
        A = M_diff / D[idx]
    elif modalidad == "Vida Entera":
        A = M[idx] / D[idx]
    elif modalidad == "Dotal":
        M_diff = M[idx] - M[idx+n]
        E = D[idx+n] / D[idx]
        A = (M_diff / D[idx]) + E
    return suma_asegurada * A

def calcular_anualidad_primas(x, n, forma_pago, h, m, modalidad, D, N, edad_min):
    idx = x - edad_min
    if forma_pago == "Prima Única":
        return 1.0
    elif forma_pago == "Prima Nivelada":
        if modalidad == "Vida Entera":
            ddot = N[idx] / D[idx]
        else:
            ddot = (N[idx] - N[idx+n]) / D[idx]
        return ddot
    elif forma_pago == "Prima Limitada":
        ddot = (N[idx] - N[idx+h]) / D[idx]
        return ddot
    elif forma_pago == "Prima Fraccionada":
        if modalidad == "Vida Entera":
            ddot = N[idx] / D[idx]
            ddot_m = ddot - ((m - 1.0) / (2.0 * m))
        else:
            ddot = (N[idx] - N[idx+n]) / D[idx]
            E_n = D[idx+n] / D[idx]
            ddot_m = ddot - ((m - 1.0) / (2.0 * m)) * (1.0 - E_n)
        return ddot_m
    return 1.0

def calcular_prima_comercial(p_neta, alfa, beta, gamma, utilidad, gasto_fijo):
    denominador = 1.0 - (alfa + beta + gamma + utilidad)
    if denominador <= 0:
        raise ValueError("La suma de recargos debe ser estrictamente menor a 1.")
    g = (p_neta + gasto_fijo) / denominador
    return g