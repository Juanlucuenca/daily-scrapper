import datetime
import traceback
import requests
from typing import List, Optional, Dict
from fastapi import HTTPException
from bs4 import BeautifulSoup
import unidecode

from .fetch_webpage import fetch_webpage

class ScrapingError(Exception):
    """Excepción personalizada para errores de scraping."""
    pass

def get_uva_value() -> Optional[float]:
    """Obtiene el valor actual del UVA."""
    try:
        URL_UVA = "https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/"
        uva_history_price = requests.get(URL_UVA).json()
        uva_of_the_current_day = next(
            (item for item in uva_history_price if item["fecha"] == datetime.datetime.now().strftime("%d-%m-%Y")), None)
        return float(uva_of_the_current_day["valor"]) if uva_of_the_current_day else None
    except Exception as e:
        raise ScrapingError(f"Error obteniendo valor UVA: {str(e)}")

def get_dolar_mep() -> Optional[float]:
    """Obtiene el valor actual del Dólar MEP."""
    try:
        page_content = fetch_webpage("https://www.dolarhoy.com/")
        soup = BeautifulSoup(page_content, 'lxml')
        dolars_list = []

        dollars_html_list = soup.find_all('div', class_='tile is-child', limit=5)
        for dolar_html in dollars_html_list:
            title = dolar_html.find('a', class_='titleText').getText().strip()
            values = dolar_html.find('div', class_='values')
            sell = float(values.find('div', class_='venta').find('div', class_='val').get_text().strip().replace('$', '').replace(',', '.'))
            
            if "mep" in title.lower():
                print(sell)
                return sell
        return None
    except Exception as e:
        raise ScrapingError(f"Error obteniendo Dólar MEP: {str(e)}")

def get_dolar_mayorista() -> Optional[float]:
    """Obtiene el valor actual del Dólar Mayorista."""
    try:
        url = "https://es.investing.com/currencies/usd-ars"
        page_content = fetch_webpage(url)
        soup = BeautifulSoup(page_content, 'lxml')
        
        precio_dolar_mayorista = soup.find('div', {'data-test': 'instrument-price-last'}).getText()
        # Eliminar los puntos de los miles y reemplazar la coma decimal por punto
        precio_limpio = precio_dolar_mayorista.replace('.', '').replace(',', '.')
        print(precio_limpio)
        return float(precio_limpio)
    except Exception as e:
        raise ScrapingError(f"Error obteniendo Dólar Mayorista: {str(e)}")

def get_all_quotes() -> Dict[str, Optional[float]]:
    """Obtiene todas las cotizaciones en una sola función."""
    quotes = {
        'uva': None,
        'dolar_mep': None,
        'dolar_mayorista': None
    }
    
    try:
        quotes['uva'] = get_uva_value()
    except ScrapingError as e:
        print(f"Error al obtener UVA: {e}")

    try:
        quotes['dolar_mep'] = get_dolar_mep()
    except ScrapingError as e:
        print(f"Error al obtener Dólar MEP: {e}")

    try:
        quotes['dolar_mayorista'] = get_dolar_mayorista()
    except ScrapingError as e:
        print(f"Error al obtener Dólar Mayorista: {e}")

    return quotes 