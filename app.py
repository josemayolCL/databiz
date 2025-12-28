"""
app.py
Aplicación Streamlit para visualizar datos de establecimientos de salud de Chile.
Consume datos desde el portal datos.gob.cl (API CKAN).
Tema oscuro profesional.
"""

import streamlit as st
import pandas as pd
from typing import Optional

from src.api_client import (
    fetch_package_info,
    fetch_resource_csv,
    get_csv_resources_from_package
)
from src.processing import (
    load_csv_from_text,
    clean_dataframe,
    validate_required_columns,
    agg_by_region,
    agg_by_tipo_establecimiento,
    agg_by_dependencia,
    filter_by_region,
    filter_by_tipo,
    get_unique_values,
    calculate_kpis
)
from src.viz import (
    plot_bar_regiones,
    plot_donut_tipos,
    plot_bar_dependencia,
    plot_top_comunas
)
from src.utils import df_to_csv_bytes, format_number, generate_conclusions


st.set_page_config(
    page_title="Establecimientos de Salud Chile",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --bg-primary: #0a0a0a;
        --bg-secondary: #111111;
        --bg-tertiary: #171717;
        --bg-elevated: #1f1f1f;
        --border: #262626;
        --border-light: #333333;
        --text-primary: #fafafa;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --accent-violet: #8b5cf6;
        --accent-violet-light: #a78bfa;
        --accent-cyan: #22d3ee;
        --accent-emerald: #34d399;
        --accent-amber: #fbbf24;
        --accent-rose: #fb7185;
        --gradient: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #22d3ee 100%);
    }
    
    .stApp {
        background: var(--bg-primary);
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }
    
    .hero {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient);
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0 0 0.75rem 0;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.6;
        max-width: 700px;
    }
    
    @media (max-width: 768px) {
        .hero {
            padding: 1.5rem;
            border-radius: 12px;
        }
        .hero-title {
            font-size: 1.8rem;
        }
        .hero-subtitle {
            font-size: 0.95rem;
        }
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        padding: 0.4rem 0.8rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-secondary);
        margin-top: 1.25rem;
    }
    
    .hero-badge::before {
        content: '';
        width: 6px;
        height: 6px;
        background: var(--accent-emerald);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .custom-metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .metric-card:hover {
        border-color: var(--accent-violet);
        transform: translateY(-2px);
    }
    
    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 3rem 0 1.5rem 0;
    }
    
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.01em;
        white-space: nowrap;
    }
    
    .section-line {
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, var(--border) 0%, transparent 100%);
    }
    
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }
    
    .sidebar-section {
        font-size: 0.7rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border);
    }
    
    .stButton > button {
        background: var(--gradient);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        font-size: 0.9rem;
        width: 100%;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(52, 211, 153, 0.25);
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 25px rgba(52, 211, 153, 0.35);
        transform: translateY(-2px);
    }
    
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > div > input {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--accent-violet);
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
    }
    
    .stCheckbox > label > span {
        color: var(--text-secondary);
    }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border);
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: var(--bg-secondary);
    }
    
    .conclusion-item {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent-violet);
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
        line-height: 1.7;
        color: var(--text-secondary);
    }
    
    .conclusion-item strong {
        color: var(--text-primary);
    }
    
    .stAlert {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 12px;
        color: var(--text-secondary);
    }
    
    .filter-active {
        display: inline-flex;
        align-items: center;
        background: var(--bg-tertiary);
        border: 1px solid var(--accent-violet);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        color: var(--accent-violet-light);
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    
    .footer {
        text-align: center;
        padding: 4rem 0 2rem;
        color: var(--text-muted);
        font-size: 0.8rem;
        border-top: 1px solid var(--border);
        margin-top: 4rem;
    }
    
    .footer a {
        color: var(--accent-violet-light);
        text-decoration: none;
        transition: color 0.2s;
    }
    
    .footer a:hover {
        color: var(--accent-violet);
    }
    
    .stSpinner > div {
        border-color: var(--accent-violet) transparent transparent transparent;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    @media (max-width: 576px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .section-title {
            font-size: 1.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)


DEFAULT_PACKAGE_ID = "3bf4cf7c-f638-4735-9a01-f65faae4beca"
DEFAULT_RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"
BASE_URL = "https://datos.gob.cl"

REQUIRED_COLUMNS = [
    "RegionGlosa",
    "TipoEstablecimientoGlosa",
    "DependenciaAdministrativa",
    "ComunaGlosa"
]


@st.cache_data(ttl=3600, show_spinner=False)
def load_data(resource_url: str) -> Optional[pd.DataFrame]:
    try:
        csv_text = fetch_resource_csv(resource_url)
        df = load_csv_from_text(csv_text, separator=";")
        df = clean_dataframe(df)
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_package_resources(package_id: str) -> list:
    try:
        package_info = fetch_package_info(package_id, base_url=BASE_URL)
        return get_csv_resources_from_package(package_info)
    except Exception as e:
        return []


def render_sidebar() -> dict:
    with st.sidebar:
        st.markdown('<div class="sidebar-section">Fuente de Datos</div>', unsafe_allow_html=True)
        
        use_custom = st.checkbox("ID personalizado", value=False)
        
        if use_custom:
            custom_id = st.text_input("Resource ID", value=DEFAULT_RESOURCE_ID)
            resource_url = f"{BASE_URL}/dataset/{DEFAULT_PACKAGE_ID}/resource/{custom_id}/download/"
        else:
            resources = get_package_resources(DEFAULT_PACKAGE_ID)
            if resources:
                names = [r["name"] for r in resources]
                idx = st.selectbox("Recurso", range(len(resources)), format_func=lambda x: names[x])
                resource_url = resources[idx]["url"]
            else:
                resource_url = f"{BASE_URL}/dataset/{DEFAULT_PACKAGE_ID}/resource/{DEFAULT_RESOURCE_ID}/download/establecimientos_20251223.csv"
        
        st.markdown("---")
        
        if st.button("Actualizar"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown('<div class="sidebar-section">Filtros</div>', unsafe_allow_html=True)
        
        return {"resource_url": resource_url}


def render_filters(df: pd.DataFrame) -> dict:
    with st.sidebar:
        regiones = ["Todas"] + get_unique_values(df, "RegionGlosa")
        region = st.selectbox("Región", regiones)
        
        tipos = ["Todos"] + get_unique_values(df, "TipoEstablecimientoGlosa")
        tipo = st.selectbox("Tipo", tipos)
        
        deps = ["Todas"] + get_unique_values(df, "DependenciaAdministrativa")
        dep = st.selectbox("Dependencia", deps)
        
        return {"region": region, "tipo": tipo, "dependencia": dep}


def render_hero():
    st.markdown('''
    <div class="hero">
        <h1 class="hero-title">Establecimientos de Salud en Chile</h1>
        <p class="hero-subtitle">
            Dashboard interactivo del registro oficial de salud.
            Proporcionado por datos.gob.cl
        </p>
        <div class="hero-badge">En línea • Actualizado</div>
    </div>
    ''', unsafe_allow_html=True)


def render_kpis(kpis: dict):
    html = f"""
    <div class="custom-metric-container">
        <div class="metric-card">
            <span class="metric-label">Total Establecimientos</span>
            <span class="metric-value">{format_number(kpis["total_establecimientos"])}</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Regiones</span>
            <span class="metric-value">{kpis["regiones"]}</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Comunas</span>
            <span class="metric-value">{kpis["comunas"]}</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Públicos</span>
            <span class="metric-value">{kpis['pct_publico']}%</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_section_header(title: str):
    st.markdown(f'''
    <div class="section-header">
        <h2 class="section-title">{title}</h2>
        <div class="section-line"></div>
    </div>
    ''', unsafe_allow_html=True)


def render_charts(df: pd.DataFrame):
    render_section_header("Análisis Visual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Por Región")
        fig1 = plot_bar_regiones(agg_by_region(df))
        st.pyplot(fig1)
    
    with col2:
        st.markdown("### Por Tipo")
        fig2 = plot_donut_tipos(agg_by_tipo_establecimiento(df))
        st.pyplot(fig2)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### Por Dependencia")
        fig3 = plot_bar_dependencia(agg_by_dependencia(df))
        st.pyplot(fig3)
    
    with col4:
        st.markdown("### Top Comunas")
        fig4 = plot_top_comunas(df)
        st.pyplot(fig4)


def render_data_table(df: pd.DataFrame):
    render_section_header("Explorar Datos")
    
    cols = df.columns.tolist()
    default = ["EstablecimientoGlosa", "RegionGlosa", "ComunaGlosa", "TipoEstablecimientoGlosa", "DependenciaAdministrativa"]
    default = [c for c in default if c in cols]
    
    selected = st.multiselect("Columnas visibles", cols, default=default if default else cols[:5])
    
    st.dataframe(df[selected], use_container_width=True, height=450)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, _ = st.columns([1, 2])
    
    with col1:
        st.download_button(
            "⬇ Descargar CSV",
            df_to_csv_bytes(df),
            "establecimientos_salud.csv",
            "text/csv",
            use_container_width=True
        )


def render_conclusions(kpis: dict, df: pd.DataFrame):
    render_section_header("Conclusiones")
    
    for conclusion in generate_conclusions(kpis, df):
        st.markdown(f'<div class="conclusion-item">{conclusion}</div>', unsafe_allow_html=True)


def render_footer():
    st.markdown('''
    <div class="footer">
        Desarrollado con Python & Streamlit • Datos de datos.gob.cl
    </div>
    ''', unsafe_allow_html=True)


def main():
    render_hero()
    config = render_sidebar()
    
    with st.spinner("Conectando con datos.gob.cl..."):
        df = load_data(config["resource_url"])
    
    if df is None or df.empty:
        st.error("⚠️ No se pudieron cargar los datos. Por favor verifica tu conexión a internet o intenta más tarde.")
        return
    
    is_valid, missing = validate_required_columns(df, REQUIRED_COLUMNS)
    if not is_valid:
        st.warning(f"Faltan columnas requeridas: {', '.join(missing)}")
    
    filters = render_filters(df)
    
    df_f = df.copy()
    df_f = filter_by_region(df_f, filters["region"])
    df_f = filter_by_tipo(df_f, filters["tipo"])
    
    if filters["dependencia"] != "Todas" and "DependenciaAdministrativa" in df_f.columns:
        df_f = df_f[df_f["DependenciaAdministrativa"] == filters["dependencia"]]
    
    if df_f.empty:
        st.warning("No se encontraron registros con los filtros actuales.")
        return
    
    if filters["region"] != "Todas" or filters["tipo"] != "Todos" or filters["dependencia"] != "Todas":
        st.markdown(f'<div class="filter-active">🎯 Filtrado: {len(df_f):,} registros encontrados</div>', unsafe_allow_html=True)
    
    kpis = calculate_kpis(df_f)
    
    render_kpis(kpis)
    render_charts(df_f)
    render_data_table(df_f)
    render_conclusions(kpis, df_f)
    render_footer()


if __name__ == "__main__":
    main()
