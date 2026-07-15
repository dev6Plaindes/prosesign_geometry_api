# [DOCUMENTACIÓN] Render 2D por niveles con navegación interactiva (tabs + scroll)
# Este módulo genera HTML navegable con tabs por piso y scroll vertical
import plotly.graph_objects as go
import re
from bim.utils.color_map import get_ambiente_style

def obtener_estilo(nombre):
    """Busca estilo por nombre (reutiliza lógica existente de render_2d)"""
    from bim.render_2d import ESTILOS
    for clave, estilo in ESTILOS.items():
        if clave in nombre:
            return estilo
    return ESTILOS["DEFAULT"]

def render_2d_por_nivel(escena_shapely, titulo="Plano 2D", height_per_level=700):
    """
    Genera un HTML navegable con:
    - Tabs superiores para cambiar entre niveles
    - Scroll vertical para ver todos los niveles
    - Leyenda interactiva
    - Responsive
    """
    
    # 1. Clasificar elementos por nivel (reutiliza lógica de render_2d_shapely_automatico_regex)
    elementos_por_nivel = {}
    elementos_globales = []
    
    for nombre, coleccion in escena_shapely.items():
        if "Base Cuadrante" in nombre or "Terreno" in nombre:
            elementos_globales.append((nombre, coleccion))
            continue
        
        coincidencia = re.search(r"(Nivel\s+\d+)", nombre)
        if coincidencia:
            nivel = coincidencia.group(1)
        else:
            nivel = "General"
            
        if nivel not in elementos_por_nivel:
            elementos_por_nivel[nivel] = []
        elementos_por_nivel[nivel].append((nombre, coleccion))
    
    # Inyectar globales en cada nivel
    for nivel in elementos_por_nivel:
        elementos_por_nivel[nivel].extend(elementos_globales)
    
    # Si solo hay globales, crear nivel "General"
    if not elementos_por_nivel and elementos_globales:
        elementos_por_nivel["General"] = elementos_globales
    
    # Ordenar niveles: Nivel 1, Nivel 2, ..., General
    def sort_nivel(n):
        m = re.search(r"Nivel\s+(\d+)", n)
        return (0, int(m.group(1))) if m else (1, 0)
    
    niveles_ordenados = sorted(elementos_por_nivel.keys(), key=sort_nivel)
    
    # 2. Generar figura Plotly por nivel
    figuras = {}
    all_bounds = []  # Para calcular límites globales
    
    for nivel in niveles_ordenados:
        elementos = elementos_por_nivel[nivel]
        fig = go.Figure()
        
        for nombre, coleccion in elementos:
            estilo = obtener_estilo(nombre)
            x_lines, y_lines = [], []
            
            for geom in coleccion.geoms:
                if geom.geom_type == "Polygon":
                    x_coords, y_coords = geom.exterior.xy
                    x_lines.extend(list(x_coords) + [None])
                    y_lines.extend(list(y_coords) + [None])
                    
                    # Recalcular bounds para escala global
                    bounds = geom.bounds
                    all_bounds.append(bounds)
                    
                    # Relleno exacto del polígono (no rectangular)
                    if estilo["fill_color"]:
                        x_fill, y_fill = geom.exterior.xy
                        fig.add_trace(go.Scatter(
                            x=list(x_fill), y=list(y_fill),
                            fill="toself", fillcolor=estilo["fill_color"],
                            mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
                            legendgroup=nombre, showlegend=False,
                            hoveron="fills", hovertemplate=f"<b>{nombre}</b><extra></extra>",
                        ))
                    
                    # Huecos internos
                    for interior in geom.interiors:
                        x_int, y_int = interior.xy
                        x_lines.extend(list(x_int) + [None])
                        y_lines.extend(list(y_int) + [None])
                        
                elif geom.geom_type == "LineString":
                    x_coords, y_coords = geom.xy
                    x_lines.extend(list(x_coords) + [None])
                    y_lines.extend(list(y_coords) + [None])
            
            # Borde
            if x_lines:
                fig.add_trace(go.Scatter(
                    x=x_lines, y=y_lines, mode="lines",
                    line=dict(color=estilo["line_color"], width=estilo["line_width"], dash=estilo["dash"]),
                    legendgroup=nombre, showlegend=False, hoverinfo="skip"
                ))
            
            # Leyenda (marker invisible con color)
            if estilo["fill_color"] and estilo["legend"]:
                fig.add_trace(go.Scatter(
                    x=[None], y=[None], mode="markers",
                    marker=dict(size=12, color=estilo["fill_color"], symbol="square"),
                    name=nombre, legendgroup=nombre, showlegend=True,
                    hoverinfo="skip"
                ))
        
        # Layout por nivel
        fig.update_layout(
            title=f"{titulo} - {nivel}",
            xaxis_title="X (m)", yaxis_title="Y (m)",
            yaxis_scaleanchor="x",  # aspect ratio 1:1
            template="plotly_white",
            height=height_per_level,
            legend=dict(groupclick="toggleitem", orientation="v", x=1.02, y=1),
            margin=dict(l=60, r=180, t=60, b=60),
            hovermode="closest",
        )
        
        figuras[nivel] = fig
    
    # 3. Calcular rango global X/Y para sincronizar zoom/pan entre niveles
    if all_bounds:
        min_x = min(b[0] for b in all_bounds) - 2
        max_x = max(b[2] for b in all_bounds) + 2
        min_y = min(b[1] for b in all_bounds) - 2
        max_y = max(b[3] for b in all_bounds) + 2
    else:
        min_x, max_x, min_y, max_y = -10, 10, -10, 10
    
    for fig in figuras.values():
        fig.update_xaxes(range=[min_x, max_x])
        fig.update_yaxes(range=[min_y, max_y], scaleanchor="x", scaleratio=1)
    
    # 4. Generar HTML con navegación (tabs + scroll)
    return _generar_html_navegable(figuras, niveles_ordenados, titulo, min_x, max_x, min_y, max_y)

def _generar_html_navegable(figuras, niveles, titulo, min_x, max_x, min_y, max_y):
    """Genera HTML standalone con tabs, scroll y sincronía de zoom"""
    
    # Convertir cada figura a div HTML (sin wrapper completo)
    divs_niveles = {}
    for nivel, fig in figuras.items():
        # plotly.js incluye el div con id único
        html = fig.to_html(include_plotlyjs=False, full_html=False, div_id=f"plot-{nivel.replace(' ', '-')}")
        divs_niveles[nivel] = html
    
    # IDs para tabs
    nivel_ids = [n.replace(" ", "-") for n in niveles]
    
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <script src="https://cdn.plot.ly/plotly-3.6.0.min.js" charset="utf-8"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5; 
            min-height: 100vh;
        }}
        .header {{
            background: #1e3a5f; color: white;
            padding: 16px 24px;
            position: sticky; top: 0; z-index: 100;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 1.25rem; font-weight: 600; }}
        .header .subtitle {{ font-size: 0.875rem; opacity: 0.8; margin-top: 4px; }}
        
        /* Tabs de navegación */
        .nav-tabs {{
            display: flex;
            gap: 4px;
            padding: 12px 24px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
            position: sticky; top: 68px; z-index: 99;
            overflow-x: auto;
            flex-wrap: wrap;
        }}
        .nav-tab {{
            padding: 8px 16px;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            background: #fafafa;
            color: #333;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .nav-tab:hover {{ background: #f0f0f0; border-color: #bbb; }}
        .nav-tab.active {{
            background: #1e3a5f; color: white; border-color: #1e3a5f;
        }}
        .nav-tab .level-badge {{
            display: inline-block;
            min-width: 20px; height: 20px;
            background: #4a90d9; color: white;
            border-radius: 10px; font-size: 0.7rem;
            padding: 0 6px; margin-left: 6px;
            line-height: 20px; text-align: center;
        }}
        .nav-tab.active .level-badge {{ background: #fff; color: #1e3a5f; }}
        
        /* Contenedor principal con scroll */
        .main-container {{ padding: 24px; max-width: 1400px; margin: 0 auto; }}
        
        /* Panel de nivel */
        .level-panel {{
            display: none;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            overflow: hidden;
            margin-bottom: 24px;
        }}
        .level-panel.active {{ display: block; animation: fadeIn 0.2s; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
        
        .level-header {{
            padding: 16px 24px;
            background: #f8f9fa;
            border-bottom: 1px solid #eee;
            display: flex; justify-content: space-between; align-items: center;
        }}
        .level-title {{ font-size: 1.1rem; font-weight: 600; color: #1e3a5f; }}
        .level-info {{ font-size: 0.8rem; color: #666; }}
        
        .plotly-container {{ width: 100%; height: 700px; }}
        
        /* Scroll indicator */
        .scroll-hint {{
            text-align: center; padding: 16px; color: #888; font-size: 0.85rem;
            background: linear-gradient(to bottom, transparent, #f5f5f5);
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .header {{ padding: 12px 16px; }}
            .nav-tabs {{ padding: 8px 16px; }}
            .nav-tab {{ padding: 6px 12px; font-size: 0.8rem; }}
            .main-container {{ padding: 16px; }}
            .plotly-container {{ height: 500px; }}
        }}
        
        /* Print styles */
        @media print {{
            .header, .nav-tabs, .scroll-hint {{ display: none; }}
            .level-panel {{ display: block !important; page-break-after: always; }}
            .plotly-container {{ height: 600px; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>{titulo}</h1>
        <div class="subtitle">{len(niveles)} nivel(es) — Click en tabs o usa scroll</div>
    </header>
    
    <nav class="nav-tabs" role="tablist" aria-label="Niveles del edificio">
"""
    
    for i, (nivel, nid) in enumerate(zip(niveles, nivel_ids)):
        active = ' active' if i == 0 else ''
        # Extraer número de nivel para badge
        m = re.search(r"Nivel\s+(\d+)", nivel)
        badge = f'<span class="level-badge">{m.group(1)}</span>' if m else ''
        html_template += f'''
        <button class="nav-tab{active}" role="tab" aria-selected="{'true' if i==0 else 'false'}" 
                data-target="#panel-{nid}" onclick="switchLevel('{nid}')">
            {nivel}{badge}
        </button>'''
    
    html_template += """
    </nav>
    
    <main class="main-container">
"""
    
    for i, (nivel, nid) in enumerate(zip(niveles, nivel_ids)):
        active = ' active' if i == 0 else ''
        html_template += f'''
        <section id="panel-{nid}" class="level-panel{active}" role="tabpanel" aria-labelledby="tab-{nid}">
            <div class="level-header">
                <span class="level-title">{nivel}</span>
                <span class="level-info">Planta arquitectónica</span>
            </div>
            <div class="plotly-container" id="plot-{nid}-container">
                {divs_niveles[nivel]}
            </div>
        </section>
'''
    
    html_template += """
        <div class="scroll-hint">
            💡 Desplázate hacia abajo para ver más niveles | Usa las pestañas arriba para navegación rápida
        </div>
    </main>
    
    <script>
        // Sincronía de zoom/pan entre niveles
        let isSyncing = false;
        const plotDivs = {};
        
        // Inicializar referencias a los divs de Plotly
        document.querySelectorAll('.plotly-container > div[id^="plot-"]').forEach(div => {
            const levelId = div.id.replace('plot-', '').replace('-container', '');
            plotDivs[levelId] = div;
        });
        
        function switchLevel(targetId) {
            // Tabs
            document.querySelectorAll('.nav-tab').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.target === '#panel-' + targetId);
                btn.setAttribute('aria-selected', btn.dataset.target === '#panel-' + targetId);
            });
            // Panels
            document.querySelectorAll('.level-panel').forEach(panel => {
                panel.classList.toggle('active', panel.id === 'panel-' + targetId);
            });
            // Scroll suave al panel
            document.getElementById('panel-' + targetId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        // Sincronizar zoom/pan (relayout) entre todos los niveles visibles
        function attachSync(div, levelId) {
            div.on('plotly_relayout', function(eventData) {
                if (isSyncing) return;
                // Solo sincronizar xaxis.range y yaxis.range
                const xRange = eventData['xaxis.range[0]'] !== undefined ? 
                    [eventData['xaxis.range[0]'], eventData['xaxis.range[1]']] : 
                    (eventData['xaxis.range'] || null);
                const yRange = eventData['yaxis.range[0]'] !== undefined ? 
                    [eventData['yaxis.range[0]'], eventData['yaxis.range[1]']] : 
                    (eventData['yaxis.range'] || null);
                
                if (xRange || yRange) {
                    isSyncing = true;
                    Object.entries(plotDivs).forEach(([otherId, otherDiv]) => {
                        if (otherId !== levelId && otherDiv._fullLayout) {
                            const update = {};
                            if (xRange) update['xaxis.range'] = xRange;
                            if (yRange) update['yaxis.range'] = yRange;
                            if (Object.keys(update).length) {
                                Plotly.relayout(otherDiv, update).catch(() => {});
                            }
                        }
                    });
                    isSyncing = false;
                }
            });
        }
        
        // Inicializar sincronía cuando Plotly esté listo
        document.addEventListener('DOMContentLoaded', function() {
            // Esperar a que los plots se rendericen
            setTimeout(() => {
                Object.entries(plotDivs).forEach(([levelId, div]) => {
                    if (div && div._fullLayout) attachSync(div, levelId);
                });
            }, 500);
        });
        
        // Soporte teclado: flechas izquierda/derecha para cambiar nivel
        document.addEventListener('keydown', (e) => {
            const activeTab = document.querySelector('.nav-tab.active');
            if (!activeTab) return;
            const tabs = Array.from(document.querySelectorAll('.nav-tab'));
            const idx = tabs.indexOf(activeTab);
            if (e.key === 'ArrowRight' && idx < tabs.length - 1) {
                tabs[idx + 1].click();
            } else if (e.key === 'ArrowLeft' && idx > 0) {
                tabs[idx - 1].click();
            }
        });
    </script>
</body>
</html>
"""
    
    return html_template


def wrap_plotly_figure_in_html(fig, title="Render 2D"):
    """Wrapper compatible con endpoint existente - delega a render_2d_por_nivel si es dict por niveles"""
    if isinstance(fig, dict):  # escena_shapely
        return render_2d_por_nivel(fig, titulo=title)
    return fig.to_html(include_plotlyjs='cdn', full_html=True)


# Función helper para endpoint
def generar_html_planta_2d_navegable(escena_shapely, titulo="Plano 2D"):
    """Punto de entrada único para el endpoint /project-render con render=2d-nav"""
    return render_2d_por_nivel(escena_shapely, titulo=titulo)