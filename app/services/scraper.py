import re
import datetime
import traceback
import requests
from time import sleep
from fastapi import HTTPException
from bs4 import BeautifulSoup
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class FinancialScraper:

    @staticmethod
    def parse_price(price_str: str) -> float:
        """
        Convierte un string de precio en float, manejando formatos como:
        - "1.000,00" -> 1000.00
        - "1000,00" -> 1000.00
        - "1000" -> 1000.00
        """
        # Detectar el formato usando expresiones regulares
        if re.search(r'\.\d{3},', price_str):  # Tiene punto como separador de miles y coma decimal
            # Eliminar separadores de miles y ajustar decimal
            clean_price = price_str.replace('.', '').replace(',', '.')
        elif re.search(r',\d{2}$', price_str):  # Solo coma como separador decimal
            clean_price = price_str.replace(',', '.')
        else:
            # Caso sin separador decimal ni de miles (número simple)
            clean_price = price_str

        # Convertir a float
        try:
            return round(float(clean_price), 2)
        except ValueError:
            raise ValueError(f"No se pudo convertir el precio: {price_str}")

    @staticmethod
    def fetch_webpage(url: str) -> str:
        """Obtiene el contenido HTML de una URL con reintentos"""
        backoff_factor = 0.3
        max_retries = 5
        retries = 0

        while retries < max_retries:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                retries += 1
                logger.warning(f"Error fetching {url} (attempt {retries}/{max_retries}): {str(e)}")
                if retries < max_retries:
                    sleep(backoff_factor)
                    backoff_factor *= 2  # Incremento exponencial del tiempo de espera
                else:
                    raise HTTPException(status_code=503, detail=f"Failed to fetch {url} after {max_retries} attempts")

    @staticmethod
    def scrape_uva() -> Dict[str, float]:
        """
        Scrapeando UVA desde la API de ikiwi
        Returns: {'valor': float}
        """
        URL_UVA = "https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/"

        try:
            logger.info("Scraping UVA value...")
            uva_history_price = requests.get(URL_UVA, timeout=10).json()
            uva_of_the_current_day = next(
                (item for item in uva_history_price if item["fecha"] == datetime.datetime.now().strftime("%d-%m-%Y")),
                None
            )

            if uva_of_the_current_day:
                valor = float(uva_of_the_current_day.get('valor', 0))
                logger.info(f"UVA value scraped successfully: {valor}")
                return {'valor': valor}
            else:
                logger.warning("UVA value for current day not found")
                return {'valor': 0.0}

        except Exception as e:
            logger.error(f"Error scraping UVA: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Error parsing UVA info: {e}")

    @staticmethod
    def scrape_dolar_mayorista() -> Dict[str, float]:
        """
        Scrapeando Dólar Mayorista desde investing.com usando ScraperAPI
        Returns: {'valor': float}
        """
        try:
            logger.info("Scraping Dólar Mayorista value...")

            # Configuración para ScraperAPI
            payload = {
                'api_key': '0f7d8d0b3ba5e529319c2b0d531dc156',
                'url': 'https://es.investing.com/currencies/usd-ars'
            }

            # Request a través de ScraperAPI
            response = requests.get('https://api.scraperapi.com/', params=payload, timeout=60)
            response.raise_for_status()

            # Parsear HTML
            soup = BeautifulSoup(response.text, 'lxml')
            precio_dolar_mayorista = soup.find('div', {'data-test': 'instrument-price-last'}).getText()
            precio_formatted = FinancialScraper.parse_price(precio_dolar_mayorista)

            logger.info(f"Dólar Mayorista value scraped successfully: {precio_formatted}")
            return {'valor': precio_formatted}

        except Exception as e:
            logger.error(f"Error scraping Dólar Mayorista: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Error parsing Dólar Mayorista info: {e}")

    @staticmethod
    def scrape_dolar_mep() -> Dict[str, float]:
        """
        Scrapeando Dólar MEP desde dolarhoy.com
        Returns: {'valor': float}
        """
        try:
            logger.info("Scraping Dólar MEP value...")
            page_content = FinancialScraper.fetch_webpage("https://www.dolarhoy.com/")
            soup = BeautifulSoup(page_content, 'lxml')

            # Buscar los dólares en la estructura
            dollars_html_list = soup.find_all('div', class_='tile is-child', limit=10)

            # Filtrar solo los elementos que contienen información de dólar
            dollars_html_list = [d for d in dollars_html_list if d.find('a', class_='titleText')]

            for dolar_html in dollars_html_list:
                title = dolar_html.find('a', class_='titleText').getText().strip()

                # Buscar específicamente "Dólar MEP"
                if "Dólar MEP" in title or "MEP" in title:
                    values = dolar_html.find('div', class_='values')

                    # Intentar obtener precio de venta
                    venta_elem = values.find('div', class_='venta')
                    venta_val = venta_elem.find('div', class_='val') if venta_elem else None

                    if venta_val:
                        valor = float(venta_val.get_text().strip().replace('$', '').replace(',', '.'))
                        logger.info(f"Dólar MEP value scraped successfully: {valor}")
                        return {'valor': valor}

            logger.warning("Dólar MEP not found on page")
            return {'valor': 0.0}

        except Exception as e:
            logger.error(f"Error scraping Dólar MEP: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Error parsing Dólar MEP info: {e}")
