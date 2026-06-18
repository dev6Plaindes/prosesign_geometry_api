import os
from typing import TypedDict, List
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from utils.logger import logger
from io import BytesIO

from reportlab.lib.pagesizes import A4, landscape

def transform_areas(raw_data: list[dict]) -> list[list]:
    result = []

    for nivel_dict in raw_data:
        for nivel, filas in nivel_dict.items():

            for fila in filas:  # filas del nivel
                for ambiente in fila:  # ambientes

                    nombre = ambiente["ambiente"]
                    area = ambiente["largo"] * 8
                    pabellon = ambiente["pabellon"]
                    piso = ambiente["piso"]
                    

                    result.append([
                        nombre,
                        pabellon,
                        piso,
                        f"{area:.2f} m²"
                    ])

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

from typing import Dict, Any

def calcular_total_alumnos(aforo: Dict[str, Dict[str, Any]]) -> int:
    return sum(
        data["cantidad_aulas"] * data["aforo_por_grado"]
        for data in aforo.values()
    )
    
import json
from typing import Dict, Any

def analizar_pisos_pabellon(resumen_ambientes: str) -> Dict[str, int]:
    """
    Retorna número de pisos por pabellón a partir del JSON string.
    """

    data = json.loads(resumen_ambientes)  # 1️⃣ string -> lista de dicts

    resultado = {}

    for bloque in data:
        for pabellon, grupos in bloque.items():

            # grupos = [[piso1_items], [piso2_items], ...]
            pisos = set()

            for grupo in grupos:
                for item in grupo:
                    pisos.add(item["piso"])

            resultado[pabellon] = len(pisos)

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

class SchoolReportePDF:
    def __init__(self, data_project: dict = None, output_path: str = "output.pdf"):
        self.data_project = data_project or {}
        self.output_path = output_path
        self.c = canvas.Canvas(output_path, pagesize=A4)
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
        self.reset_cursor()
        self.draw_title("1. INFORMACIÓN GENERAL DEL PROYECTO", size=14)

        pisos_pabellon = self.data_project.get("pisos_pabellon", {})
        pisos_texto = ", ".join(f"{k.capitalize()} ({v})" for k, v in pisos_pabellon.items())
        created_at = self.data_project.get("created_at", "")
        
        data = [
            ["Campo", "Información"],
            ["Nombre del proyecto", self.data_project.get("name", "")],
            ["Nivel educativo", self.data_project.get("tipo_institucion", "")],
            ["Número de alumnos", self.data_project.get("total_alumnos", "")],
            ["Número de pisos", pisos_texto],
            ["Ubicación", self.data_project.get("ubication", "")],
            ["Área aproximada", ""],
            ["Fecha de generación", created_at],
        ]

        table = Table(data, colWidths=[200, 280])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 8),
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
        self.reset_cursor()
        self.draw_title("3. CUADRO RESUMEN DE ÁREAS")

        table_data = [["Ambiente", "Pabellon", "Nivel/Piso", "Área"]] + data_areas
        table = Table(table_data, colWidths=[180, 100, 100, 100])
        
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgrey),
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
