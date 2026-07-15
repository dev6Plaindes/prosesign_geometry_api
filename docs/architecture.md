# ProDesign Geometry Service - Architecture 📐

## 1. Visión General de Arquitectura

ProDesign Geometry Service está diseñado como un microservicio independiente encargado del procesamiento geométrico, generación de planos y creación de modelos 3D.

La arquitectura separa responsabilidades entre:

- Capa API: exposición de servicios.
- Capa lógica BIM: procesamiento y generación geométrica.
- Motor geométrico: algoritmos de optimización.
- Motor CAD: exportación de modelos.
- Capa visual: renderizado de resultados.


## 2. Diagrama de Componentes

```mermaid
flowchart TD

A[ProDesign Platform]

A --> B[BIM API]

B --> C[Auth JWT]

B --> D[BIM Lib]

D --> E[Geometry Engine]

E --> F[Shapely]

E --> G[Rectangle Max]

E --> H[Unpacking Algorithm]

D --> I[CAD Engine]

I --> J[CadQuery]

I --> K[QueryCAD]

D --> L[Render Engine]

L --> M[Plotly]

I --> N[Export]

N --> O[STEP]
N --> P[DXF]
N --> Q[SVG]

D --> R[Cost Calculator]
````

---

# 3. Flujo General del Sistema

## Generación de Proyecto Arquitectónico

```mermaid
sequenceDiagram

Usuario->>BIM API: Solicitud de generación

BIM API->>Auth: Validación JWT

Auth-->>BIM API: Usuario autorizado

BIM API->>BIM Lib: Procesar parámetros

BIM Lib->>Geometry Engine: Calcular distribución

Geometry Engine->>Rectangle Max: Buscar área óptima

Geometry Engine->>Unpacking: Distribuir ambientes

BIM Lib->>CAD Engine: Generar modelo

CAD Engine->>CadQuery: Crear geometría 3D

CAD Engine->>Export: Generar archivos

Export-->>BIM API: Resultado generado

BIM API-->>Usuario: Plano + modelo + costos
```

---

# 4. Componentes Principales

## BIM API

Responsabilidad:

* Punto de entrada del servicio.
* Exposición de endpoints REST.
* Validación de solicitudes.
* Orquestación del flujo.

Entrada:

* Datos del terreno.
* Requerimientos arquitectónicos.
* Parámetros normativos.

Salida:

* Layout generado.
* Archivos CAD.
* Información calculada.

---

## BIM Lib

Motor principal del sistema.

Responsabilidades:

* Creación de geometrías.
* Generación de ambientes.
* Construcción de componentes arquitectónicos.

Componentes generados:

* Muros.
* Pisos.
* Techos.
* Columnas.
* Puertas.
* Ventanas.
* Escaleras.
* Balcones.

---

## Geometry Engine

Responsable del procesamiento matemático.

Funciones:

* Operaciones geométricas.
* Intersecciones.
* Validaciones.
* Cálculo de áreas.

Tecnología:

* Shapely

---

## Optimization Engine

Incluye:

### Rectangle Max

Encuentra áreas máximas utilizables dentro de terrenos irregulares.

### Unpacking Algorithm

Distribuye ambientes respetando restricciones.

---

## CAD Engine

Responsable de transformar geometrías en modelos CAD.

Tecnologías:

* CadQuery
* QueryCAD

Salida:

* STEP
* DXF
* SVG

---

## Render Engine

Responsable de visualización.

Tecnología:

* Plotly

Permite:

* Render de polígonos.
* Visualización de vértices.
* Validación visual del diseño.

---

# 5. Flujo de Datos

```text

Terreno + Aforo
          |
          v
     BIM API
          |
          v
  Geometry Processing
          |
          v
 Optimization Algorithms
          |
          v
 Environment Generation
          |
          v
 CAD Generation
          |
          +--------+
          |        |
          v        v
       2D Plan   3D Model

          |
          v

 Cost Estimation
```

---

# 6. Principios Arquitectónicos

* Separación de responsabilidades.
* Motor geométrico desacoplado de la API.
* Capacidad de agregar nuevos tipos de infraestructura.
* Reutilización de algoritmos BIM.
* Exportación independiente del formato.

---

# 7. Evolución Futura

La arquitectura permite incorporar:

* Nuevos tipos de infraestructura.
* Nuevas reglas arquitectónicas.
* Nuevos algoritmos de optimización.
* Nuevos formatos CAD.

```
