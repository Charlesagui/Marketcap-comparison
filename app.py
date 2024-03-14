from flask import Flask, request, jsonify, render_template
import requests
import csv

app = Flask(__name__)

API_KEY = 'd3f45586-0973-4309-abe2-bd4bdf44b498'
ARCHIVO_HISTORIAL = 'historial_criptomonedas.csv'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/obtener_datos_criptomoneda/<nombre_cripto>', methods=['GET'])
def obtener_datos_criptomoneda(nombre_cripto):
    print(f"Obteniendo datos para: {nombre_cripto}")
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parametros = {'symbol': nombre_cripto.upper()}
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': API_KEY}
    respuesta = requests.get(url, headers=headers, params=parametros)
    datos = respuesta.json()
    print(f"Respuesta API para {nombre_cripto}: {datos}")
    return jsonify(datos)

@app.route('/api/guardar_resultado', methods=['POST'])
def guardar_resultado():
    data = request.json
    nombre_cripto = data.get('nombre_cripto')
    score = data.get('score')
    print(f"Guardando resultado para {nombre_cripto} con score {score}")
    if not activo_ya_registrado(nombre_cripto):
        guardar_resultado_en_archivo(nombre_cripto, score)
        return jsonify({'mensaje': 'Resultado guardado exitosamente'})
    else:
        return jsonify({'mensaje': 'El activo ya está registrado'})

def activo_ya_registrado(nombre_cripto):
    try:
        with open(ARCHIVO_HISTORIAL, 'r', newline='') as archivo:
            for fila in csv.reader(archivo):
                if nombre_cripto == fila[0]:
                    print(f"{nombre_cripto} ya está registrado")
                    return True
    except FileNotFoundError:
        pass
    return False

def guardar_resultado_en_archivo(nombre_cripto, score):
    with open(ARCHIVO_HISTORIAL, 'a', newline='') as archivo:
        csv.writer(archivo).writerow([nombre_cripto, score])
    print(f"Resultado para {nombre_cripto} guardado exitosamente")

@app.route('/api/calcular_calificacion', methods=['POST'])
def calcular_calificacion_endpoint():
    data = request.json
    print(f"Datos recibidos en calcular_calificacion_endpoint: {data}")

    nombre_cripto = data['nombre_cripto']
    datos_cripto = data['datos_cripto']

    calificacion, score = calcular_calificacion(datos_cripto, nombre_cripto)

    print(f"Calificación calculada para {nombre_cripto}: Calificación = {calificacion}, Score = {score}")
    return jsonify({'calificacion': calificacion, 'score': score})

def calcular_calificacion(datos_cripto, nombre_cripto):
    try:
        if 'data' not in datos_cripto or nombre_cripto not in datos_cripto['data']:
            print(f"No se encontraron datos para la criptomoneda {nombre_cripto}")
            return "Error: No se encontraron datos para la criptomoneda", 0

        datos_moneda = datos_cripto['data'][nombre_cripto]
        circulating_supply = datos_moneda.get('circulating_supply', 0)
        max_supply = datos_moneda.get('max_supply')
        market_cap = datos_moneda['quote']['USD']['market_cap']

        muy_alta = 50000000000
        alta = 10000000000
        media = 1000000000
        baja = 100000000

        if max_supply is not None and max_supply > 0:
            score = round((circulating_supply / max_supply) * 100, 2)
            calificacion = f'Calificación basada en supply: {score}/100'
        elif market_cap:
            # Si max_supply es None o cero, pero tenemos market_cap, calculamos basado en market_cap.
            if market_cap >= muy_alta:
                calificacion = 'Excelente pero sin max supply'
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
        else:
            # Caso en que ni max_supply ni market_cap están disponibles
            return "No se puede calcular calificación sin supply o market cap", 0

        return calificacion, score

    except Exception as e:
        print(f"Error al calcular calificación: {e}")
        # Considera capturar y manejar diferentes tipos de excepciones de manera específica
        return f"Error durante el cálculo de calificación: {str(e)}", 0


@app.route('/api/estimar_precio_potencial', methods=['POST'])
def estimar_precio_potencial():
    data = request.json
    cripto_base = data['cripto_base'].upper()
    cripto_objetivo = data['cripto_objetivo'].upper()

    # Obtener market caps de las criptomonedas
    datos_base = obtener_market_cap(cripto_base)
    datos_objetivo = obtener_market_cap(cripto_objetivo)

    if datos_base and datos_objetivo:
        try:
            market_cap_objetivo = datos_objetivo.get('market_cap')
            circulating_supply_base = datos_base.get('circulating_supply')
            if market_cap_objetivo and circulating_supply_base:
                precio_potencial = market_cap_objetivo / circulating_supply_base
                return jsonify({'precio_potencial': precio_potencial})
            else:
                return jsonify({'error': 'Datos faltantes para una de las criptomonedas'}), 400
        except Exception as e:
            return jsonify({'error': f'Error al calcular el precio potencial: {e}'}), 500
    return jsonify({'error': 'Error al obtener datos de las criptomonedas'}), 500


def obtener_market_cap(cripto):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={cripto}"
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': API_KEY}
    respuesta = requests.get(url, headers=headers)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        market_cap = datos['data'][cripto]['quote']['USD']['market_cap']
        circulating_supply = datos['data'][cripto]['circulating_supply']
        return {'market_cap': market_cap, 'circulating_supply': circulating_supply}
    return None

if __name__ == '__main__':
    app.run(debug=True)
