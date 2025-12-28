"""
processing.py
Funciones de limpieza y transformación de datos con pandas.
"""

import pandas as pd
from io import StringIO
from typing import Optional, List, Tuple


def load_csv_from_text(
    csv_text: str,
    separator: str = ";",
    encoding: str = "utf-8"
) -> pd.DataFrame:
    """
    Carga un DataFrame desde texto CSV.
    
    Args:
        csv_text: Contenido del CSV como string.
        separator: Separador de columnas.
        encoding: Codificación (para referencia, el texto ya está decodificado).
    
    Returns:
        DataFrame con los datos.
    """
    return pd.read_csv(StringIO(csv_text), sep=separator, encoding=encoding)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el DataFrame: normaliza columnas, maneja nulos, corrige tipos.
    
    Args:
        df: DataFrame original.
    
    Returns:
        DataFrame limpio.
    """
    df = df.copy()
    
    df.columns = df.columns.str.strip()
    
    text_cols = df.select_dtypes(include=["object"]).columns
    df[text_cols] = df[text_cols].fillna("No informado")
    
    for col in df.columns:
        if "Codigo" in col and df[col].dtype == object:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df


def validate_required_columns(
    df: pd.DataFrame,
    required: List[str]
) -> Tuple[bool, List[str]]:
    """
    Verifica que el DataFrame tenga las columnas requeridas.
    
    Args:
        df: DataFrame a validar.
        required: Lista de nombres de columnas requeridas.
    
    Returns:
        Tupla (es_valido, columnas_faltantes).
    """
    existing = set(df.columns)
    required_set = set(required)
    missing = required_set - existing
    
    return (len(missing) == 0, list(missing))


def agg_by_region(df: pd.DataFrame, region_col: str = "RegionGlosa") -> pd.DataFrame:
    """
    Agrupa y cuenta establecimientos por región.
    
    Args:
        df: DataFrame con los datos.
        region_col: Nombre de la columna de región.
    
    Returns:
        DataFrame con columnas [region, cantidad], ordenado descendente.
    """
    if region_col not in df.columns:
        return pd.DataFrame(columns=["region", "cantidad"])
    
    counts = df.groupby(region_col).size().reset_index(name="cantidad")
    counts.columns = ["region", "cantidad"]
    counts = counts.sort_values("cantidad", ascending=False)
    
    return counts


def agg_by_tipo_establecimiento(
    df: pd.DataFrame,
    tipo_col: str = "TipoEstablecimientoGlosa"
) -> pd.DataFrame:
    """
    Agrupa y cuenta establecimientos por tipo.
    
    Args:
        df: DataFrame con los datos.
        tipo_col: Nombre de la columna de tipo.
    
    Returns:
        DataFrame con columnas [tipo, cantidad], ordenado descendente.
    """
    if tipo_col not in df.columns:
        return pd.DataFrame(columns=["tipo", "cantidad"])
    
    counts = df.groupby(tipo_col).size().reset_index(name="cantidad")
    counts.columns = ["tipo", "cantidad"]
    counts = counts.sort_values("cantidad", ascending=False)
    
    return counts


def agg_by_dependencia(
    df: pd.DataFrame,
    dep_col: str = "DependenciaAdministrativa"
) -> pd.DataFrame:
    """
    Agrupa y cuenta establecimientos por dependencia administrativa.
    
    Args:
        df: DataFrame con los datos.
        dep_col: Nombre de la columna de dependencia.
    
    Returns:
        DataFrame con columnas [dependencia, cantidad].
    """
    if dep_col not in df.columns:
        return pd.DataFrame(columns=["dependencia", "cantidad"])
    
    counts = df.groupby(dep_col).size().reset_index(name="cantidad")
    counts.columns = ["dependencia", "cantidad"]
    counts = counts.sort_values("cantidad", ascending=False)
    
    return counts


def filter_by_region(
    df: pd.DataFrame,
    region: str,
    region_col: str = "RegionGlosa"
) -> pd.DataFrame:
    """
    Filtra el DataFrame por región.
    
    Args:
        df: DataFrame original.
        region: Nombre de la región a filtrar (o "Todas").
        region_col: Nombre de la columna de región.
    
    Returns:
        DataFrame filtrado.
    """
    if region == "Todas" or region_col not in df.columns:
        return df
    
    return df[df[region_col] == region].copy()


def filter_by_tipo(
    df: pd.DataFrame,
    tipo: str,
    tipo_col: str = "TipoEstablecimientoGlosa"
) -> pd.DataFrame:
    """
    Filtra el DataFrame por tipo de establecimiento.
    
    Args:
        df: DataFrame original.
        tipo: Tipo a filtrar (o "Todos").
        tipo_col: Nombre de la columna de tipo.
    
    Returns:
        DataFrame filtrado.
    """
    if tipo == "Todos" or tipo_col not in df.columns:
        return df
    
    return df[df[tipo_col] == tipo].copy()


def get_unique_values(df: pd.DataFrame, column: str) -> List[str]:
    """
    Obtiene valores únicos de una columna.
    
    Args:
        df: DataFrame.
        column: Nombre de la columna.
    
    Returns:
        Lista de valores únicos ordenados.
    """
    if column not in df.columns:
        return []
    
    values = df[column].dropna().unique().tolist()
    return sorted(values)


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calcula KPIs principales del dataset.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Diccionario con métricas clave.
    """
    total = len(df)
    
    regiones = 0
    if "RegionGlosa" in df.columns:
        regiones = df["RegionGlosa"].nunique()
    
    comunas = 0
    if "ComunaGlosa" in df.columns:
        comunas = df["ComunaGlosa"].nunique()
    
    pct_publico = 0.0
    if "DependenciaAdministrativa" in df.columns:
        publicos = df["DependenciaAdministrativa"].str.contains(
            "Público|Servicio de Salud|Municipal", 
            case=False, 
            na=False
        ).sum()
        pct_publico = (publicos / total * 100) if total > 0 else 0.0
    
    con_urgencia = 0
    if "TieneServicioUrgencia" in df.columns:
        con_urgencia = (df["TieneServicioUrgencia"] == "Sí").sum()
    
    return {
        "total_establecimientos": total,
        "regiones": regiones,
        "comunas": comunas,
        "pct_publico": round(pct_publico, 1),
        "con_urgencia": con_urgencia
    }
