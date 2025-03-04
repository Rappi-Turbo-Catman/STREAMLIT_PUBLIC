import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================
#  Carga de Datos
# =========================================

def load_data_super():
    """
    Carga el CSV original de Turbo vs Super.
    Asume que las columnas con sufijo _SUPER existen y que la
    métrica principal es TOTAL_PRICE_USD_SUPER.
    """
    #file_path = "./WorkShop Carulla - Alt/New - Workshop - Super.csv"
    url = "https://raw.githubusercontent.com/Rappi-Turbo-Catman/STREAMLIT_PUBLIC/refs/heads/main/WorkShop%20Carulla%20-%20Alt/New%20-%20Workshop%20-%20Super.csv"
    df = pd.read_csv(url)
    df["MONTH"] = pd.to_datetime(df["MONTH"])
    df["YEAR"] = df["MONTH"].dt.year
    return df

def load_data_carulla():
    # file_path = "./WorkShop Carulla - Alt/New - Workshop - Carulla.csv"
    url = "https://raw.githubusercontent.com/Rappi-Turbo-Catman/STREAMLIT_PUBLIC/refs/heads/main/WorkShop%20Carulla%20-%20Alt/New%20-%20Workshop%20-%20Carulla.csv"
    df = pd.read_csv(url)
    df["MONTH"] = pd.to_datetime(df["MONTH"])
    df["YEAR"] = df["MONTH"].dt.year
    
    # Convertir columnas a tipo numérico si alguna viene como objeto
    num_cols_carulla = ["NPI", "AOV_TURBO", "AOV_CARULLA", "BASKET_SIZE_TURBO", "BASKET_SIZE_CARULLA"]
    for col in num_cols_carulla:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

df_super = load_data_super()
df_carulla = load_data_carulla()

# =========================================
#  Configuración de la página
# =========================================
st.set_page_config(page_title="Turbo vs Super/Carulla Dashboard", layout="wide")
st.title("📊 Comparación de Categorías")

# =========================================
#  Tabs: Turbo vs Super | Turbo vs Carulla
# =========================================
tabs = st.tabs(["Turbo vs Super", "Turbo vs Carulla", "Deep Dive Zonas"])

# =========================================
#  Tab 1: Turbo vs Super
# =========================================
with tabs[0]:
    st.header("Turbo vs Super")
    # -----------------------------------------
    #   Filtros de Sidebar
    # -----------------------------------------
    if "selected_metrics_super" not in st.session_state:
        st.session_state.selected_metrics_super = ["ORDERS_TURBO"]
    if "selected_total_price_super" not in st.session_state:
        st.session_state.selected_total_price_super = ["TOTAL_PRICE_USD_TURBO", "TOTAL_PRICE_USD_SUPER"]

    st.sidebar.subheader("Filtros (Turbo vs Super)")
    selected_years_super = st.sidebar.multiselect(
        "Selecciona el año (SUPER)",
        df_super["YEAR"].unique(),
        default=df_super["YEAR"].unique()
    )
    st.session_state.selected_metrics_super = st.sidebar.multiselect(
        "Selecciona métricas para comparar (SUPER)",
        ["ORDERS_TURBO", "ORDERS_SUPER", "USERS_TURBO", "USERS_SUPER", 
         "AOV_TURBO", "AOV_SUPER", "NPI", "BASKET_SIZE_TURBO", "BASKET_SIZE_SUPER"],
        default=st.session_state.selected_metrics_super
    )
    st.session_state.selected_total_price_super = st.sidebar.multiselect(
        "Selecciona el Sell-Out a mostrar (SUPER)",
        ["TOTAL_PRICE_USD_TURBO", "TOTAL_PRICE_USD_SUPER"],
        default=st.session_state.selected_total_price_super
    )

    ## Sidebar categoría
    selected_cats_super = st.sidebar.multiselect(
        'Selecciona la categoría (SUPER)',
        df_super['CAT'].unique(),
        default = df_super['CAT'].unique(),
    )

    # -----------------------------------------
    #   Definir agregaciones (promedio vs suma)
    # -----------------------------------------
    sum_cols_super = [c for c in df_super.columns 
                      if c not in ["MONTH", "YEAR", "ZONA",
                                   "NPI", "AOV_TURBO", "AOV_SUPER",
                                   "BASKET_SIZE_TURBO", "BASKET_SIZE_SUPER"]]
    agg_dict_super = {c: "sum" for c in sum_cols_super}
    mean_cols_super = ["NPI", "AOV_TURBO", "AOV_SUPER", "BASKET_SIZE_TURBO", "BASKET_SIZE_SUPER"]
    for c in mean_cols_super:
        if c in df_super.columns:
            agg_dict_super[c] = "mean"

    # -----------------------------------------
    #   Filtrar y agrupar
    # -----------------------------------------
    df_filtered_super = df_super[df_super["CAT"].isin(selected_cats_super)]
    
    df_filtered_super = df_filtered_super[df_filtered_super["YEAR"].isin(selected_years_super)]
    df_filtered_super = df_filtered_super.groupby("MONTH", as_index=False).agg(agg_dict_super)

    
   


    # -----------------------------------------
    #   Cálculo de variaciones
    # -----------------------------------------
    df_filtered_super.sort_values("MONTH", inplace=True)
    df_filtered_super["VARIACION_TURBO"] = df_filtered_super["TOTAL_PRICE_USD_TURBO"].pct_change(fill_method=None) * 100
    df_filtered_super["VARIACION_SUPER"] = df_filtered_super["TOTAL_PRICE_USD_SUPER"].pct_change(fill_method=None) * 100
    df_filtered_super["VARIACION_TURBO_SMA3"] = df_filtered_super["VARIACION_TURBO"].rolling(3, min_periods=1).mean()
    df_filtered_super["VARIACION_SUPER_SMA3"] = df_filtered_super["VARIACION_SUPER"].rolling(3, min_periods=1).mean()

    # -----------------------------------------
    #   Gráfico de barras de tendencias
    # -----------------------------------------
    fig1 = px.bar(
        df_filtered_super,
        x="MONTH",
        y=st.session_state.selected_total_price_super,
        title="Tendencia de Sell-Out (Turbo vs Super)",
        barmode="group"
    )
    fig1.update_traces(texttemplate='%{y:.2f}', textposition='outside', textfont_size=14)
    st.plotly_chart(fig1, use_container_width=True)

    # -----------------------------------------
    #   Gráfico de variación mensual (Line)
    # -----------------------------------------
    fig2 = px.line(
        df_filtered_super,
        x="MONTH",
        y=["VARIACION_TURBO", "VARIACION_SUPER", "VARIACION_TURBO_SMA3", "VARIACION_SUPER_SMA3"],
        title="Variación Mensual (%) (Turbo vs Super)",
        markers=True
    )
    fig2.update_traces(text=df_filtered_super["VARIACION_TURBO"].round(1), textposition='top center', textfont_size=14)
    fig2.update_traces(text=df_filtered_super["VARIACION_SUPER"].round(1), textposition='top center', textfont_size=14)
    st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------------------
    #   KPI Cards con Delta (Turbo vs Super)
    # -----------------------------------------
    col1, col2 = st.columns(2)
    latest_month_super = df_filtered_super["MONTH"].max()
    prev_month_super = latest_month_super - pd.DateOffset(months=1)

    def calc_delta_super(metric):
        latest_value = df_filtered_super.loc[df_filtered_super["MONTH"] == latest_month_super, metric].sum()
        prev_value = df_filtered_super.loc[df_filtered_super["MONTH"] == prev_month_super, metric].sum()
        return latest_value, latest_value - prev_value

    sell_out_turbo_super, delta_turbo_super = calc_delta_super("TOTAL_PRICE_USD_TURBO")
    sell_out_super_, delta_super_ = calc_delta_super("TOTAL_PRICE_USD_SUPER")
#
    col1.metric("Sell-Out Turbo (USD)",
                f"${sell_out_turbo_super:,.2f}",
                f"Δ ${delta_turbo_super:,.2f}")
    col2.metric("Sell-Out Super (USD)",
                f"${sell_out_super_:,.2f}",
                f"Δ ${delta_super_:,.2f}")

    # -----------------------------------------
    #   Gráfico Combinado (Bar + Line)
    # -----------------------------------------
    fig3 = go.Figure()
    for price in st.session_state.selected_total_price_super:
        fig3.add_trace(go.Bar(x=df_filtered_super["MONTH"], y=df_filtered_super[price], name=price, opacity=0.6))
    for metric in st.session_state.selected_metrics_super:
        fig3.add_trace(go.Scatter(
            x=df_filtered_super["MONTH"],
            y=df_filtered_super[metric],
            name=metric,
            mode='lines+markers',
            yaxis='y2',
            line=dict(width=3),
            text=df_filtered_super[metric].round(2),
            textposition='top center'
        ))
    fig3.update_layout(
        title="Comparacion Sell-Out vs Métricas (Turbo vs Super)",
        barmode='group',
        yaxis=dict(title="Sell-Out", side="left", showgrid=False),
        yaxis2=dict(title="Métricas Seleccionadas", overlaying='y', side='right', showgrid=False, matches=None, anchor='x'),
        hovermode="x unified"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # -----------------------------------------
    #   Heatmap de Correlación
    # -----------------------------------------
    correlation_super = df_filtered_super[[
        "TOTAL_PRICE_USD_TURBO",
        "TOTAL_PRICE_USD_SUPER",
        "AOV_TURBO",
        "AOV_SUPER",
        "BASKET_SIZE_TURBO",
        "BASKET_SIZE_SUPER",
        "NPI"
    ]].corr(numeric_only=True)

    fig4 = px.imshow(
        correlation_super,
        text_auto=True,
        title="Mapa de Calor de Correlación (Turbo vs Super)",
        color_continuous_scale="RdBu_r"
    )
    fig4.update_layout(width=900, height=700)
    st.plotly_chart(fig4, use_container_width=True)


# =========================================
#  Tab 2: Turbo vs Carulla
# =========================================
with tabs[1]:
    st.header("Turbo vs Carulla")
    # -----------------------------------------
    #   Filtros de Sidebar
    # -----------------------------------------
    if "selected_metrics_carulla" not in st.session_state:
        st.session_state.selected_metrics_carulla = ["ORDERS_TURBO"]
    if "selected_total_price_carulla" not in st.session_state:
        st.session_state.selected_total_price_carulla = ["TOTAL_PRICE_USD_TURBO", "TOTAL_PRICE_USD_CARULLA"]

    st.sidebar.subheader("Filtros (Turbo vs Carulla)")
    selected_years_carulla = st.sidebar.multiselect(
        "Selecciona el año (CARULLA)",
        df_carulla["YEAR"].unique(),
        default=df_carulla["YEAR"].unique()
    )
    st.session_state.selected_metrics_carulla = st.sidebar.multiselect(
        "Selecciona métricas para comparar (CARULLA)",
        ["ORDERS_TURBO", "ORDERS_CARULLA", "USERS_TURBO", "USERS_CARULLA",
         "AOV_TURBO", "AOV_CARULLA", "NPI", "BASKET_SIZE_TURBO", "BASKET_SIZE_CARULLA"],
        default=st.session_state.selected_metrics_carulla
    )
    st.session_state.selected_total_price_carulla = st.sidebar.multiselect(
        "Selecciona el Sell-Out a mostrar (CARULLA)",
        ["TOTAL_PRICE_USD_TURBO", "TOTAL_PRICE_USD_CARULLA"],
        default=st.session_state.selected_total_price_carulla
    )

    selected_cats_carulla = st.sidebar.multiselect(
        'Selecciona la categoría (CARULLA)',
        df_carulla['CAT'].unique(),
        default = df_carulla['CAT'].unique(),
    )

    # -----------------------------------------
    #   Definir agregaciones (promedio vs suma)
    # -----------------------------------------
    sum_cols_carulla = [c for c in df_carulla.columns 
                        if c not in ["MONTH", "YEAR", "ZONA",
                                     "NPI", "AOV_TURBO", "AOV_CARULLA",
                                     "BASKET_SIZE_TURBO", "BASKET_SIZE_CARULLA"]]
    agg_dict_carulla = {c: "sum" for c in sum_cols_carulla}
    mean_cols_carulla = ["NPI", "AOV_TURBO", "AOV_CARULLA", "BASKET_SIZE_TURBO", "BASKET_SIZE_CARULLA"]
    for c in mean_cols_carulla:
        if c in df_carulla.columns:
            agg_dict_carulla[c] = "mean"

    # -----------------------------------------
    #   Filtrar y agrupar
    # -----------------------------------------
    df_filtered_carulla = df_carulla[df_carulla["CAT"].isin(selected_cats_carulla)]

    
    df_filtered_carulla = df_filtered_carulla[df_filtered_carulla["YEAR"].isin(selected_years_carulla)]
    df_filtered_carulla = df_filtered_carulla.groupby("MONTH", as_index=False).agg(agg_dict_carulla)

   



    # -----------------------------------------
    #   Cálculo de variaciones
    # -----------------------------------------
    df_filtered_carulla.sort_values("MONTH", inplace=True)
    df_filtered_carulla["VARIACION_TURBO"] = df_filtered_carulla["TOTAL_PRICE_USD_TURBO"].pct_change(fill_method=None) * 100
    df_filtered_carulla["VARIACION_CARULLA"] = df_filtered_carulla["TOTAL_PRICE_USD_CARULLA"].pct_change(fill_method=None) * 100
    df_filtered_carulla["VARIACION_TURBO_SMA3"] = df_filtered_carulla["VARIACION_TURBO"].rolling(3, min_periods=1).mean()
    df_filtered_carulla["VARIACION_CARULLA_SMA3"] = df_filtered_carulla["VARIACION_CARULLA"].rolling(3, min_periods=1).mean()

    # -----------------------------------------
    #   Gráfico de barras de tendencias
    # -----------------------------------------
    fig_carulla_1 = px.bar(
        df_filtered_carulla,
        x="MONTH",
        y=st.session_state.selected_total_price_carulla,
        title="Tendencia de Sell-Out (Turbo vs Carulla)",
        barmode="group"
    )
    fig_carulla_1.update_traces(texttemplate='%{y:.2f}', textposition='outside', textfont_size=14)
    st.plotly_chart(fig_carulla_1, use_container_width=True)

    # -----------------------------------------
    #   Gráfico de variación mensual (Line)
    # -----------------------------------------
    fig_carulla_2 = px.line(
        df_filtered_carulla,
        x="MONTH",
        y=["VARIACION_TURBO", "VARIACION_CARULLA", "VARIACION_TURBO_SMA3", "VARIACION_CARULLA_SMA3"],
        title="Variación Mensual (%) (Turbo vs Carulla)",
        markers=True
    )
    fig_carulla_2.update_traces(text=df_filtered_carulla["VARIACION_TURBO"].round(1), textposition='top center', textfont_size=14)
    fig_carulla_2.update_traces(text=df_filtered_carulla["VARIACION_CARULLA"].round(1), textposition='top center', textfont_size=14)
    st.plotly_chart(fig_carulla_2, use_container_width=True)

    # -----------------------------------------
    #   KPI Cards con Delta (Turbo vs Carulla)
    # -----------------------------------------
    col3, col4 = st.columns(2)
    latest_month_carulla = df_filtered_carulla["MONTH"].max()
    prev_month_carulla = latest_month_carulla - pd.DateOffset(months=1)

    def calc_delta_carulla(metric):
        latest_value = df_filtered_carulla.loc[df_filtered_carulla["MONTH"] == latest_month_carulla, metric].sum()
        prev_value = df_filtered_carulla.loc[df_filtered_carulla["MONTH"] == prev_month_carulla, metric].sum()
        return latest_value, latest_value - prev_value

    sell_out_turbo_carulla, delta_turbo_carulla = calc_delta_carulla("TOTAL_PRICE_USD_TURBO")
    sell_out_carulla, delta_carulla = calc_delta_carulla("TOTAL_PRICE_USD_CARULLA")

    col3.metric("Sell-Out Turbo (USD)",
                f"${sell_out_turbo_carulla:,.2f}",
                f"Δ ${delta_turbo_carulla:,.2f}")
    col4.metric("Sell-Out Carulla (USD)",
                f"${sell_out_carulla:,.2f}",
                f"Δ ${delta_carulla:,.2f}")

    # -----------------------------------------
    #   Gráfico Combinado (Bar + Line)
    # -----------------------------------------
    fig_carulla_3 = go.Figure()
    for price in st.session_state.selected_total_price_carulla:
        fig_carulla_3.add_trace(go.Bar(x=df_filtered_carulla["MONTH"], y=df_filtered_carulla[price], name=price, opacity=0.6))
    for metric in st.session_state.selected_metrics_carulla:
        fig_carulla_3.add_trace(go.Scatter(
            x=df_filtered_carulla["MONTH"],
            y=df_filtered_carulla[metric],
            name=metric,
            mode='lines+markers',
            yaxis='y2',
            line=dict(width=3),
            text=df_filtered_carulla[metric].round(2),
            textposition='top center'
        ))
    fig_carulla_3.update_layout(
        title="Comparacion Sell-Out vs Métricas (Turbo vs Carulla)",
        barmode='group',
        yaxis=dict(title="Sell-Out", side="left", showgrid=False),
        yaxis2=dict(title="Métricas Seleccionadas", overlaying='y', side='right', showgrid=False, matches=None, anchor='x'),
        hovermode="x unified"
    )
    st.plotly_chart(fig_carulla_3, use_container_width=True)

    # -----------------------------------------
    #   Heatmap de Correlación (Turbo vs Carulla)
    # -----------------------------------------
    correlation_carulla = df_filtered_carulla[[
        "TOTAL_PRICE_USD_TURBO",
        "TOTAL_PRICE_USD_CARULLA",
        "AOV_TURBO",
        "AOV_CARULLA",
        "BASKET_SIZE_TURBO",
        "BASKET_SIZE_CARULLA",
        "NPI"
    ]].corr(numeric_only=True)

    fig_carulla_4 = px.imshow(
        correlation_carulla,
        text_auto=True,
        title="Mapa de Calor de Correlación (Turbo vs Carulla)",
        color_continuous_scale="RdBu_r"
    )
    fig_carulla_4.update_layout(width=900, height=700)
    st.plotly_chart(fig_carulla_4, use_container_width=True)

    # TODO: Convert lower part into another tab


with tabs[2]:
    
    # 1. Carga de datos a nivel de zona
    df_zone_monthly = df_super.groupby(["MONTH", "ZONA"], as_index=False)["TOTAL_PRICE_USD_TURBO"].sum()

    # 2. Calcular variacion mensual por zona
    df_zone_monthly.sort_values(["ZONA", "MONTH"], inplace=True)
    df_zone_monthly["VARIACION_ZONA"] = df_zone_monthly.groupby("ZONA")["TOTAL_PRICE_USD_TURBO"].diff().fillna(0)

    # 3. Calcular variacion mensual total
    df_total_zone = df_super.groupby("MONTH", as_index=False)["TOTAL_PRICE_USD_TURBO"].sum()
    df_total_zone.rename(columns={"TOTAL_PRICE_USD_TURBO": "TOTAL_PRICE_TURBO"}, inplace=True)
    df_total_zone["VARIACION_TOTAL"] = df_total_zone["TOTAL_PRICE_TURBO"].diff().fillna(0)

    # 4. Unir dataframes
    df_zone_monthly = df_zone_monthly.merge(df_total_zone, on="MONTH", how="left")

    # 5. Calcular aporte porcentual de cada zona, ajustando signo real
    df_zone_monthly["APORTE_ZONA"] = df_zone_monthly.apply(
        lambda row: (row["VARIACION_ZONA"] / abs(row["VARIACION_TOTAL"])) * 100 if row["VARIACION_TOTAL"] != 0 else 0,
        axis=1
    )

    # 6. Pivot para representacion final
    df_zone_pivot = df_zone_monthly.pivot(index="MONTH", columns="ZONA", values="APORTE_ZONA").reset_index()
    df_zone_pivot.fillna(0, inplace=True)

    # Ajustar formato de fecha para mostrar solo AAAA-MM-DD
    if pd.api.types.is_datetime64_any_dtype(df_zone_pivot["MONTH"]):
        df_zone_pivot["MONTH"] = df_zone_pivot["MONTH"].dt.strftime("%Y-%m-%d")

    # 7. Titulo y grafico
    st.write("### Aporte de cada Zona al Crecimiento/Decrecimiento de TOTAL_PRICE_TURBO")
    fig_contribucion = go.Figure()
    for zona in df_zone_pivot.columns[1:]:
        fig_contribucion.add_trace(go.Bar(
            x=df_zone_pivot["MONTH"],
            y=df_zone_pivot[zona],
            name=zona
        ))

    fig_contribucion.update_layout(
        title="Aporte (%) de cada Zona",
        xaxis_title="Mes",
        yaxis_title="Contribucion (%)",
        barmode='relative'
    )
    st.plotly_chart(fig_contribucion, use_container_width=True)

    # 8. Tabla de datos con Total Price y Variación Total
    #   Unimos df_zone_pivot con df_total_zone, usando MONTH
    df_merge_temp = df_zone_pivot.copy()

    if pd.api.types.is_datetime64_any_dtype(df_total_zone["MONTH"]):
        df_total_zone["MONTH"] = df_total_zone["MONTH"].dt.strftime("%Y-%m-%d")

    df_final = pd.merge(
        df_merge_temp,
        df_total_zone[["MONTH", "TOTAL_PRICE_TURBO", "VARIACION_TOTAL"]],
        on="MONTH",
        how="left"
    )

    st.write("#### Tabla de Aportes por Zona (con Total Turbo y Variacion Total)")
    st.dataframe(df_final)