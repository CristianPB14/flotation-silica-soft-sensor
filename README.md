# Sensor virtual de sílice en la flotación de mineral de hierro

## Problema y uso previsto

En una planta de flotación de mineral de hierro, el laboratorio analiza
muestras del concentrado para determinar qué porcentaje de sílice contienen.
Mientras se espera el resultado, la planta continúa produciendo.

El objetivo de este proyecto es estimar cada hora el porcentaje de sílice
del concentrado a partir de las señales disponibles al emitir la predicción.
La estimación ayudaría al operador a decidir si conviene revisar el aire
de flotación o la dosificación de reactivos.

## Datos y evaluación

El conjunto [Quality Prediction in a Mining Process](https://www.kaggle.com/datasets/edumagalhaes/quality-prediction-in-a-mining-process) contiene 737.453 registros de marzo a septiembre de 2017. Se agregaron las señales por hora y se obtuvo una tabla de 4.091 horas con historial disponible. Se asumió que la sílice de tres horas antes estaba disponible al emitir cada estimación. El hierro del concentrado se excluyó por su disponibilidad simultánea con el objetivo.

Las últimas 819 horas se reservaron para prueba. La persistencia obtuvo el menor MAE (0,679 puntos porcentuales de sílice). El bosque con señales de proceso y sílice rezagada obtuvo el menor RMSE (0,935). La [tabla completa](reports/metricas_prueba.csv) incluye los ocho métodos y escenarios evaluados.

## Reproducción en Linux

Entorno utilizado: Python 3.13.5. Desde una terminal, clonar el proyecto e instalar sus dependencias:

```bash
git clone https://github.com/CristianPB14/flotation-silica-soft-sensor.git
cd flotation-silica-soft-sensor
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Desde la raíz de la copia nueva, descargar los datos y extraer el CSV original con el nombre esperado por el pipeline. Estos comandos requieren curl y unzip:

```bash
mkdir -p data/raw
curl --fail --location "https://www.kaggle.com/api/v1/datasets/download/edumagalhaes/quality-prediction-in-a-mining-process" --output data/raw/mining.zip
unzip -p data/raw/mining.zip MiningProcess_Flotation_Plant_Database.csv > data/raw/mining.csv
```

Ejecutar las etapas en orden. Bronze convierte los tipos de datos, silver valida las mediciones y gold construye las variables horarias. La evaluación genera las métricas y las predicciones por hora en `reports/`.

```bash
python src/flotacion/bronze.py
python src/flotacion/silver.py
python src/flotacion/gold.py
python src/flotacion/evaluate.py
python -m jupyterlab notebooks/ProyectoFinal_CristianCamiloPiñerosBautista.ipynb
```

En JupyterLab, seleccionar **Kernel → Restart Kernel and Run All Cells**. El notebook vuelve a calcular la importancia por permutación en las 655 horas de validación y muestra las figuras y métricas.
