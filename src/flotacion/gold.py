from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "data/silver/flotacion.parquet"
DESTINO = RAIZ / "data/gold/features.parquet"


def crear_gold():
    datos = pd.read_parquet(ORIGEN)

    aire = [f"flotation_column_{n:02d}_air_flow" for n in range(1, 8)]
    nivel = [f"flotation_column_{n:02d}_level" for n in range(1, 8)]
    proceso = [
        "amina_flow", "starch_flow", "ore_pulp_flow",
        "ore_pulp_ph", "ore_pulp_density", *aire, *nivel,
    ]
    grupos = datos.groupby("date", sort=True)

    # Una fila por hora, con cuatro estadísticas para cada señal.
    resumen = grupos[proceso].agg(["mean", "std", "min", "max"])
    resumen.columns = [
        f"{senal}_{estadistica}" for senal, estadistica in resumen.columns
    ]
    tabla = resumen.asfreq("h")

    # Relaciones entre los flujos medios de la misma hora.
    pulpa = tabla["ore_pulp_flow_mean"]
    amina = tabla["amina_flow_mean"]
    almidon = tabla["starch_flow_mean"]
    if (pulpa <= 0).any() or (amina <= 0).any():
        raise ValueError("Hay un denominador no positivo en las dosis relativas.")

    tabla["amina_por_pulpa"] = amina / pulpa
    tabla["almidon_por_pulpa"] = almidon / pulpa
    tabla["almidon_por_amina"] = almidon / amina

    medias_aire = tabla[[f"{col}_mean" for col in aire]]
    medias_nivel = tabla[[f"{col}_mean" for col in nivel]]
    tabla["flujo_aire_total"] = medias_aire.sum(axis=1, min_count=7)
    tabla["nivel_promedio"] = medias_nivel.mean(axis=1)
    tabla["dispersion_niveles"] = medias_nivel.std(axis=1, ddof=0)

    # Historia disponible al cierre de cada hora.
    tabla["amina_cambio_1h"] = amina.diff()
    tabla["amina_media_3h_previas"] = amina.shift(1).rolling(3).mean()

    # Objetivo, referencia de persistencia y campos de diagnóstico.
    silice = grupos["pct_silica_concentrate"]
    tabla["silice_objetivo"] = silice.mean()
    tabla["silice_hace_3h"] = tabla["silice_objetivo"].shift(3)
    tabla["lecturas"] = grupos.size()
    tabla["valores_silice"] = silice.nunique()

    # Mismas horas comparables que en el ejercicio de persistencia.
    tabla = tabla.dropna(subset=[
        "silice_objetivo", "silice_hace_3h", "amina_media_3h_previas"
    ])

    if not tabla.index.is_unique or not tabla.index.is_monotonic_increasing:
        raise ValueError("Revisa la unicidad y el orden de las horas.")
    if tabla.isna().any().any():
        raise ValueError("La tabla horaria contiene valores faltantes.")

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(DESTINO, index=True)
    print("Horas guardadas:", len(tabla))
    print("Columnas guardadas:", len(tabla.columns))
    print("Archivo creado:", DESTINO.relative_to(RAIZ))


if __name__ == "__main__":
    crear_gold()
