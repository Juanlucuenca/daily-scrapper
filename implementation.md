
Se requiere generar un sistema, un servicio en faseAPI utilizando Python, el cual, utilizando las funciones de web scraping que ya se desarrollaron, scrape los tres valores necesarios. Los actualiza en un CSV todos los días a las 4 y 10 de la tarde, en horario argentino. Luego, que tenga tres endpoints para poder obtener cada uno de los valores deseados con el mismo formato del CSV en el cual se pueden obtener fecha y valor, y luego 10 años de fecha hacia adelante, moqueados con fecha y valor 1.

Deben tener también un input donde se pueda probar que el sistema está trayendo correctamente los tres valores financieros, es decir, está haciendo el web scraping correctamente.

También quiero que el tema de las fechas esté optimizado, para que sea performante y se realice de una forma que sea escalable, ya que son muchos registros de fechas moqueados luego de los reales.

Desarrolla toda la lógica para leer y escribir los valores en el CSV. En el CSV ya están cargados los valores que te utilizan actualmente.


def convert_to_float(value):
    try:
        if "," in value:
            formatted_value = value.replace(".", "").replace(",", ".")
            return float(formatted_value)
        else:
            return value
    except ValueError:
        return value

import re

def parse_price(price_str):
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

# Fetch web page
from fastapi import HTTPException
import requests
from time import sleep

def fetch_webpage(url):
    backoff_factor = 0.3
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {str(e)}. Retrying...")
            sleep(backoff_factor)
            backoff_factor *= 2  # Incremento exponencial del tiempo de espera




# UVA SCRAPPER FUNCTION

import datetime
import traceback
from fastapi import HTTPException
import requests

URL_UVA = "https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/"

def uva_parsing():
    try:
        uva_history_price = requests.get(URL_UVA).json()
        uva_of_the_current_day = next(
            (item for item in uva_history_price if item["fecha"] == datetime.datetime.now().strftime("%d-%m-%Y")), None)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error parsing uva info: {e}")
    return uva_of_the_current_day


# DOLAR MAYORISTA SCRAPPER FUNCTION

import datetime
from typing import List

from bs4 import BeautifulSoup

from utils.parse_price import parse_price
from models.DolarResponse import DolarResponse
from utils.fetch_webpage import fetch_webpagSe requiere generar un sistema que, utilizando la función ya desarrollada,¿Se requiere generar un sistema?e


def scrapping_investing():
    url = "https://es.investing.com/currencies/usd-ars"
    page_content = fetch_webpage(url)
    soup = BeautifulSoup(page_content, 'lxml')
    dolars_list: List[DolarResponse] = []

    precio_dolar_mayorista = soup.find(
        'div', {'data-test': 'instrument-price-last'}).getText()


    precio_formatted = parse_price(precio_dolar_mayorista)


    DolarMayorista = DolarResponse(
        id='dolar_mayorista_investing',
        name="Dolar Mayorista (investing)",
        buy_price=precio_formatted,
        sell_price=precio_formatted,
    )

    dolars_list.append(DolarMayorista)

    return dolars_list


# DOLAR MEP SCRAPPER
scrapear unicamente el que el titulo sea Dólar MEP

import datetime
import traceback

from typing import List
from fastapi import HTTPException
from bs4 import BeautifulSoup
import unidecode

from utils.fetch_webpage import fetch_webpage
from models.DolarResponse import DolarResponse

def scrapping_dolarhoy() -> List[DolarResponse]:
    try:
        page_content = fetch_webpage("https://www.dolarhoy.com/")
        soup = BeautifulSoup(page_content, 'lxml')
        dolars_list: List[DolarResponse] = []

        # Buscar los dólares en la nueva estructura
        dollars_html_list = soup.find_all('div', class_='tile is-child', limit=5)
        
        # Filtrar solo los elementos que contienen información de dólar (excluyendo el encabezado)
        dollars_html_list = [d for d in dollars_html_list if d.find('a', class_='titleText')]

        for dolar_html in dollars_html_list:
            dolars_list.append(parse_dolar_info(dolar_html)) 
            
        # Buscar el dólar mayorista en la nueva estructura
        dolar_mayorista_html = soup.find('div', class_='title', text=lambda t: t and 'Dólar Mayorista' in t)
        if dolar_mayorista_html:
            dolar_mayorista_html = dolar_mayorista_html.parent
            dolars_list.append(parse_dolar_mayorista(dolar_mayorista_html))

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error parsing dolar info: {e}")
    
    return dolars_list


def parse_dolar_mayorista(dolar_mayorista_html: BeautifulSoup) -> DolarResponse:
    try:
        title = dolar_mayorista_html.find('div', class_='title').getText().strip()
        buy = float(dolar_mayorista_html.find('div', class_='compra').getText().strip().replace('$', '').replace(',', '.'))
        sell = float(dolar_mayorista_html.find('div', class_='venta').getText().strip().replace('$', '').replace(',', '.'))
        dollars_id = unidecode.unidecode((title).lower().replace(" ", "_"))
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error parsing dolar mayorista info: {e}")

    return DolarResponse(
        id=dollars_id,
        name=title,
        buy_price=buy,
        sell_price=sell,
    )


def parse_dolar_info(dolar_html: BeautifulSoup) -> DolarResponse:
    try:
        title = dolar_html.find('a', class_='titleText').getText().strip()
        values = dolar_html.find('div', class_='values')
        
        # Intentar obtener precio de compra
        compra_elem = values.find('div', class_='compra')
        compra_val = compra_elem.find('div', class_='val') if compra_elem else None
        
        # Intentar obtener precio de venta
        venta_elem = values.find('div', class_='venta')
        venta_val = venta_elem.find('div', class_='val') if venta_elem else None
        
        if compra_val:
            buy = float(compra_val.get_text().strip().replace('$', '').replace(',', '.'))
        else:
            buy = 0.0  # o 0.0, dependiendo de los requisitos
        
        if venta_val:
            sell = float(venta_val.get_text().strip().replace('$', '').replace(',', '.'))
        else:
            sell = 0.0  # o 0.0, dependiendo de los requisitos
        
        # Si no hay precio de compra, usar el de venta
        if buy == 0.0 and sell != 0.0:
            buy = sell
            
        dollars_id = unidecode.unidecode(title.lower().replace(" ", "_"))
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error parsing dolar info of {dolar_html}: {e}")

    return DolarResponse(
        id=dollars_id,
        name=title,
        buy_price=buy,
        sell_price=sell,
    )

