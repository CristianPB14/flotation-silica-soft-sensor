# Sensor virtual de sílice en la flotación de mineral de hierro

## Problema y uso previsto

En una planta de flotación de mineral de hierro, el laboratorio analiza
muestras del concentrado para determinar qué porcentaje de sílice contienen.
Mientras se espera el resultado, la planta continúa produciendo.

El objetivo de este proyecto es estimar cada hora el porcentaje de sílice
del concentrado a partir de las señales disponibles al emitir la predicción.
La estimación ayudaría al operador a decidir si conviene revisar el aire
de flotación o la dosificación de reactivos.

## Cómo se evaluará

Cada estimación se comparará con el resultado de laboratorio correspondiente
a la misma muestra. También se evaluará si el modelo mejora una referencia
sencilla: usar como estimación el último resultado de laboratorio disponible.
