# ProDesign - Geometry Service API 📐

## Descripción General

ProDesign Geometry Service es un microservicio especializado en procesamiento geométrico avanzado, optimización espacial y generación automática de planos arquitectónicos.

El servicio permite transformar parámetros arquitectónicos, normativos y geométricos en distribuciones optimizadas de ambientes, generando automáticamente planos en 2D, modelos tridimensionales y estimaciones preliminares de costos de infraestructura.

Actualmente el servicio está orientado a la generación de infraestructura educativa (colegios), permitiendo la creación automática de espacios como aulas, laboratorios, servicios higiénicos, áreas administrativas y zonas de circulación.

La arquitectura del servicio está diseñada para permitir la incorporación futura de nuevos tipos de infraestructura como:

- Sector salud.
- Oficinas.
- Infraestructura pública.
- Otros tipos de edificaciones.

---

# Objetivos del Servicio

- Automatizar la generación de planos arquitectónicos.
- Optimizar la distribución de ambientes dentro de terrenos regulares e irregulares.
- Generar representaciones arquitectónicas 2D y 3D.
- Reducir tiempos de diseño preliminar.
- Optimizar el uso del área disponible.
- Calcular áreas construidas y métricas espaciales.
- Generar estimaciones de costos de infraestructura basadas en los planos generados.
- Servir como motor geométrico para la plataforma ProDesign.

---

# Tecnologías Utilizadas

| Tecnología | Propósito |
|------------|-----------|
| Python 3.12 | Lenguaje principal del servicio |
| FastAPI | Exposición de servicios REST |
| Shapely | Procesamiento y cálculos geométricos |
| Pydantic | Validación y definición de modelos |
| CadQuery | Generación de geometría 2D y 3D |
| QueryCAD | Construcción y consulta de modelos geométricos |
| Plotly | Renderizado interactivo de geometrías, vértices y shapes generados |
| Docker | Contenerización del servicio |
| GitHub Actions | Automatización CI/CD |

---

# Capacidades Principales

## Generación Automática de Ambientes

El sistema genera distribuciones automáticas de ambientes según el tipo de infraestructura requerida.

Actualmente soporta:

- Aulas.
- Laboratorios.
- Servicios higiénicos.
- Áreas administrativas.
- Pasadizos y circulaciones.

Tipo de infraestructura actual:

- Colegios.

Tipos de infraestructura proyectados:

- Hospitales.
- Centros de salud.
- Oficinas.
- Otros modelos arquitectónicos.

---

# Optimización Geométrica

El sistema analiza terrenos y restricciones espaciales para obtener una distribución eficiente.

Incluye:

- Procesamiento de terrenos regulares e irregulares.
- Identificación de áreas útiles.
- Cálculo de áreas construibles.
- Optimización del aprovechamiento espacial.

---

# Algoritmos Principales

## Rectangle Max

Algoritmo encargado de encontrar el área rectangular máxima disponible dentro de geometrías irregulares.

Aplicaciones:

- Ubicación óptima de bloques arquitectónicos.
- Identificación de áreas aprovechables.
- Optimización preliminar del diseño.

---

## Algoritmo de Unpacking de Ambientes

Algoritmo encargado de distribuir ambientes dentro del espacio disponible.

Objetivos:

- Reducir desperdicio de área.
- Cumplir restricciones geométricas.
- Mantener relaciones funcionales entre ambientes.
- Generar configuraciones válidas automáticamente.

---

# Generación de Planos 2D

El sistema genera representaciones bidimensionales de los diseños arquitectónicos.

Incluye:

- Ambientes.
- Muros.
- Puertas.
- Ventanas.
- Circulaciones.
- Distribuciones por capas.

Formatos soportados:

- SVG.
- DXF.

---

# Generación de Modelos 3D

El servicio genera modelos tridimensionales utilizando CadQuery.

Componentes generados:

- Pisos.
- Muros.
- Techos.
- Columnas.
- Escaleras.
- Balcones.
- Elementos arquitectónicos.

Formato soportado:

- STEP.

Aplicaciones:

- Visualización.
- Integración CAD.
- Validación geométrica.

---

### AMBIENTES COMPLEMENTARIOS OPCIONALES
OBLIGATORIOS:
- Tópico
- Patio de Inicial
- Direccion administrativa
- Sala de profesores
---


# Render y Visualización

El sistema utiliza Plotly para la representación visual interactiva de las geometrías generadas.

Permite visualizar:

- Vértices.
- Polígonos.
- Shapes.
- Distribuciones espaciales.
- Resultados geométricos antes de exportación CAD.

---

# Cálculo de Costos de Infraestructura

El sistema genera estimaciones preliminares de costos basadas en los planos arquitectónicos generados.

Los cálculos consideran:

- Áreas construidas.
- Distribución de ambientes.
- Métricas espaciales.
- Componentes generados.

Resultado:

- Resumen de áreas.
- Información base para estimación económica del proyecto.
- Reportes asociados al diseño generado.

---

# Arquitectura Interna

## Auth

Responsable de:

- Validación JWT.
- Control de acceso.
- Seguridad de endpoints.

---

## BIM API

Capa encargada de exponer los servicios del motor geométrico.

Responsabilidades:

- Recepción de solicitudes de generación.
- Validación de parámetros.
- Orquestación del proceso geométrico.
- Generación de layouts.
- Cálculo de cuadrantes máximos.
- Cálculo de costos de infraestructura.
- Generación de reportes de proyecto.
- Exposición de resultados 2D y 3D.

---

## BIM Lib

Motor interno encargado de la generación geométrica.

Responsabilidades:

- Generación automática de planos.
- Cálculo geométrico.
- Generación de ambientes.
- Creación de componentes arquitectónicos:

  - Muros.
  - Puertas.
  - Ventanas.
  - Columnas.
  - Pisos.
  - Losas.
  - Techos.
  - Escaleras.
  - Balcones.

- Separación de componentes por capas.
- Configuración para visualización 2D y 3D.
- Exportación CAD:

  - STEP.
  - DXF.

---

# Inicio Rápido

## Activar entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

## Levantar Fast API

```powershell
fastapi dev main.py --port 8001
```