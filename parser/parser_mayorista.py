import csv
import re
from datetime import datetime

# Datos del dólar mayorista
mayorista = """
Fecha	Valor
10/03/2025	1066
11/03/2025	1066.5
12/03/2025	1066.75
13/03/2025	1067
14/03/2025	1068.5
15/03/2025	1068.5
16/03/2025	1068.5
17/03/2025	1068.5
18/03/2025	1069
19/03/2025	1069.75
20/03/2025	1069.5
21/03/2025	1071.5
22/03/2025	1071.5
23/03/2025	1071.5
24/03/2025	1071.5
25/03/2025	1071.75
26/03/2025	1071.75
27/03/2025	1072.5
28/03/2025	1073.5
29/03/2025	1073.5
30/03/2025	1073.5
31/03/2025	1074
01/04/2025	1074.75
02/04/2025	1074.75
03/04/2025	1075
04/04/2025	1076
05/04/2025	1076
06/04/2025	1076
07/04/2025	1076.5
08/04/2025	1076.5
09/04/2025	1077.5
10/04/2025	1077.5
11/04/2025	1078
12/04/2025	1078
13/04/2025	1078
14/04/2025	1198
15/04/2025	1200
16/04/2025	1135
17/04/2025	1135
18/04/2025	1135
19/04/2025	1135
20/04/2025	1135

"""

def parse_mayorista_data():
    """
    Procesa el string mayorista y genera un CSV con el formato requerido.
    Convierte los años de 4 dígitos a 2 dígitos (ej: 2024 -> 24).
    También convierte números con coma a números con punto (ej: 1228,4 -> 1228.4).
    Y maneja números con punto como separador de miles (ej: 1.123,12 -> 1123.12).
    """
    # Eliminar espacios en blanco al inicio y final
    data = mayorista.strip()
    
    # Dividir por líneas
    lines = data.split('\n')
    
    # Eliminar la primera línea (encabezado)
    lines = lines[1:]
    
    # Lista para almacenar los datos procesados
    processed_data = []
    
    # Procesar cada línea
    for line in lines:
        # Ignorar líneas vacías
        if not line.strip():
            continue
            
        # Dividir por tabulador
        parts = line.split('\t')
        
        # Verificar que la línea tenga el formato correcto
        if len(parts) != 2:
            continue
            
        fecha_str, valor_str = parts
        
        # Convertir la fecha de DD/MM/YYYY a DD-MM-YY
        try:
            # Parsear la fecha
            fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
            
            # Formatear la fecha como DD-MM-YY
            fecha_formatted = fecha.strftime('%d-%m-%y')
            
            # Convertir el valor a formato estándar
            # Primero eliminar los puntos de miles
            # valor_str = valor_str.replace('.', '')
            # Luego convertir la coma decimal a punto
            # valor_str = valor_str.replace(',', '.')
            
            # Convertir el valor a float
            valor = float(valor_str)
            
            # Agregar a la lista de datos procesados
            processed_data.append((fecha_formatted, valor))
        except (ValueError, TypeError):
            # Ignorar líneas con formato incorrecto
            continue
    
    # Ordenar por fecha
    processed_data.sort(key=lambda x: datetime.strptime(x[0], '%d-%m-%y'))
    
    # Eliminar duplicados (mantener el último valor para cada fecha)
    unique_data = {}
    for fecha, valor in processed_data:
        unique_data[fecha] = valor
    
    # Convertir a lista de tuplas
    final_data = [(fecha, valor) for fecha, valor in unique_data.items()]
    
    # Ordenar por fecha
    final_data.sort(key=lambda x: datetime.strptime(x[0], '%d-%m-%y'))
    
    return final_data

def save_to_csv(data, filename='mayorista_lo_q_falta.csv'):
    """
    Guarda los datos procesados en un archivo CSV.
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Escribir encabezado
        writer.writerow(['fecha', 'valor'])
        # Escribir datos
        writer.writerows(data)
    
    print(f"Archivo CSV guardado como {filename}")

if __name__ == "__main__":
    # Procesar los datos
    data = parse_mayorista_data()
    
    # Guardar en CSV
    save_to_csv(data)
    
    # Mostrar los primeros 5 registros
    print("\nPrimeros 5 registros del CSV:")
    for fecha, valor in data[:5]:
        print(f"{fecha}, {valor}")