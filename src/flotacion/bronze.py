from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "data/raw/mining.csv"
DESTINO = RAIZ / "data/bronze/flotacion.parquet"


def crear_bronze():
    datos = pd.read_csv(ORIGEN, decimal=",", encoding="utf-8-sig")
    datos["date"] = pd.to_datetime(
        datos["date"], format="%Y-%m-%d %H:%M:%S", errors="raise"
    )

    medidas = datos.drop(columns="date")
    sin_convertir = medidas.select_dtypes(exclude="number").columns.tolist()
    if sin_convertir:
        raise ValueError(f"Estas columnas siguen siendo texto: {sin_convertir}")

    if datos.shape != (737453, 24):
        raise ValueError(f"Dimensiones inesperadas: {datos.shape}")

    nulos = datos.isna().sum()
    if nulos.any():
        raise ValueError(f"Se encontraron valores nulos:\n{nulos[nulos > 0]}")

    datos.columns = (
        datos.columns.str.strip()
        .str.lower()
        .str.replace("% ", "pct_", regex=False)
        .str.replace(" ", "_", regex=False)
    )

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    datos.to_parquet(DESTINO, engine="pyarrow", index=False)

    muestra = pd.read_parquet(
        DESTINO, columns=["date", "amina_flow", "pct_silica_concentrate"]
    )
    print(muestra.head(3).to_string(index=False))
    print(f"\nDimensiones: {len(datos)} filas y {len(datos.columns)} columnas")
    print(f"Periodo: {muestra['date'].min()} a {muestra['date'].max()}")
    print(f"Tamaño CSV: {ORIGEN.stat().st_size / 1024**2:.1f} MiB")
    print(f"Tamaño Parquet: {DESTINO.stat().st_size / 1024**2:.1f} MiB")
    print(f"Archivo creado: {DESTINO.relative_to(RAIZ)}")


if __name__ == "__main__":
    crear_bronze()
