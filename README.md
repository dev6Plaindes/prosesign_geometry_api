# ProDesign - Geometry Service API 📐

## Descripción General

ProDesign Geometry Service es un microservicio especializado en el procesamiento geométrico, optimización espacial y generación automática de planos arquitectónicos.

El servicio recibe parámetros arquitectónicos y normativos para generar distribuciones de ambientes optimizadas, produciendo planos 2D y modelos 3D de forma automatizada.

Actualmente el sistema se encuentra orientado a la generación de infraestructura educativa (colegios). La arquitectura ha sido diseñada para soportar futuros módulos especializados para otros sectores, como salud, oficinas y edificaciones públicas.

---

## Objetivos del Servicio

* Automatizar la generación de planos arquitectónicos.
* Optimizar la distribución de ambientes dentro de terrenos regulares e irregulares.
* Generar representaciones 2D y 3D de los diseños.
* Reducir tiempos de diseño preliminar.
* Estimar áreas construidas y requerimientos espaciales.
* Servir como motor geométrico para la plataforma ProDesign.
* Cálculo de costos de infraestructura en base a los planos generados.

---

## Tecnologías

| Tecnología     | Propósito                                      |
| -------------- | ---------------------------------------------- |
| Python 3.12    | Lenguaje principal                             |
| FastAPI        | Exposición de servicios REST                   |
| Shapely        | Operaciones geométricas                        |
| Pydantic       | Validación de modelos                          |
| CadQuery       | Generación geométrica 2D y 3D                  |
| QueryCAD       | Construcción y consulta de modelos geométricos |
| Docker         | Contenerización                                |
| GitHub Actions | Automatización CI/CD                           |
| Plotly | Renderiza las gemoetrias, vertices, shapes generados en el plano                           |

---

## Capacidades Principales

### Generación Automática de Ambientes

El sistema genera automáticamente la distribución de ambientes requeridos según el tipo de infraestructura.

Ejemplos actuales:

* Aulas
* Laboratorios
* Servicios higiénicos
* Áreas administrativas
* Circulaciones

Actualmente implementado para:

* Infraestructura educativa (colegios)

Planificado:

* Infraestructura de salud
* Infraestructura administrativa
* Otros tipos de edificaciones

---

### Optimización de Terrenos

El sistema analiza terrenos regulares e irregulares para determinar el área útil disponible.

Incluye:

* Cálculo geométrico.
* Identificación de áreas construibles.
* Maximización del aprovechamiento espacial.

---

### Algoritmo Rectangle Max

Permite identificar el rectángulo máximo utilizable dentro de polígonos irregulares.

Aplicaciones:

* Ubicación de bloques principales.
* Determinación de áreas edificables.
* Optimización preliminar del diseño.

---

### Algoritmo de Unpacking de Ambientes

Utilizado para distribuir ambientes dentro de la superficie disponible.

Objetivos:

* Minimizar desperdicio de espacio.
* Cumplir restricciones geométricas.
* Mantener relaciones funcionales entre ambientes.
* Generar configuraciones válidas automáticamente.

---

### Generación de Planos 2D

Salida disponible en formatos:

* SVG
* DXF

---

### Generación de Modelos 3D

Generación automática de modelos tridimensionales utilizando CadQuery.

Formatos soportados:

* STEP

Aplicaciones:

* Visualización
* Integración CAD
* Validación geométrica

---

## Módulos Principales

### Auth

Responsable de:

* Validación JWT.
* Control de acceso.
* Seguridad de endpoints.

### BIM API

Responsable de:

* Solicitud de generación de planos
* Generacion de máximos cuadrantes
* Costos de infraestructura de los proyectos
* Generacion de reporte de proyecto para proinvierte
* Renderizar planos generalizados en 2d y 3d

### BIM lib

Responsable de:
* Generacion de planos
* Calculo de maximos cuadrantes
* Generacion de ambientes, pasadizos, columnas, puertas, ventanas, muros, techos, escaleras, balcon, losa y pisos.
* Separacion de componentes por capas (pisos)
* Exportacion en step, xdf
* Configuracion para la vista 2d y 3d


## Inicio Rápido

### Activar entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar en desarrollo

```bash
fastapi dev main.py --port 8001
```

---

## Documentación API

La documentación interactiva está disponible mediante Swagger/OpenAPI.

Endpoints disponibles:

* Generación de layouts
* Procesamiento geométrico
* Exportación CAD
* Validación de terrenos
* Autenticación
