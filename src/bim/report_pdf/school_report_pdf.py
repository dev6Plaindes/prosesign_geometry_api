import os
from typing import TypedDict, List
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from src.utils.logger import logger
from io import BytesIO

from reportlab.lib.pagesizes import A4, landscape

def transform_areas(raw_data: list[dict]) -> list[list]:
    # [DOCUMENTACIÓN] Se robusteció la función transform_areas con validaciones de tipo, métodos .get() y try/except para evitar caídas en caso de datos nulos o malformados en resumen_ambientes
    result = []
    if not raw_data or not isinstance(raw_data, list):
        return result

    try:
        for nivel_dict in raw_data:
            if not isinstance(nivel_dict, dict):
                continue
            for nivel, filas in nivel_dict.items():
                if not isinstance(filas, list):
                    continue

                for fila in filas:  # filas del nivel
                    if not isinstance(fila, list):
                        continue
                    for ambiente in fila:  # ambientes
                        if not isinstance(ambiente, dict):
                            continue

                        nombre = ambiente.get("ambiente", "Desconocido")
                        largo = ambiente.get("largo", 0)
                        try:
                            area = float(largo) * 8
                        except (ValueError, TypeError):
                            area = 0.0
                        pabellon = ambiente.get("pabellon", "Desconocido")
                        piso = ambiente.get("piso", "Desconocido")
                        

                        result.append([
                            nombre,
                            pabellon,
                            piso,
                            f"{area:.2f} m²"
                        ])
    except Exception as e:
        logger.error(f"[DOCUMENTACIÓN] Error transformando áreas para reporte: {e}")

    return result


class DataProject(TypedDict):
    name: str
    niveles: List[str]
    total_alumnos: int


def _extract_nivel(filename: str) -> str:
    """MODELO_3D_CAPA_1.svg → 1"""
    name = filename.replace(".svg", "")
    parts = name.split("_")
    return parts[-1]


def _build_title(nivel: str) -> str:
    mapping = {
        "1": "Plano arquitectónico - Piso 1",
        "2": "Plano arquitectónico - Piso 2",
        "3": "Plano arquitectónico - Piso 3",
        "4": "Plano arquitectónico - Piso 4",
    }
    return mapping.get(nivel, f"Plano arquitectónico del nivel {nivel}")

from typing import List, Dict, Any

def calcular_total_alumnos(aforo: List[Dict[str, Any]]) -> int:
    return sum(
        item["cantidad_aulas"] * item["aforo_por_grado"]
        for item in aforo
    )
    
def analizar_pisos_pabellon(resumen_ambientes: list) -> Dict[str, int]:
    # [DOCUMENTACIÓN] Se robusteció la función analizar_pisos_pabellon para evitar excepciones con datos malformados
    resultado = {}
    if not resumen_ambientes or not isinstance(resumen_ambientes, list):
        return resultado

    try:
        for bloque in resumen_ambientes:
            if not isinstance(bloque, dict):
                continue
            for pabellon, grupos in bloque.items():
                if not isinstance(grupos, list):
                    continue

                pisos = set()

                for grupo in grupos:
                    if not isinstance(grupo, list):
                        continue
                    for item in grupo:
                        if isinstance(item, dict) and "piso" in item:
                            pisos.add(item["piso"])

                resultado[pabellon] = len(pisos)
    except Exception as e:
        logger.error(f"[DOCUMENTACIÓN] Error analizando pisos por pabellón: {e}")

    return resultado


import shutil
import logging

logger = logging.getLogger(__name__)

def limpiar_archivos(pdf_path: str, folder_path: str):
    # 1. borrar PDF
    try:
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"PDF eliminado: {pdf_path}")
    except Exception as e:
        logger.warning(f"No se pudo eliminar PDF: {e}")

    # 2. borrar carpeta completa
    try:
        if folder_path and os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            logger.info(f"Carpeta eliminada: {folder_path}")
    except Exception as e:
        logger.warning(f"No se pudo eliminar carpeta: {e}")

class NumberedCanvas(canvas.Canvas):
    # [DOCUMENTACIÓN] Clase NumberedCanvas para cabecera dinámica, pie de página confidencial y numeración automática de hojas
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Omitir en la portada
            
        width, height = self._pagesize
        
        # Omitir cabeceras y pies de página estándar en planos (páginas horizontales)
        if width > height:
            return

        self.saveState()
        
        # Cabecera
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1E3A8A"))
        self.drawString(50, height - 35, "PRODESIGN | REPORTE TÉCNICO DE INFRAESTRUCTURA")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#595959"))
        self.drawRightString(width - 50, height - 35, "PREPARADO PARA: PROINVIERTE")
        
        self.setStrokeColor(colors.HexColor("#D9D9D9"))
        self.setLineWidth(0.5)
        self.line(50, height - 42, width - 50, height - 42)
        
        # Pie de página
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#595959"))
        self.drawString(50, 35, "Documento de Planificación - Confidencial")
        
        self.drawRightString(width - 50, 35, f"Página {self._pageNumber} de {page_count}")
        
        self.line(50, 45, width - 50, 45)
        
        self.restoreState()


def obtener_medidas_terreno(data_project: dict) -> dict:
    # [DOCUMENTACIÓN] Obtener medidas del terreno basándose en la caja del cuadrante máximo guardado en vertices
    ancho = 61.5
    largo = 97.5
    
    vertices_str = data_project.get("vertices")
    if vertices_str:
        try:
            import json
            vertices_data = json.loads(vertices_str) if isinstance(vertices_str, str) else vertices_str
            for item in vertices_data:
                if isinstance(item, dict) and item.get("name") in ["max_cuadrante", "Cuadrante"]:
                    pts = item.get("vertices", [])
                    if pts:
                        xs = [pt[0] for pt in pts]
                        ys = [pt[1] for pt in pts]
                        ancho = max(xs) - min(xs)
                        largo = max(ys) - min(ys)
                        if ancho > largo:
                            ancho, largo = largo, ancho
                        break
        except Exception:
            pass
            
    area = ancho * largo
    perimetro = 2 * (ancho + largo)
    return {
        "ancho": ancho,
        "largo": largo,
        "area": area,
        "perimetro": perimetro
    }


class SchoolReportePDF:
    def __init__(self, data_project: dict = None, output_path: str = "output.pdf"):
        self.data_project = data_project or {}
        self.output_path = output_path
        self.c = NumberedCanvas(output_path, pagesize=A4)
        self.width, self.height = A4
       
        self.margin_left = 50
        self.margin_right = 50
        self.margin_top = 60
        self.margin_bottom = 60
        self.y = self.height - self.margin_top

    # =============================================================
    # CONTROL DE PÁGINA Y ORIENTACIÓN
    # =============================================================
    def new_page(self):
        self.c.showPage()
        self.reset_cursor()

    def reset_cursor(self):
        self.y = self.height - self.margin_top

    def check_page_break(self, needed_height: float):
        if self.y - needed_height < self.margin_bottom:
            self.new_page()

    def new_landscape_page(self):
        """Nueva página en orientación horizontal"""
        self.c.showPage()
        self.c.setPageSize(landscape(A4))
        self.width, self.height = landscape(A4)
        self.reset_cursor()

    def new_portrait_page(self):
        """Nueva página en orientación vertical"""
        self.c.showPage()
        self.c.setPageSize(A4)
        self.width, self.height = A4
        self.reset_cursor()

    # =============================================================
    # HELPERS DE DIBUJO
    # =============================================================
    def draw_title(self, text: str, size: int = 14):
        self.check_page_break(40)
        self.c.setFont("Helvetica-Bold", size)
        self.c.setFillColorRGB(0, 0, 0)
        self.c.drawString(self.margin_left, self.y, text)
        self.y -= 35

    def draw_table(self, table):
        available_width = self.width - 2 * self.margin_left
        w, h = table.wrap(available_width, self.height)
        self.check_page_break(h + 30)
        x = self.margin_left
        y = self.y - h
        table.drawOn(self.c, x, y)
        self.y = y - 20

    def draw_svg_full_page(self, drawing, title: str):
        """Cada SVG en su propia página horizontal"""
        self.new_landscape_page()

        margin = 35

        # Título
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawCentredString(self.width / 2, self.height - margin, title)

        # Área disponible
        available_width = self.width - (margin * 2)
        available_height = self.height - 100
        
        # Calcular escala máxima manteniendo proporción
        scale_x = available_width / drawing.width
        scale_y = available_height / drawing.height
        scale = min(scale_x, scale_y) * 0.99

        # Crear una copia del drawing para no afectar el original
        from copy import deepcopy
        drawing_copy = deepcopy(drawing)

        scaled_width = drawing_copy.width * scale
        scaled_height = drawing_copy.height * scale

        # Centrar en la página
        x = (self.width - scaled_width) / 2
        y = (self.height - scaled_height) / 2 - 10

        drawing_copy.scale(scale, scale)
        renderPDF.draw(drawing_copy, self.c, x, y)

    # =============================================================
    # MÉTODOS PÚBLICOS
    # =============================================================
    def portada(self):
        self.reset_cursor()
        logo_path = "public/logo_prodesign.png"
        if os.path.exists(logo_path):
            self.c.drawImage(
                logo_path,
                x=(self.width / 2) - 55,
                y=self.height - 170,
                width=110,
                height=110,
                preserveAspectRatio=True,
                mask='auto'
            )

        self.c.setFont("Helvetica", 12)
        self.c.setFillColorRGB(0.3, 0.4, 0.55)
        self.c.drawCentredString(self.width / 2, self.height - 230, "Proyecto:")
        
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawCentredString(
            self.width / 2,
            self.height - 260,
            self.data_project.get("name", "Proyecto sin nombre")
        )

        self.c.setFont("Helvetica", 12)
        self.c.drawCentredString(
            self.width / 2, 
            self.height - 310, 
            "Tipo de institución: Colegio"
        )

        self.new_page()

    def info_project(self):
        # [DOCUMENTACIÓN] Se rediseñó info_project para presentar la información general del proyecto alineada a los campos de ProInvierte
        self.reset_cursor()
        self.draw_title("1. INFORMACIÓN GENERAL DEL PROYECTO", size=14)

        pisos_pabellon = self.data_project.get("pisos_pabellon", {})
        pisos_texto = ", ".join(f"{k.capitalize()} ({v} pisos)" for k, v in pisos_pabellon.items()) if pisos_pabellon else "1 pisos"
        
        created_at = self.data_project.get("created_at", "")
        ubication = self.data_project.get("ubication")
        if not ubication:
            ubication = f"{self.data_project.get('distrito', '')}, {self.data_project.get('provincia', '')}, {self.data_project.get('departamento', '')}"
        
        zone = self.data_project.get("zone")
        if zone:
            ubication = f"{ubication} ({zone})"

        data = [
            ["Campo de Información", "Detalle Registrado"],
            ["Nombre del Proyecto", self.data_project.get("name", "")],
            ["Entidad Solicitante", self.data_project.get("client", "ALCALDE DE PICOTA")],
            ["Proyectista / Responsable", self.data_project.get("manager", "DR. LEON")],
            ["Tipología de Proyecto", self.data_project.get("tipo_institucion", "Educación (Colegio)")],
            ["Pisos por Pabellón / Bloque", pisos_texto],
            ["Ubicación Política", ubication],
            ["Fecha de Registro", created_at if created_at else "-"],
        ]

        table = Table(data, colWidths=[200, 280])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))

        self.draw_table(table)

    def add_aforo_table(self):
        # [DOCUMENTACIÓN] Nuevo método add_aforo_table para consolidar capacidad y aforos por nivel y calcular el total general
        self.y -= 15
        self.draw_title("2. CUADRO DE CAPACIDAD Y AFOROS", size=14)

        aforo_data = self.data_project.get("aforo", [])
        table_data = [["Nivel / Grado", "Cant. Aulas", "Aforo por Aula", "Capacidad Total"]]
        
        total_aulas = 0
        total_alumnos = 0

        for item in aforo_data:
            grado = item.get("grado", "Desconocido").upper()
            cant_aulas = item.get("cantidad_aulas", 0)
            aforo_aula = item.get("aforo_por_grado", 0)
            capacidad = cant_aulas * aforo_aula

            total_aulas += cant_aulas
            total_alumnos += capacidad

            table_data.append([
                grado,
                str(cant_aulas),
                str(aforo_aula),
                f"{capacidad} alumnos"
            ])

        table_data.append([
            "TOTAL GENERAL",
            str(total_aulas),
            "-",
            f"{total_alumnos} alumnos"
        ])

        table = Table(table_data, colWidths=[180, 100, 100, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F3F4F6")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ]))

        self.draw_table(table)

    def add_terrain_measurements_table(self):
        # [DOCUMENTACIÓN] Nuevo método add_terrain_measurements_table para detallar las dimensiones y áreas del terreno calculado
        self.y -= 15
        self.draw_title("3. CUADRO DE MEDIDAS Y DIMENSIONES DEL TERRENO", size=14)

        medidas = obtener_medidas_terreno(self.data_project)

        table_data = [
            ["Dimensión del Terreno", "Medida Real Calculada"],
            ["Ancho del Terreno", f"{medidas['ancho']:.1f} m"],
            ["Largo del Terreno", f"{medidas['largo']:.1f} m"],
            ["Perímetro del Terreno", f"{medidas['perimetro']:.1f} m"],
            ["Área Disponible del Terreno", f"{medidas['area']:.2f} m²"]
        ]

        table = Table(table_data, colWidths=[240, 240])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))

        self.draw_table(table)


    def add_svgs_from_folder(self, folder_path: str):
        """Cada SVG en una hoja aparte en orientación horizontal"""
        if not os.path.exists(folder_path):
            logger.warning(f"Carpeta no encontrada: {folder_path}")
            return

        svg_files = sorted([
            f for f in os.listdir(folder_path) if f.lower().endswith(".svg")
        ])

        for svg_file in svg_files:
            file_path = os.path.join(folder_path, svg_file)
            nivel = _extract_nivel(svg_file)
            titulo = _build_title(nivel)

            try:
                drawing = svg2rlg(file_path)
                self.draw_svg_full_page(drawing, titulo)
            except Exception as e:
                logger.exception(f"Error procesando {svg_file}: {e}")

        # Volver a orientación vertical después de todos los planos
        self.new_portrait_page()


    def add_area_summary_table(self, data_areas: list):
        # [DOCUMENTACIÓN] Se diseñó add_area_summary_table para soportar paginación manual de tablas largas en el canvas, evitando desbordamientos
        self.reset_cursor()
        self.draw_title("3. CUADRO RESUMEN DE ÁREAS")

        if not data_areas:
            data_areas = [["No hay ambientes registrados", "-", "-", "-"]]

        headers = ["Ambiente", "Pabellon", "Nivel/Piso", "Área"]
        
        # Paginación manual de la tabla (máximo 22 filas por página)
        rows_per_page = 22
        total_rows = len(data_areas)
        
        for i in range(0, total_rows, rows_per_page):
            chunk = data_areas[i:i+rows_per_page]
            table_data = [headers] + chunk
            
            table = Table(table_data, colWidths=[180, 100, 100, 100])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7F8C8D")), # Cabecera gris neutro premium
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]), # Alternancia de color
            ]))
            
            self.draw_table(table)
            
            # Si hay más filas, hacer un salto de página e imprimir el título de continuación
            if i + rows_per_page < total_rows:
                self.new_page()
                self.draw_title("3. CUADRO RESUMEN DE ÁREAS (CONTINUACIÓN)")


    def add_general_area_table(self, data: dict):
        self.reset_cursor()
        self.draw_title("7. RESUMEN GENERAL DE ÁREAS")

        table_data = [
            ["Concepto", "Valor"],
            ["Área de pabellones", data.get("area_pabellones", "")],
            ["Número de pisos", data.get("pisos_pabellones", "")],
            ["Área de pasadizos", data.get("area_pasadizos", "")],
            ["Área techada", data.get("area_techada", "")],
            ["Área libre", data.get("area_libre", "")],
        ]

        table = Table(table_data, colWidths=[320, 160])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))

        self.draw_table(table)

    def save(self):
        self.c.save()
        logger.info(f"PDF generado exitosamente: {self.output_path}")
        return self.output_path

    def save_to_bin(self):
        self.c.save()
        with open(self.output_path, "rb") as f:
            buffer = BytesIO(f.read())
        buffer.seek(0)
        return buffer
