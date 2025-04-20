import requests
from typing import Optional
from requests.exceptions import RequestException

def fetch_webpage(url: str, headers: Optional[dict] = None) -> str:
    """
    Obtiene el contenido de una página web de manera segura.
    
    Args:
        url: URL de la página web
        headers: Headers opcionales para la petición
        
    Returns:
        str: Contenido de la página web
        
    Raises:
        RequestException: Si hay un error al obtener la página
    """
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    headers = headers or default_headers
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        raise RequestException(f"Error al obtener la página {url}: {str(e)}") 