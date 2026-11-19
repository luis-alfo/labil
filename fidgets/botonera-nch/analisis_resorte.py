"""Análisis del resorte en espiral de la v5 (modelo de vigas: flexión + torsión).

Modela un brazo como cadena de vigas en el plano XY que se deforman en Z.
Extremo exterior empotrado en el marco; extremo interior unido al buje, que baja
`RECORRIDO` sin girar (por simetría de los 3 brazos). Da la fuerza total del
botón y la tensión/deformación máxima del plástico.
Uso: python3 analisis_resorte.py
"""
import numpy as np
import generar_v5 as v5

MATERIALES = {  # módulo E (MPa), deformación admisible orientativa para fatiga
    "PLA": (3500, 0.010),
    "PETG": (2100, 0.020),
}
NU = 0.35


def nodos():
    r0, r1 = v5.R_BUJE, v5.R_LIBRE  # tramo libre entre buje y marco
    t = np.linspace(0, 1, 201)
    ang = np.radians(v5.GIRO_BRAZO * t)
    r = r0 + (r1 - r0) * t
    return np.c_[r * np.cos(ang), r * np.sin(ang)]


def analizar(E, recorrido=v5.RECORRIDO, b=v5.ANCHO_BRAZO, t=v5.GROSOR_BRAZO):
    G = E / (2 * (1 + NU))
    I = b * t**3 / 12                       # flexión fuera del plano
    a_, c_ = max(b, t), min(b, t)
    J = c_**3 * a_ * (1 / 3 - 0.21 * c_ / a_ * (1 - c_**4 / (12 * a_**4)))  # torsión
    p = nodos()
    n = len(p)
    K = np.zeros((3 * n, 3 * n))            # gdl por nodo: w, rot_x, rot_y
    elems = []
    for i in range(n - 1):
        d = p[i + 1] - p[i]
        L = np.hypot(*d)
        c, s = d / L
        k = np.zeros((6, 6))                # local: w, theta_t (torsión), theta_b (flexión)
        kb = E * I / L**3 * np.array([[12, 6*L, -12, 6*L], [6*L, 4*L*L, -6*L, 2*L*L],
                                       [-12, -6*L, 12, -6*L], [6*L, 2*L*L, -6*L, 4*L*L]])
        idx = [0, 2, 3, 5]
        k[np.ix_(idx, idx)] = kb
        kt = G * J / L
        k[np.ix_([1, 4], [1, 4])] = kt * np.array([[1, -1], [-1, 1]])
        # rotaciones globales (rx, ry) -> locales: torsión = eje del brazo, flexión = perpendicular
        R1 = np.array([[1, 0, 0], [0, c, s], [0, s, -c]])
        T = np.zeros((6, 6)); T[:3, :3] = R1; T[3:, 3:] = R1
        kg = T.T @ k @ T
        g = list(range(3 * i, 3 * i + 6))
        K[np.ix_(g, g)] += kg
        elems.append((g, T, L))
    u = np.zeros(3 * n)
    fijos = {0: recorrido, 1: 0, 2: 0, 3 * (n - 1): 0, 3 * (n - 1) + 1: 0, 3 * (n - 1) + 2: 0}
    libres = [i for i in range(3 * n) if i not in fijos]
    for i, v in fijos.items():
        u[i] = v
    fij = list(fijos)
    u[libres] = np.linalg.solve(K[np.ix_(libres, libres)], -K[np.ix_(libres, fij)] @ u[fij])
    fuerza_brazo = (K @ u)[0]
    sig_max = 0
    for g, T, L in elems:
        ul = T @ u[g]
        # momentos en extremos (flexión) y torsor
        kb = E * I / L**3 * np.array([[12, 6*L, -12, 6*L], [6*L, 4*L*L, -6*L, 2*L*L],
                                       [-12, -6*L, 12, -6*L], [6*L, 2*L*L, -6*L, 4*L*L]])
        f = kb @ ul[[0, 2, 3, 5]]
        M = max(abs(f[1]), abs(f[3]))
        Tq = abs(G * J / L * (ul[4] - ul[1]))
        sig = M * (t / 2) / I
        tau = Tq / (J / c_) if J else 0       # aprox. tau_max = T*c/J
        sig_max = max(sig_max, np.hypot(sig, np.sqrt(3) * tau))   # von Mises
    return v5.N_BRAZOS * fuerza_brazo, sig_max


if __name__ == "__main__":
    for nombre, (E, eps_adm) in MATERIALES.items():
        F, s = analizar(E)
        eps = s / E
        print(f"{nombre}: fuerza {F:.2f} N ({F / 9.81 * 1000:.0f} g) | tensión máx {s:.1f} MPa | "
              f"deformación {eps * 100:.2f} % (orientativo admisible {eps_adm * 100:.1f} %) -> "
              f"margen x{eps_adm / eps:.1f}")
