# ProDesign Geometry Service - Casos de Uso 📐

## 1. Generación de Proyecto Arquitectónico

### Descripción

Permite generar automáticamente una propuesta arquitectónica a partir de parámetros definidos del proyecto.

El sistema procesa información del terreno, requerimientos arquitectónicos y restricciones para generar:

- Distribución de ambientes.
- Planos arquitectónicos.
- Geometrías 2D.
- Modelo 3D.
- Información necesaria para cálculos posteriores.

---

## Actor

- Usuario de la plataforma ProDesign.
- Sistema ProDesign.
---

## Flujo Principal

1. El usuario envía una solicitud de generación de proyecto.
2. El sistema valida la información recibida.
3. El motor geométrico procesa las restricciones.
4. Se ejecutan algoritmos de optimización:
   - Rectangle Max.
   - Unpacking de ambientes.
5. Se generan los ambientes requeridos.
6. Se construyen elementos arquitectónicos:
   - Muros.
   - Puertas.
   - Ventanas.
   - Columnas.
   - Pisos.
   - Techos.
7. Se genera la geometría del proyecto.
8. El sistema almacena el resultado.
9. Se retorna un identificador de proceso/proyecto.

---

## Entrada

Información del proyecto:

- Datos del terreno.
- Dimensiones.
- Parámetros arquitectónicos.
- Tipo de infraestructura.
- Requerimientos de ambientes.
- Restricciones del diseño.

---

## Salida

Resultado de generación:

- ID del proyecto.
- Estado del proceso.
- Información geométrica generada.
- Datos para render.
- Datos para exportación CAD.

---

## Reglas de Negocio

- El terreno debe contener información geométrica válida.
- La distribución debe respetar restricciones espaciales.
- Los ambientes deben cumplir las relaciones definidas.
- La generación depende del tipo de infraestructura seleccionado.

---

# 2. Consulta de Estado de Generación (Jobs)

## Descripción

Permite consultar el estado de un proceso de generación arquitectónica.

---

## Actor

- Usuario de la plataforma.
- Sistema frontend.

---

## Flujo Principal

1. El usuario consulta un job mediante su identificador.
2. El sistema busca el estado del proceso.
3. Retorna la información actual.

---

## Entrada

- ID del job.

---

## Salida

Información del proceso:

- Estado.
- Resultado.
- Errores encontrados.
- Datos asociados.

---

## Reglas de Negocio

- Solo pueden consultarse jobs existentes.
- Un proceso puede tener estados:
  - Pendiente.
  - Procesando.
  - Completado.
  - Error.

---

# 3. Visualización de Proyecto Generado

## Descripción

Permite visualizar el proyecto generado en diferentes representaciones.

Tipos disponibles:

- Render 2D.
- Render 3D.
- Render mediante IA.

---

## Actor

- Usuario de plataforma.

---

## Flujo Principal

1. Usuario solicita visualización.
2. Sistema obtiene geometría almacenada.
3. Según el tipo solicitado:

### Render 3D

- Convierte geometría en modelo tridimensional.
- Renderiza mediante Plotly.

### Render 2D

- Convierte geometrías en representación plana.
- Organiza componentes por niveles.
- Genera visualización.

### Render IA

- Genera imagen base del modelo 3D.
- Envía imagen al servicio de IA.
- Obtiene render arquitectónico.

---

## Entrada

- ID del proyecto.
- Tipo de render:

Valores:

- 2d
- 3d
- render ia

---

## Salida

- Vista HTML interactiva.
- Imagen renderizada.
- Modelo visual del proyecto.

---

## Reglas de Negocio

- El proyecto debe existir.
- Debe contar con geometría generada.
- El tipo de render debe ser válido.

---

# 4. Cálculo de Costos de Infraestructura

## Descripción

Permite calcular costos preliminares de infraestructura utilizando la información generada del proyecto arquitectónico.

---

## Actor

- Usuario.
- Sistema ProDesign.

---

## Flujo Principal

1. Usuario solicita cálculo de costos.
2. Sistema obtiene información del proyecto.
3. Procesa:
   - Áreas.
   - Ambientes.
   - Distribución.
   - Parámetros económicos.
4. Ejecuta pipeline de costos.
5. Genera resultado económico.

---

## Entrada

- ID del proyecto.
- Parámetros de costos.

---

## Salida

Información calculada:

- Costos estimados.
- Resumen del cálculo.
- Información asociada al proyecto.

---

## Reglas de Negocio

- El proyecto debe existir.
- Debe contar con información arquitectónica generada.
- Los costos dependen de los parámetros configurados.

---

# 5. Generación de Reporte ProInvierte

## Descripción

Genera un reporte del proyecto para procesos de evaluación y presentación.

---

## Actor

- Sistema ProDesign.
- Sistema Proinvierte.

---

## Flujo Principal

1. Usuario solicita reporte.
2. Sistema obtiene información del proyecto.
3. Procesa datos arquitectónicos.
4. Genera documento final.

---

## Entrada

- ID del proyecto.

---

## Salida

- URL del documento generado.
- Información del reporte.

---

## Reglas de Negocio

- El proyecto debe existir.
- Debe tener información generada previamente.

---

# 6. Consulta de Proyecto

## Descripción

Permite obtener la información almacenada de un proyecto generado.

---

## Actor

- Usuario.

---

## Flujo Principal

1. Usuario solicita proyecto.
2. Sistema consulta almacenamiento.
3. Retorna información.

---

## Entrada

- ID del proyecto.

---

## Salida

- Datos generales.
- Geometrías.
- Información generada.

---

# 7. Consulta de Proyectos

## Descripción

Permite listar proyectos disponibles dentro del sistema.

---

## Actor

- Usuario.

---

## Flujo Principal

1. Usuario solicita listado.
2. Sistema consulta proyectos.
3. Retorna información.

---

## Entrada

Sin parámetros.

---

## Salida

Listado de proyectos registrados.
