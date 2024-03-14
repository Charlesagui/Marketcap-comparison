from flask import Flask, request, jsonify
import requests
import csv
from os import path

app = Flask(__name__)

API_KEY = 'd3f45586-0973-4309-abe2-bd4bdf44b498'
ARCHIVO_HISTORIAL = 'historial_criptomonedas.csv'

@app.route('/api/obtener_datos_criptomoneda', methods=['GET'])
def obtener_datos_criptomoneda():
    nombre_cripto = request.args.get('nombre_cripto')
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parametros = {'symbol': nombre_cripto}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY
    }
    respuesta = requests.get(url, headers=headers, params=parametros)
    return jsonify(respuesta.json())

@app.route('/api/guardar_calificacion', methods=['POST'])
def guardar_calificacion():
    content = request.json
    nombre_cripto = content['nombre_cripto']
    score = content['score']

    if not activo_ya_registrado(nombre_cripto):
        with open(ARCHIVO_HISTORIAL, 'a', newline='') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([nombre_cripto, score])
            return jsonify({"status": "Guardado"})
    else:
        return jsonify({"status": "Ya registrado"})

def activo_ya_registrado(nombre_cripto):
    if not path.exists(ARCHIVO_HISTORIAL):
        return False
    with open(ARCHIVO_HISTORIAL, 'r', newline='') as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if nombre_cripto in fila:
                return True
    return False

@app.route('/api/calcular_calificacion', methods=['POST'])
def calcular_calificacion_endpoint():
    # Obtener el cuerpo de la solicitud JSON
    content = request.json
    nombre_cripto = content['nombre_cripto']
    datos_moneda = content['datos_cripto']['data'][nombre_cripto]
    
    # Extraer los valores necesarios del contenido
    circulating_supply = datos_moneda.get('circulating_supply', 0)
    max_supply = datos_moneda.get('max_supply', 0)  # Asegurar un valor por defecto
    market_cap = datos_moneda['quote']['USD']['market_cap']
    
    # Rangos de market cap
    muy_alta = 50000000000
    alta = 10000000000
    media = 1000000000
    baja = 100000000
    
    # Lógica para calcular la calificación y el score
    if max_supply:
        score = round((circulating_supply / max_supply) * 100, 2)  # Redondeo para 2 decimales
        calificacion = f'Calificación de {nombre_cripto} basada en supply: {score} / 100'
    else:
        if market_cap >= muy_alta:
            calificacion = '<Excelente pero sin max supply'
            score = 90
        elif market_cap >= alta and market_cap < muy_alta:
            calificacion = 'Muy buena pero sin max supply'
            score = 75
        elif market_cap >= media and market_cap < alta:
            calificacion = 'Buena pero sin max supply'
            score = 50
        elif market_cap >= baja and market_cap < media:
            calificacion = 'Mala y sin max supply'
            score = 25
        else:
            calificacion = 'Muy mala y sin max supply'
            score = 10
    
    # Devolver la respuesta como JSON
    return jsonify({'calificacion': calificacion, 'score': score})


if __name__ == '__main__':
    app.run(debug=True)
