import pbi_connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
import sys

def main():
    # Detect running instances
    instances = pbi_connector.get_active_pbi_instances()
    if not instances:
        print("Error: No active Power BI Desktop instances found.")
        sys.exit(1)
        
    # Use the first active instance detected
    port = instances[0]['port']
    print(f"Connecting to Power BI Desktop instance on port: {port}")
    connector = pbi_connector.PowerBIConnector(port)
    
    # DAX query grouped by Country and Brand
    dax_query = """
    EVALUATE SUMMARIZECOLUMNS(
        'Base_Datos_Consolidada'[Country],
        'Base_Datos_Consolidada'[Brand],
        "Net Sales USD", SUM('Base_Datos_Consolidada'[Net Sales USD]),
        "Costs USD", SUM('Base_Datos_Consolidada'[Costs USD]),
        "Gross Margin USD", SUM('Base_Datos_Consolidada'[Gross Margin USD])
    )
    """
    
    print("Executing DAX query against local Analysis Services engine...")
    try:
        data = connector.execute_query(dax_query)
    except Exception as e:
        print(f"Error executing DAX query: {e}")
        sys.exit(1)
    
    if not data:
        print("No data returned from the query.")
        return
        
    df = pd.DataFrame(data)
    
    # Normalize column names returned from the tabular model
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
    
    # Safely convert column types to numeric
    df['NetSales'] = pd.to_numeric(df['NetSales'], errors='coerce').fillna(0)
    df['Costs'] = pd.to_numeric(df['Costs'], errors='coerce').fillna(0)
    df['Margin'] = pd.to_numeric(df['Margin'], errors='coerce').fillna(0)
    
    print(f"Successfully loaded {len(df)} aggregated records.")
    
    # --- BUILD INTERACTIVE DASHBOARD WITH PLOTLY ---
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Net Sales & Costs by Country (USD)", "Top 10 Brands by Gross Margin (USD)"),
        vertical_spacing=0.15
    )
    
    # 1. Net Sales & Costs by Country
    df_country = df.groupby('Country')[['NetSales', 'Costs']].sum().reset_index()
    df_country = df_country.sort_values(by='NetSales', ascending=False)
    
    fig.add_trace(
        go.Bar(
            x=df_country['Country'],
            y=df_country['NetSales'],
            name='Net Sales',
            marker_color='#10b981', # Emerald green
            hovertemplate='Country: %{x}<br>Sales: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df_country['Country'],
            y=df_country['Costs'],
            name='Costs',
            marker_color='#f43f5e', # Rose/Red
            hovertemplate='Country: %{x}<br>Costs: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Gross Margin by Brand (Top 10)
    df_brand = df.groupby('Brand')['Margin'].sum().reset_index()
    df_brand = df_brand.sort_values(by='Margin', ascending=False).head(10)
    
    fig.add_trace(
        go.Bar(
            x=df_brand['Brand'],
            y=df_brand['Margin'],
            name='Gross Margin',
            marker_color='#3b82f6', # Premium Blue
            hovertemplate='Brand: %{x}<br>Margin: $%{y:,.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Premium Layout Configuration
    fig.update_layout(
        title={
            'text': "Power BI Local Data Analysis Dashboard",
            'y':0.96,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#f8fafc', 'family': 'Segoe UI, Helvetica, sans-serif'}
        },
        template='plotly_dark',
        paper_bgcolor='#0f172a', # Slate-900 general background
        plot_bgcolor='#1e293b',  # Slate-800 chart background
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
    
    # Adjust axes styling
    fig.update_xaxes(showgrid=False, tickfont=dict(color='#cbd5e1'))
    fig.update_yaxes(showgrid=True, gridcolor='#334155', tickfont=dict(color='#cbd5e1'))
    
    output_html = "dashboard.html"
    fig.write_html(output_html)
    abs_path = os.path.abspath(output_html)
    print(f"Success! Interactive dashboard saved to: {abs_path}")
    
    # Open dashboard in default browser
    webbrowser.open(f"file:///{abs_path}")

if __name__ == "__main__":
    main()
