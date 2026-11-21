from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


RAIZ = Path(__file__).resolve().parents[2]
OBJETIVO = "silice_objetivo"
REZAGO = "silice_hace_3h"


def evaluar():
    tabla = pd.read_parquet(RAIZ / "data/gold/features.parquet").sort_index()
    prueba = tabla.iloc[int(len(tabla) * 0.80):]
    corte = prueba.index[0] - pd.Timedelta(hours=3)
    entrenamiento = tabla.loc[:corte]

    aparte = [OBJETIVO, REZAGO, "lecturas", "valores_silice"]
    proceso = tabla.drop(columns=aparte).columns.tolist()

    predicciones = pd.DataFrame(index=prueba.index)
    predicciones["media"] = entrenamiento[OBJETIVO].mean()
    predicciones["persistencia"] = prueba[REZAGO]

    for escenario in ["proceso", "proceso_laboratorio"]:
        con_laboratorio = escenario == "proceso_laboratorio"
        columnas = proceso + [REZAGO] if con_laboratorio else proceso

        modelos = {
            "ridge": make_pipeline(StandardScaler(), Ridge(alpha=1000)),
            "knn": make_pipeline(
                StandardScaler(),
                KNeighborsRegressor(n_neighbors=15 if con_laboratorio else 35),
            ),
            "bosque": RandomForestRegressor(
                n_estimators=60,
                max_depth=6 if con_laboratorio else None,
                min_samples_leaf=3 if con_laboratorio else 10,
                max_features=0.4,
                random_state=42,
                n_jobs=2,
            ),
        }

        for nombre, modelo in modelos.items():
            modelo.fit(entrenamiento[columnas], entrenamiento[OBJETIVO])
            predicciones[f"{nombre}_{escenario}"] = modelo.predict(prueba[columnas])

    real = prueba[OBJETIVO]
    resultados = []
    for nombre, estimacion in predicciones.items():
        resultados.append({
            "metodo": nombre,
            "MAE": mean_absolute_error(real, estimacion),
            "RMSE": mean_squared_error(real, estimacion) ** 0.5,
            "R2": r2_score(real, estimacion),
        })

    metricas = pd.DataFrame(resultados).set_index("metodo")
    carpeta = RAIZ / "reports"
    carpeta.mkdir(exist_ok=True)
    metricas.to_csv(carpeta / "metricas_prueba.csv")
    predicciones.insert(0, OBJETIVO, real)
    predicciones.to_csv(carpeta / "predicciones_prueba.csv", index_label="date")

    print(f"Horas de entrenamiento: {len(entrenamiento)}")
    print(f"Horas de prueba: {len(prueba)}")
    print(metricas.round(3).to_string())


if __name__ == "__main__":
    evaluar()
