import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# Configuración inicial
st.set_page_config(layout="wide", page_title="Dashboard Analítico")
st.sidebar.title("Configuración")

# Cargar datos desde Excel
EXCEL_FILE = "STREAMLIT/Cervezas y Sidras DeepDive/WorkShop Carulla.xlsx"
xls = pd.ExcelFile(EXCEL_FILE)
data_dict = {sheet: xls.parse(sheet, parse_dates=["MONTH"]) for sheet in xls.sheet_names}

# Mapeo de categorías y DataFrames
CATEGORIAS = {
    "Cervezas": {
        "super": data_dict.get('Turbo vs Super - Cervezas', pd.DataFrame()),
        "carulla": data_dict.get('Turbo vs Carulla - Cervezas', pd.DataFrame())
    },
    "Vinos": {
        "super": data_dict.get('Turbo vs Super - Vinos', pd.DataFrame()),
        "carulla": data_dict.get('Turbo vs Carulla - Vinos', pd.DataFrame())
    }
}

# Función para aplicar Pareto al 80%
def apply_pareto(df, metric_column='TOTAL_PRICE_USD_TURBO'):
    if df.empty:
        return df, []
    
    # Calcular participación por Maker
    maker_sales = df.groupby('MAKER')[metric_column].sum().reset_index()
    maker_sales = maker_sales.sort_values(metric_column, ascending=False)
    maker_sales['cum_pct'] = maker_sales[metric_column].cumsum() / maker_sales[metric_column].sum()
    
    # Identificar Makers clave (80%)
    pareto_makers = maker_sales[maker_sales['cum_pct'] <= 0.8]['MAKER'].tolist()
    other_makers = maker_sales[maker_sales['cum_pct'] > 0.8]['MAKER'].tolist()
    
    # Crear columna agrupada
    df['MAKER_GROUPED'] = np.where(df['MAKER'].isin(pareto_makers), df['MAKER'], 'Otros')
    
    # Ordenar por participación
    ordered_makers = maker_sales['MAKER'].tolist()[:len(pareto_makers)] + ['Otros']
    df['MAKER_GROUPED'] = pd.Categorical(
        df['MAKER_GROUPED'], 
        categories=ordered_makers,
        ordered=True
    )
    
    return df, pareto_makers

# Función base para estilos
def apply_style(fig, title):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': title,
            'font': {'size': 14}
        },
        legend={'font': {'size': 10}},
        xaxis={'title_font': {'size': 12}, 'tickfont': {'size': 10}},
        yaxis={'title_font': {'size': 12}, 'tickfont': {'size': 10}},
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    return fig

# Función para fila comparativa
def create_comparison_row(df, metric_pair, title, suffix):
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico Turbo
        fig = px.bar(
            df.groupby(['MONTH', 'MAKER_GROUPED'])[metric_pair[0]].sum().reset_index(),
            x='MONTH', 
            y=metric_pair[0],
            color='MAKER_GROUPED',
            title=f"Turbo - {title}",
            barmode='stack'
        )
        apply_style(fig, f"Turbo - {title}")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico Super/Carulla
        fig = px.bar(
            df.groupby(['MONTH', 'MAKER_GROUPED'])[metric_pair[1]].sum().reset_index(),
            x='MONTH', 
            y=metric_pair[1],
            color='MAKER_GROUPED',
            title=f"{suffix} - {title}",
            barmode='stack'
        )
        apply_style(fig, f"{suffix} - {title}")
        st.plotly_chart(fig, use_container_width=True)

# Función principal de sección
def create_section(df, title, suffix):
    if df.empty:
        st.warning(f"No hay datos disponibles para {title}")
        return
    
    # Aplicar Pareto
    df_processed, pareto_makers = apply_pareto(df)
    
    # Definir métricas a comparar
    METRICS = [
        ('USERS_TURBO', f'USERS_{suffix}', 'Usuarios Únicos'),
        ('ORDERS_TURBO', f'ORDERS_{suffix}', 'Pedidos'),
        ('TOTAL_PRICE_USD_TURBO', f'TOTAL_PRICE_USD_{suffix}', 'Ingresos (USD)'),
        ('SOLD_UNITS_TURBO', f'SOLD_UNITS_{suffix}', 'Unidades Vendidas')
    ]
    
    # Generar filas comparativas
    for turbo_metric, super_metric, metric_title in METRICS:
        st.markdown(f"### {metric_title}")
        create_comparison_row(df_processed, (turbo_metric, super_metric), metric_title, title)
        st.markdown("---")
    
    # Sección análisis adicional
    st.markdown("### Análisis de Performance")
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico NPI
        fig = px.line(
            df_processed[df_processed['MAKER'].isin(pareto_makers)],
            x='MONTH',
            y='NPI',
            color='MAKER',
            title="Evolución del NPI (Top Makers)",
            markers=True
        )
        apply_style(fig, "Evolución del NPI").update_layout(yaxis_range=[0.85,1.15])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter plot NPI vs Basket
        fig = px.scatter(
            df_processed[df_processed['MAKER'].isin(pareto_makers)],
            x='NPI',
            y='BASKET_SIZE_TURBO',
            size='TOTAL_PRICE_USD_TURBO',
            color='MAKER',
            title="Relación NPI vs Basket Size",
            hover_data=['MONTH']
        )
        apply_style(fig, "Relación NPI vs Basket Size").update_layout(xaxis_range=[0.85,1.15])
        st.plotly_chart(fig, use_container_width=True)

# Interfaz principal
selected_category = st.sidebar.selectbox("Seleccionar categoría", list(CATEGORIAS.keys()))
df_super = CATEGORIAS[selected_category]["super"]
df_carulla = CATEGORIAS[selected_category]["carulla"]

st.title(f"Análisis Comparativo: {selected_category}")

# Sección Turbo vs Super
if not df_super.empty:
    st.markdown("## Turbo vs Super")
    create_section(df_super, "Super", "SUPER")

# Sección Turbo vs Carulla
if not df_carulla.empty:
    st.markdown("## Turbo vs Carulla")
    create_section(df_carulla, "Carulla", "CARULLA")