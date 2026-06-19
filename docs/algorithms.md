# 1. Algoritmo Rectangle Max

## Descripción General

El algoritmo Rectangle Max permite encontrar el rectángulo máximo utilizable dentro de un terreno irregular.

Su objetivo es identificar el área rectangular más grande disponible para ubicar bloques arquitectónicos dentro del terreno.

Aplicaciones:

- Ubicación de pabellones.
- Distribución inicial de bloques.
- Optimización del área construible.


---

# Problema que resuelve

Dado un terreno representado como un polígono irregular:

```text
        Terreno irregular

      ****************
    **                **
   *                    *
   *                    *
    **              ****
       **************
````

El algoritmo busca:

```text
      +-------------+
      |             |
      |  Rectángulo |
      |    máximo   |
      |             |
      +-------------+
```

Encontrando la mayor área rectangular posible dentro del terreno.

---

# Flujo del Algoritmo

```mermaid
flowchart TD

A[Polygon del terreno]

A --> B[Normalizar coordenadas]

B --> C[Obtener ángulos candidatos]

C --> D[Rotar terreno]

D --> E[Rasterizar polígono a matriz binaria]

E --> F[Aplicar Maximal Rectangle]

F --> G[Convertir matriz a geometría]

G --> H[Rotar geometría al ángulo original]

H --> I[Rectángulo máximo encontrado]
```

---

# Etapas Internas

## 1. Normalización del Terreno

Función:

```
normalizar_polygon()
```

Responsabilidad:

Transformar coordenadas grandes (ejemplo UTM) a un sistema local cercano a:

```
(0,0)
```

Beneficios:

* Menor error numérico.
* Operaciones geométricas más estables.

---

## 2. Obtención de Ángulos Candidatos

Función:

```
get_candidate_angles()
```

Responsabilidad:

Analizar los lados del terreno para obtener posibles orientaciones del rectángulo.

Ejemplo:

```text
Lado del terreno
        |
        |
        +------------

Ángulo candidato:
0°
90°
45°
```

Esto evita probar infinitas rotaciones.

---

## 3. Conversión a Matriz Binaria

El polígono se convierte a una matriz:

```text
0 0 0 0 0

0 1 1 1 0

0 1 1 1 0

0 0 0 0 0
```

Donde:

* 1 = área disponible.
* 0 = fuera del terreno.

---

## 4. Maximal Rectangle

Función:

```
maximal_rectangle()
```

Utiliza una estrategia basada en:

* Histograma por filas.
* Stack monotónico.
* Cálculo de áreas máximas.

Salida:

```text
Área máxima

Posición:
(x,y)

Dimensiones:

ancho
largo
```

---

# Optimización de Búsqueda

El algoritmo utiliza dos fases:

## Primera pasada

Objetivo:

Encontrar una solución aproximada rápidamente.

Configuración:

```
cell_size = 0.5
```

Menor precisión.

Mayor velocidad.

---

## Segunda pasada

Objetivo:

Refinar el resultado encontrado.

Configuración:

```
cell_size = 0.2
```

Mayor precisión.

Menor error.

---

# Búsqueda de Siguientes Rectángulos

Función:

```
find_next_best_rectangle()
```

Permite obtener nuevos bloques dentro del terreno restante.

Flujo:

```mermaid
flowchart TD

A[Terreno original]

A --> B[Encontrar primer rectángulo]

B --> C[Restar área utilizada]

C --> D[Terreno restante]

D --> E[Buscar siguiente rectángulo máximo]

E --> F[Nuevo bloque arquitectónico]
```

---

# Entrada Rectangle Max

```text
Polygon terreno
```

Ejemplo:

```json
[
 [0,0],
 [100,0],
 [100,50],
 [0,50]
]
```

---

# Salida Rectangle Max

Retorna:

* Geometría del rectángulo.
* Área calculada.
* Ángulo de rotación.

Ejemplo:

```json
{
 "area": 3200,
 "angle": 15,
 "geometry": "POLYGON(...)"
}
```

---

# 2. Algoritmo de Distribución / Unpacking de Ambientes

## Descripción

Este algoritmo distribuye ambientes dentro del área disponible generando una configuración arquitectónica válida.

Objetivos:

* Aprovechar espacio disponible.
* Mantener distribución ordenada.
* Generar dimensiones automáticamente.

---

# Flujo del Algoritmo

```mermaid
flowchart TD

A[Lista de ambientes]

A --> B[Analizar medidas requeridas]

B --> C[Separar medidas fijas y automáticas]

C --> D[Calcular espacios disponibles]

D --> E[Distribuir ambientes]

E --> F[Generar coordenadas]

F --> G[Crear geometrías]
```

---

# Distribución de Medidas

El algoritmo permite definir:

## Medidas fijas

Ejemplo:

```text
Aula = 8m
Laboratorio = 10m
```

## Medidas automáticas

Ejemplo:

```text
Auto
Auto
Auto
```

El sistema calcula:

```
espacio restante / cantidad automática
```

---

# Generación de Coordenadas

Función:

```
acumate_coords()
```

Transforma medidas:

Entrada:

```text
[5,10,15]
```

Salida:

```text
[
 [0,5],
 [5,15],
 [15,30]
]
```

Representando posiciones dentro del plano.

---

# Distribución por Pisos

El algoritmo soporta agrupación por niveles:

```mermaid
flowchart TD

A[Ambientes]

A --> B[Piso 1]

A --> C[Piso 2]

A --> D[Piso 3]

B --> E[Distribución horizontal]

C --> F[Distribución horizontal]

D --> G[Distribución horizontal]
```

---

# Entrada Unpacking

Información:

* Lista de ambientes.
* Dimensiones disponibles.
* Número de pisos.
* Restricciones espaciales.

---

# Salida Unpacking

Genera:

* Coordenadas.
* Dimensiones finales.
* Ubicación de ambientes.
* Información para creación geométrica.

---

# Integración con BIM

```mermaid
flowchart LR

A[Terreno]

A --> B[Rectangle Max]

B --> C[Área disponible]

C --> D[Unpacking]

D --> E[Ambientes distribuidos]

E --> F[Generación BIM]

F --> G[Modelo 2D/3D]
```

---

# Consideraciones Técnicas

* Los algoritmos trabajan sobre geometrías Shapely.
* Las operaciones utilizan sistemas de coordenadas normalizados.
* La optimización busca equilibrio entre precisión y rendimiento.
* La salida geométrica es reutilizada por los módulos CAD y render.
