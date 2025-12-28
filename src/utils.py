"""
utils.py
Funciones auxiliares y helpers.
"""

import pandas as pd
from io import BytesIO
from typing import Union


def df_to_csv_bytes(df: pd.DataFrame, encoding: str = "utf-8") -> bytes:
    """
    Convierte un DataFrame a bytes CSV para descarga.
    
    Args:
        df: DataFrame a convertir.
        encoding: Codificación del archivo.
    
    Returns:
        Bytes del CSV.
    """
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding=encoding)
    buffer.seek(0)
    return buffer.getvalue()


def format_number(n: Union[int, float], decimals: int = 0) -> str:
    """
    Formatea un número con separador de miles.
    
    Args:
        n: Número a formatear.
        decimals: Decimales a mostrar.
    
    Returns:
        String formateado (ej: 1.234.567).
    """
    if decimals > 0:
        formatted = f"{n:,.{decimals}f}"
    else:
        formatted = f"{int(n):,}"
    
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Trunca un texto largo añadiendo puntos suspensivos.
    
    Args:
        text: Texto a truncar.
        max_length: Longitud máxima.
    
    Returns:
        Texto truncado.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def generate_conclusions(kpis: dict, df: pd.DataFrame) -> list:
    """
    Genera conclusiones automáticas basadas en los KPIs y datos.
    
    Args:
        kpis: Diccionario con métricas calculadas.
        df: DataFrame con los datos.
    
    Returns:
        Lista de strings con conclusiones.
    """
    conclusions = []
    
    total = kpis.get("total_establecimientos", 0)
    regiones = kpis.get("regiones", 0)
    comunas = kpis.get("comunas", 0)
    pct_publico = kpis.get("pct_publico", 0)
    con_urgencia = kpis.get("con_urgencia", 0)
    
    conclusions.append(
        f"El dataset contiene <strong>{format_number(total)}</strong> establecimientos de salud "
        f"distribuidos en <strong>{regiones}</strong> regiones y <strong>{comunas}</strong> comunas."
    )
    
    if pct_publico > 0:
        if pct_publico > 50:
            conclusions.append(
                f"La mayoría de establecimientos ({pct_publico}%) son de dependencia pública, "
                "lo que refleja la importancia del sistema de salud estatal en Chile."
            )
        else:
            conclusions.append(
                f"Los establecimientos públicos representan el {pct_publico}% del total, "
                "mostrando una significativa presencia del sector privado."
            )
    
    if con_urgencia > 0:
        pct_urgencia = (con_urgencia / total * 100) if total > 0 else 0
        conclusions.append(
            f"Un {pct_urgencia:.1f}% de los establecimientos ({format_number(con_urgencia)}) "
            "cuentan con servicio de urgencia."
        )
    
    if "RegionGlosa" in df.columns:
        top_region = df["RegionGlosa"].value_counts().head(1)
        if not top_region.empty:
            region_name = top_region.index[0]
            region_count = top_region.values[0]
            conclusions.append(
                f"La región con mayor concentración es <strong>{region_name}</strong> "
                f"con {format_number(region_count)} establecimientos."
            )
    
    if "TipoEstablecimientoGlosa" in df.columns:
        top_tipo = df["TipoEstablecimientoGlosa"].value_counts().head(1)
        if not top_tipo.empty:
            tipo_name = top_tipo.index[0]
            conclusions.append(
                f"El tipo de establecimiento más común es <strong>{truncate_text(tipo_name, 40)}</strong>."
            )
    
    return conclusions
