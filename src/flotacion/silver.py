from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "data/bronze/flotacion.parquet"
DESTINO = RAIZ / "data/silver/flotacion.parquet"


def validar_mediciones(datos):
    porcentajes = datos.filter(regex=r"^pct_")
    flujos = datos.filter(regex=r"_flow$")

    incumple = pd.DataFrame({
        "fila_con_nulos": datos.isna().any(axis=1),
        "porcentaje_fuera_de_0_a_100": (
            (porcentajes < 0) | (porcentajes > 100)
        ).any(axis=1),
        "flujo_negativo": (flujos < 0).any(axis=1),
        "densidad_no_positiva": datos["ore_pulp_density"] <= 0,
        "ph_fuera_del_rango_de_revision": ~datos["ore_pulp_ph"].between(0, 14),
    })

    conteos = incumple.sum()
    print("Filas que incumplen cada regla:")
    print(conteos.to_string())

    if conteos.any():
        raise ValueError("Revisa las mediciones señaladas antes de generar silver.")


def crear_silver():
    datos = pd.read_parquet(ORIGEN)
    validar_mediciones(datos)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    datos.to_parquet(DESTINO, engine="pyarrow", index=False)

    print(f"\nFilas de entrada: {len(datos)}")
    print(f"Filas conservadas: {len(datos)}")
    print(f"Archivo creado: {DESTINO.relative_to(RAIZ)}")


if __name__ == "__main__":
    crear_silver()
