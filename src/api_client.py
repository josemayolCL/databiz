"""
api_client.py
Cliente para consumir la API CKAN de datos.gob.cl
"""

import requests
from io import StringIO
from typing import Optional, Dict, Any
import time


BASE_URL = "https://datos.gob.cl"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2


def _make_request(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = MAX_RETRIES
) -> requests.Response:
    """
    Realiza una petición GET con reintentos.
    
    Args:
        url: URL a consultar.
        params: Parámetros de query string.
        timeout: Tiempo máximo de espera.
        retries: Número de reintentos.
    
    Returns:
        Response object.
    
    Raises:
        requests.RequestException: Si todos los reintentos fallan.
    """
    last_exception = None
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            last_exception = e
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
            continue
    
    raise last_exception


def fetch_package_info(package_id: str, base_url: str = BASE_URL) -> Dict[str, Any]:
    """
    Obtiene información de un dataset (package) desde CKAN.
    
    Args:
        package_id: ID del dataset.
        base_url: URL base del portal CKAN.
    
    Returns:
        Diccionario con los metadatos del dataset.
    
    Raises:
        ValueError: Si el paquete no existe o la respuesta es inválida.
        requests.RequestException: Si hay error de red.
    """
    url = f"{base_url}/api/3/action/package_show"
    params = {"id": package_id}
    
    response = _make_request(url, params=params)
    data = response.json()
    
    if not data.get("success"):
        raise ValueError(f"Error al obtener el paquete: {data.get('error', 'Desconocido')}")
    
    return data["result"]


def fetch_resource_csv(
    resource_url: str,
    encoding: str = "utf-8",
    timeout: int = DEFAULT_TIMEOUT
) -> str:
    """
    Descarga el contenido de un recurso CSV.
    
    Args:
        resource_url: URL directa del recurso CSV.
        encoding: Codificación del archivo.
        timeout: Tiempo máximo de espera.
    
    Returns:
        Contenido del CSV como string.
    
    Raises:
        requests.RequestException: Si hay error de red.
    """
    response = _make_request(resource_url, timeout=timeout)
    response.encoding = encoding
    return response.text


def search_packages(
    query: str,
    rows: int = 10,
    base_url: str = BASE_URL
) -> list:
    """
    Busca datasets en el portal CKAN.
    
    Args:
        query: Término de búsqueda.
        rows: Número máximo de resultados.
        base_url: URL base del portal.
    
    Returns:
        Lista de diccionarios con información de cada dataset.
    """
    url = f"{base_url}/api/3/action/package_search"
    params = {"q": query, "rows": rows}
    
    response = _make_request(url, params=params)
    data = response.json()
    
    if not data.get("success"):
        return []
    
    return data["result"]["results"]


def get_csv_resources_from_package(package_info: Dict[str, Any]) -> list:
    """
    Extrae los recursos en formato CSV de un paquete.
    
    Args:
        package_info: Diccionario con info del paquete (de fetch_package_info).
    
    Returns:
        Lista de diccionarios con id, name y url de cada recurso CSV.
    """
    resources = package_info.get("resources", [])
    csv_resources = []
    
    for res in resources:
        fmt = res.get("format", "").lower()
        if "csv" in fmt:
            csv_resources.append({
                "id": res.get("id"),
                "name": res.get("name", "Sin nombre"),
                "url": res.get("url"),
                "description": res.get("description", "")
            })
    
    return csv_resources
