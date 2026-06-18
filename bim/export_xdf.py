import ezdxf
from shapely.geometry import Polygon, MultiPolygon
import math
from shapely import wkt

class ExportDXF:
    def __init__(self, filename="output.dxf"):
        self.filename = filename
        self.doc = ezdxf.new(setup=True)
        self.msp = self.doc.modelspace()
        self.layers_created = set()
        
    def normalize_geom(self, geom):
        if geom is None:
            return None

        # ya es shapely
        if isinstance(geom, (Polygon, MultiPolygon)):
            return geom

        # viene como string WKT
        if isinstance(geom, str):
            try:
                return wkt.loads(geom)
            except:
                return None

        return None

    def normalize_layer(self, value):
        if value is None:
            return "DEFAULT"
        return str(value).strip().upper()

    def ensure_layer(self, layer_name):
        if layer_name not in self.layers_created:
            if layer_name not in self.doc.layers:
                self.doc.layers.new(name=layer_name)
            self.layers_created.add(layer_name)

    def safe_piso(self, value):

        if value is None:
            return 1

        # 🔥 si viene como string
        if isinstance(value, str):
            v = value.strip().lower()

            if v in ["nan", "none", "null", ""]:
                return 1

            try:
                return int(float(v))
            except:
                return 1

        # 🔥 floats NaN reales
        if isinstance(value, float) and math.isnan(value):
            return 1

        try:
            v = int(value)
            return v if v > 0 else 1
        except:
            return 1

    # -------------------------
    #  MAIN EXPORT
    # -------------------------
    def export(self, data_list, max_pisos):

        if not isinstance(data_list, list):
            raise ValueError("Se espera una lista de diccionarios")

        if not isinstance(max_pisos, int) or max_pisos < 1:
            raise ValueError("max_pisos debe ser un entero >= 1")

        # 1. ancho máximo global
        max_height = self._get_max_height(data_list)
        offset_y = max_height + 10

        # 2. generar pisos artificiales
        for i in range(1, max_pisos + 1):
            y_offset = (i - 1) * offset_y

            for row in data_list:
                geom = self.normalize_geom(row.get("geometria"))

                if geom is None or (isinstance(geom, float) and math.isnan(geom)):
                    continue

                tipo = row.get("tipo")
                row_piso = self.safe_piso(row.get("piso"))

                if isinstance(row_piso, float) and math.isnan(row_piso):
                    row_piso = 1

                row_piso = int(row_piso)

                # -------------------------
                # max_rect en TODOS los pisos
                # -------------------------
                # if tipo == "max_rect":
                #     self._draw_geometry(geom, row, y_offset)
                #     continue

                # -------------------------
                # solo si coincide con piso
                # -------------------------
                if row_piso == i:
                    self._draw_geometry(geom, row, y_offset)

    # -------------------------
    #  DRAW GEOMETRY
    # -------------------------
    def _draw_geometry(self, geom, data, y_offset):

        if isinstance(geom, Polygon):
            self._add_polygon(geom, data, y_offset)

        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                self._add_polygon(poly, data, y_offset)

    # -------------------------
    #  POLYGON DRAW
    # -------------------------
    def _add_polygon(self, poly: Polygon, data: dict, y_offset):
        coords = list(poly.exterior.coords)

        layer = self.normalize_layer(data.get("tipo"))
        desc = data.get("description", "")

        self.ensure_layer(layer)

        # mover en Y por piso
        coords = [(x, y + y_offset) for x, y in coords]

        # estilo por tipo
        linetype = "DASHED" if layer == "AREA" else "CONTINUOUS"

        self.msp.add_lwpolyline(
            coords,
            close=True,
            dxfattribs={
                "layer": layer,
                "linetype": linetype
            }
        )

        # texto SOLO AULA
        if layer == "AULA" and desc:
            x, y = poly.centroid.x, poly.centroid.y

            self.msp.add_text(
                desc,
                dxfattribs={
                    "height": 0.4,
                    "layer": layer
                }
            ).set_placement((x, y + y_offset))

    # -------------------------
    #  MAX WIDTH
    # -------------------------
    def _get_max_width(self, data_list):
        max_w = 0

        for row in data_list:
            geom = row.get("geometria")
            if isinstance(geom, Polygon):
                minx, miny, maxx, maxy = geom.bounds
                max_w = max(max_w, maxx - minx)

        return max_w
    
    def _get_max_height(self, data_list):
        max_h = 0

        for row in data_list:
            geom = self.normalize_geom(row.get("geometria"))

            if isinstance(geom, Polygon):
                minx, miny, maxx, maxy = geom.bounds
                max_h = max(max_h, maxy - miny)

        return max_h

    # -------------------------
    def save(self):
        self.doc.saveas(self.filename)

def get_max_pisos(data_list):
    """
    Retorna el número máximo de pisos encontrados en la data.
    Usa el campo 'piso'.
    """

    max_piso = 1

    for row in data_list:
        p = row.get("piso", 1)

        # ignorar NaN
        if isinstance(p, float) and math.isnan(p):
            continue

        try:
            p = int(p)
            if p > max_piso:
                max_piso = p
        except:
            continue

    return max_piso