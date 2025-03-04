import pandas as pd
import streamlit as st
import plotly.express as px

# Leer Data
df = pd.read_csv('STREAMLIT/Performance By Categories.csv')

# Obtener todas las categorías únicas en el DataFrame completo
unique_categories = sorted(df['MACRO_CATEGORY'].unique())
num_categories = len(unique_categories)

# Definir la paleta cualitativa de Plotly
base_palette = px.colors.qualitative.Bold

# Si hay más categorías que colores en la paleta, ampliamos la paleta
if num_categories > len(base_palette):
    factor = (num_categories // len(base_palette)) + 1
    extended_palette = base_palette * factor
else:
    extended_palette = base_palette

# Asignar colores de forma consistente y única a cada categoría
color_map = {cat: extended_palette[i] for i, cat in enumerate(unique_categories)}

# Crear slider para seleccionar semana
weeks = df["WEEK"].unique().tolist()
selected_week = st.slider("Selecciona una Semana", min_value=0, max_value=len(weeks)-1, step=1, format='Semana %d')
week_to_display = weeks[selected_week]

# Filtrar DataFrame por semana seleccionada
df_filtered = df[df['WEEK'] == week_to_display]

# Crear el gráfico Sunburst
fig = px.sunburst(
    df_filtered,
    path=["MACRO_CATEGORY", "CATEGORY", "SUB_CATEGORY"],
    values="TOTAL_PRICE_USD",
    color="MACRO_CATEGORY",
    color_discrete_map=color_map,  # Usar el mapeo de colores ampliado
    title=f"Sell Out (USD) by Category Level - Semana {week_to_display}"
)

# Ajustes en el layout
fig.update_layout(margin=dict(t=50, l=20, r=25, b=25))

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)
