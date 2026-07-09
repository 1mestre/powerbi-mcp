import pbi_connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os

def main():
    port = "60393"
    connector = pbi_connector.PowerBIConnector(port)
    
    # Consulta DAX agrupada por País y Marca
    dax_query = """
    EVALUATE SUMMARIZECOLUMNS(
        'Base_Datos_Consolidada'[Country],
        'Base_Datos_Consolidada'[Brand],
        "Net Sales USD", SUM('Base_Datos_Consolidada'[Net Sales USD]),
        "Costs USD", SUM('Base_Datos_Consolidada'[Costs USD]),
        "Gross Margin USD", SUM('Base_Datos_Consolidada'[Gross Margin USD])
    )
    """
    
    print("Ejecutando consulta DAX contra la instancia de Power BI local...")
    try:
        data = connector.execute_query(dax_query)
    except Exception as e:
        print(f"Error al ejecutar la consulta DAX: {e}")
        return
    
    if not data:
        print("No se obtuvieron datos de la consulta.")
        return
        
    df = pd.DataFrame(data)
    
    # Limpiar y renombrar las columnas que vienen del modelo tabular
    rename_map = {}
    for col in df.columns:
        if "Country" in col:
            rename_map[col] = "Country"
        elif "Brand" in col:
            rename_map[col] = "Brand"
        elif "Net Sales USD" in col:
            rename_map[col] = "NetSales"
        elif "Costs USD" in col:
            rename_map[col] = "Costs"
        elif "Gross Margin USD" in col:
            rename_map[col] = "Margin"
            
    df = df.rename(columns=rename_map)
    
    # Convertir columnas numéricas de forma segura
    df['NetSales'] = pd.to_numeric(df['NetSales'], errors='coerce').fillna(0)
    df['Costs'] = pd.to_numeric(df['Costs'], errors='coerce').fillna(0)
    df['Margin'] = pd.to_numeric(df['Margin'], errors='coerce').fillna(0)
    
    print(f"Cargados {len(df)} registros agregados.")
    
    # --- CONSTRUCCIÓN DEL DASHBOARD INTERACTIVO ---
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Ventas Netas y Costos por País (USD)", "Top 10 Marcas por Margen Bruto (USD)"),
        vertical_spacing=0.15
    )
    
    # 1. Ventas Netas y Costos por País
    df_country = df.groupby('Country')[['NetSales', 'Costs']].sum().reset_index()
    df_country = df_country.sort_values(by='NetSales', ascending=False)
    
    fig.add_trace(
        go.Bar(
            x=df_country['Country'],
            y=df_country['NetSales'],
            name='Ventas Netas',
            marker_color='#10b981', # Verde esmeralda
            hovertemplate='País: %{x}<br>Ventas: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df_country['Country'],
            y=df_country['Costs'],
            name='Costos',
            marker_color='#f43f5e', # Rosa/Rojo
            hovertemplate='País: %{x}<br>Costos: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Margen Bruto por Marca (Top 10)
    df_brand = df.groupby('Brand')['Margin'].sum().reset_index()
    df_brand = df_brand.sort_values(by='Margin', ascending=False).head(10)
    
    fig.add_trace(
        go.Bar(
            x=df_brand['Brand'],
            y=df_brand['Margin'],
            name='Margen Bruto',
            marker_color='#3b82f6', # Azul premium
            hovertemplate='Marca: %{x}<br>Margen: $%{y:,.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Diseño Premium
    fig.update_layout(
        title={
            'text': "Análisis de Datos de Power BI Desktop",
            'y':0.96,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#f8fafc', 'family': 'Segoe UI, Helvetica, sans-serif'}
        },
        template='plotly_dark',
        paper_bgcolor='#0f172a', # Fondo general Slate-900
        plot_bgcolor='#1e293b',  # Fondo del gráfico Slate-800
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=850,
        barmode='group',
        font=dict(
            family="Segoe UI, Tahoma, Geneva, Verdana, sans-serif",
            color="#94a3b8"
        )
    )
    
    # Ajustar estilos de los subplots
    fig.update_xaxes(showgrid=False, tickfont=dict(color='#cbd5e1'))
    fig.update_yaxes(showgrid=True, gridcolor='#334155', tickfont=dict(color='#cbd5e1'))
    
    output_html = "dashboard.html"
    fig.write_html(output_html)
    abs_path = os.path.abspath(output_html)
    print(f"¡Hecho! El dashboard interactivo se guardó en: {abs_path}")
    
    # Abrir en el navegador por defecto
    webbrowser.open(f"file:///{abs_path}")

if __name__ == "__main__":
    main()
