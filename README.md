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
uvicorn main:app --reload --port 8001
```

Probar el worker
```bash
watchfiles "py worker.py" src
```

Testear generacion de proyecto
```bash
py -m tests.generate_project
```


---

# [DOCUMENTACIÓN] Se añadió la sección de pruebas al README.md para detallar el funcionamiento de test_renders.py y cómo ejecutarlo.

La documentación interactiva está disponible mediante Swagger/OpenAPI.

Endpoints disponibles:

* Generación de layouts
* Procesamiento geométrico
* Exportación CAD
* Validación de terrenos
* Autenticación

---

## Pruebas

El proyecto cuenta con un módulo de pruebas automáticas configurado con Pytest. Para ejecutar las pruebas de generación de geometría y renderizado 2D/3D:

```powershell
.\venv\Scripts\pytest tests/BIM/test_renders.py
```

---

# [DOCUMENTACIÓN] Modificación de la Geometría de Techos (Julio 2026)
Se corrigieron y optimizaron los módulos de generación de techos especiales (Z1 y Z3) para resolver desalineaciones, vacíos verticales y solapamientos de losas en la API de geometría:
- **Desfase de Altura (Gaps)**: Eliminación del recargo acumulativo de `+ 0.1` en `techo_z1.py` para asegurar que el techo descanse directamente sobre los muros.
- **Alineación en X/Y**: Corrección de desfases en `techo_z1.py` usando `y_base` (puerta-dependiente) y compensando la extrusión centrada en X.
- **Pivote de Rotación**: Rotación vertical de techos especiales corregida para usar el pivote `(desplazamiento_x, desplazamiento_y, 0)` después de la traslación, logrando perfecta alineación con los muros y columnas.
- **Duplicidad de Techos**: Modificación en `techo.py` para evitar generar una losa plana redundante en el nivel superior en zonas costeras o de lluvia (`z1` y `z3`).
- **Clasificación de Región**: Integración de `get_zona_provincia` en la clasificación del pipeline para configurar dinámicamente `zona_climatica` en `CONFIG_PROYECTO`.

# [DOCUMENTACIÓN] Resiliencia ante Ausencia de Servicios de Nube (AWS S3 y Gemini) (Julio 2026)
Se añadieron controles de excepciones y fallbacks locales para garantizar la continuidad operativa de la aplicación sin depender obligatoriamente de servicios en la nube:
- **AWS S3 Fallback Local**: Si la carga del reporte PDF a S3 falla (por ejemplo, por falta de credenciales en el entorno), el archivo PDF generado se guarda localmente en la carpeta `local_pdfs/` y el endpoint `/project/generate-proinvierte/{project_id}` devuelve una URL local `/project/pdf-download/{project_id}`.
- **Endpoint de Descarga Local**: Se añadió la ruta `/project/pdf-download/{project_id}` en `route.py` para servir archivos PDF desde el almacenamiento local utilizando `FileResponse`.
- **Manejo de Errores de Render IA**: Se envolvió la llamada a `GeminiNanoBananaService` en `route.py` en un bloque `try/except`. Si falla por una clave de API inválida o problemas de conexión, se retorna una respuesta `HTMLResponse` limpia y estilizada detallando el error, en lugar de crashear el servidor con un código 500 y provocar bloqueos de CORS en el cliente.

# [DOCUMENTACIÓN] Robustez de Datos del Cuadro de Áreas en PDF (Julio 2026)
Se implementaron validaciones defensivas para asegurar la inclusión correcta del Cuadro Resumen de Áreas en el PDF:
- **Conversión de JSON Defensiva**: En `services.py`, se protege el descifrado de los campos `aforo` y `resumen_ambientes` de la base de datos para prevenir excepciones por campos nulos o ya pre-parseados.
- **Transformación Resistente a Fallas**: En `school_report_pdf.py`, las funciones `transform_areas` y `analizar_pisos_pabellon` fueron actualizadas con verificación de tipos y try/except para procesar la estructura de datos dinámicamente sin fallos por claves ausentes o tipos de datos inconsistentes (como listas de floats del segundo cuadrante), asegurando que el Cuadro Resumen de Áreas siempre se imprima en el PDF.

# [DOCUMENTACIÓN] Corrección de Inserción en Base de Datos para Campos Nuevos (Julio 2026)
Se solucionó un fallo de inserción al generar proyectos escolares debido a campos adicionales agregados al esquema de entrada:
- **Filtrado Dinámico de Columnas en Inserción**: En `repository.py`, dentro de `insert_new_project_school`, se filtran las claves del diccionario generado por el modelo Pydantic contra las columnas definidas en el modelo `ProjectDB` de SQLAlchemy antes de ejecutar la sentencia SQL `insert`. Esto evita errores de compilación (`CompileError: Unconsumed column names`) cuando se envían nuevos parámetros como `ambientes` o `number_floors` que no existen físicamente como columnas de la tabla `projects`.

# [DOCUMENTACIÓN] Corrección de Importación de Shapely Affinity (Julio 2026)
Se corrigió un error de ejecución en la generación geométrica:
- **NameError 'affinity' is not defined**: En `cuadrante_1.py`, se importó explícitamente `affinity` desde la librería `shapely` (`from shapely import affinity`). Esto resuelve el crash del worker de RQ al momento de des-normalizar y trasladar las coordenadas del cuadrante rectangular máximo al plano real de coordenadas UTM.

# [DOCUMENTACIÓN] Corrección del Desfase de Alineación de Techos Z1 y Z3 (Julio 2026)
Se corrigieron los errores de traslación horizontal que desplazaban los techos especiales de las edificaciones por la mitad de su tamaño de extrusión:
- **Techos Z1 (`techo_z1.py`)**: Se corrigió el desfase en X al remover el término sumatorio `+ (ancho_total_techo_x / 2)`. Ahora se traslada a `desplazamiento_x + ancho_total_techo_x` si hay rotación de 180° por puerta en "bottom", y a `desplazamiento_x` en caso contrario.
- **Techos Z3 (`techo_z3.py`)**: Se corrigió el desfase en Y al remover el término sumatorio `+ (ancho_total_techo_y / 2)`. Ahora el techo se traslada a `desplazamiento_y - e_muro` para centrarse perfectamente sobre los muros de la edificación.

# [DOCUMENTACIÓN] Corrección de Alineación del Techo Z3 y Evitación de Duplicación de Losas (Julio 2026)
Se realizaron las siguientes correcciones en el módulo de generación de techos para asegurar su correcto posicionamiento en 3D y evitar elementos redundantes:
- **Alineación y Rotación del Techo Z3 (`techo_z3.py`)**: Se corrigió el posicionamiento en Y usando la traslación `desplazamiento_y - e_muro + ancho_total_techo_y` para alinear el techo con el bloque en posición horizontal. Además, la rotación de 90° para orientación vertical ahora se realiza después de la traslación, pivotando sobre el centro del bloque `(desplazamiento_x, desplazamiento_y, 0)`.
- **Evitación de Duplicidad de Techos (`techo.py`)**: Se añadió una comprobación al inicio de `generate_techo` para omitir la generación de la losa plana si la zona climática configurada es `z1` o `z3`, ya que el techo especial de estas zonas se crea de forma independiente en `base_structure.py`.

# [DOCUMENTACIÓN] Corrección del Pivote y Dirección de Rotación de Escaleras (Julio 2026)
Se realizaron las siguientes correcciones en la generación de escaleras para garantizar su correcta alineación con el corredor:
- **Orientación y Pivote en Escaleras (`escaleras.py`)**: En `create_stairs`, se modificó la lógica para que la rotación dependa de la posición del corredor. Si el corredor está en el lado inferior (`bottom`), se rota `-90` grados alrededor de un pivote desplazado en X (`desplazamiento_x + ancho_total_escalera, desplazamiento_y, 0`) para orientar la escalera de cara al corredor inferior sin solapar las aulas. En caso de corredor superior (`top`), se mantiene la rotación de `90` grados sobre `(desplazamiento_x, desplazamiento_y, 0)`.
- **Actualización de Pruebas Unitarias (`test_stair_coordinates.py`)**: Se actualizaron las aserciones de límites de coordenadas en las pruebas unitarias para Secundaria e Inicial, reflejando el correcto desarrollo de la escalera hacia el corredor inferior (fuera del volumen del edificio principal).

# [DOCUMENTACIÓN] Rotación de Bloque Central, Alineación de Escaleras y Corrección de Pasadizos de Administración (Julio 2026)
Se realizaron las siguientes correcciones en el pipeline de geometría 3D para resolver las desalineaciones finales de escaleras y pabellones:
- **Rotación de Bloque Central (`cuadrante_1.py`)**: Se reemplazó la búsqueda abierta `find_next_best_rectangle` por una búsqueda directa a través de `find_max_rect_for_angle` utilizando el mismo ángulo de inclinación (`best_angle`) del primer cuadrante, garantizando que el bloque central (Inicial y SUM) quede perfectamente paralelo a los bloques perimetrales de acuerdo a la Tarea 1.
- **Corrección de Rotación y Conexión de Escaleras (`escaleras.py`, `base_structure.py`, `test_stair_coordinates.py`)**: Se corrigió el sentido de la rotación vertical de las escaleras en `escaleras.py` (rotando 90° para bottom y -90° para top con pivote desplazado por `largo_total`), logrando que el descanso de la escalera se sitúe de forma natural en el pasillo exterior (patio) y los tramos asciendan hacia la fachada. Se configuraron los offsets de conexión limpios (`desplazamiento_y` para bottom y `desplazamiento_y + ancho_hab` para top) en `base_structure.py` y se restauraron las aserciones de pruebas originales en `test_stair_coordinates.py` de acuerdo a la Tarea 2.
- **Corrección de Layout de Administración y Pasadizos (`cuadrante_1.py`)**: Se corrigió la recalculación de las divisiones de fase 2 usando `ancho_cuadrante` y los anchos reales del pabellón, y se intercambió la asignación de los pasadizos de Inicial y Admin en `cuadrante_1.py` que estaban cruzados. Esto alineó el pabellón de administración de dos niveles con su respectiva losa de circulación en el extremo derecho, integrándolo al conjunto.
- **Alineación de Techo Z3 (`techo_z3.py`)**: Se corrigieron los coeficientes de escala del largo de subida (`0.40`), bajada (`0.40`) y plano (`0.20`) para que sumen exactamente `1.0` en relación con el `largo_bloque_fijo`, logrando que el extremo derecho del techo termine flush en la coordenada exacta de la fachada de acuerdo a la Tarea 3.

# [DOCUMENTACIÓN] Reversión de Rotación de Escaleras e Inicialización de Variables de Cuadrantes (Julio 2026)
Se realizaron las siguientes correcciones para estabilizar la construcción del modelo 3D y evitar errores de ejecución:
- **Remoción de Doble Rotación de Escaleras (`base_structure.py`)**: Se eliminó el bloque condicional redundante de rotación de la escalera para orientación "vertical", ya que la función `create_stairs` ya realiza esta rotación internamente de forma correcta. Esto soluciona la desalineación y el desplazamiento incorrecto de las escaleras.
- **Robustez ante NameError en Flujo del Segundo Cuadrante (`cuadrante_1.py`)**: Se inicializaron las variables `largos_inicial` y `data_2do_cuadrante_builded` al inicio de la función `cuadrante_1`. Esto previene fallos por `NameError` (variables referenciadas antes de ser asignadas) cuando el flujo de ejecución activa el segundo cuadrante (`data_2do_cuadrante_builded_verif` es True).
- **Alineación de Escaleras con la Fachada (`base_structure.py`)**: Se reemplazó el parámetro `ancho_hab=0` por `ancho_hab=ancho_hab` en la llamada a `create_stairs`. Al pasar el ancho real, `create_stairs` calcula correctamente `y_base` (retrayendo la escalera contra el volumen del edificio), lo que evita que se desplace de más hacia el patio y asegura que quede pegada a la fachada.
