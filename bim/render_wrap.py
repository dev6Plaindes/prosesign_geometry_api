import plotly.graph_objects as go

def wrap_plotly_figure_in_html(fig: go.Figure) -> str:
    """
    Recibe un objeto Figure de Plotly y devuelve el string HTML
    con el contenedor personalizado.
    """
    plotly_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    
    html_template = f"""
    <div style="width: 75vw; border-radius: 8px; margin-bottom: 20px; padding-right: 300px">
        {plotly_html}
    </div>
    """
    
    return html_template