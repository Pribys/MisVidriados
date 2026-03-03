
"""
Funciones auxiliares de presentación para la vista Seger (versión 03).

Responsabilidad:
- Formatear receta en columnas separadas.
- Formatear pesos pendientes.
- No contiene lógica química.
"""


def formatear_receta(receta: dict, total_deseado: float | None = None):

    if not receta:
        return [], [], [], []

    total = sum(receta.values()) or 1.0

    nombres = []
    pesos = []
    porcentajes = []
    cantidades = []

    for mp, val in receta.items():

        nombres.append(mp)
        pesos.append(f"{val:.2f}")
        porcentajes.append(f"{(val / total * 100):.1f} %")

        if total_deseado is not None:
            cantidades.append(f"{(val / total * total_deseado):.2f}")
        else:
            cantidades.append("")

    return nombres, pesos, porcentajes, cantidades


def formatear_pesos_pendientes(pendientes: dict):

    if not pendientes:
        return ""

    lineas = []
    suma_ppc = 0.0

    for ox, val in pendientes.items():
        if ox.upper() == "PPC":
            suma_ppc += abs(val)
            continue
        lineas.append(f"{ox}: {val:.2f}")

    k = pendientes.get("K2O", 0.0)
    na = pendientes.get("Na2O", 0.0)

    if "K2O" in pendientes or "Na2O" in pendientes:
        lineas.append("")
        lineas.append(f"KNaO: {(k + na):.2f}")

    if suma_ppc > 0.0:
        lineas.append("")
        lineas.append(f"PPC: {suma_ppc:.2f}")

    return "\n".join(lineas)
