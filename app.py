import streamlit as st
import requests
import csv

# Función para obtener datos de la criptomoneda desde CoinMarketCap
def obtener_datos_criptomoneda(nombre_cripto):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parametros = {'symbol': nombre_cripto}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'd3f45586-0973-4309-abe2-bd4bdf44b498'
    }

    respuesta = requests.get(url, headers=headers, params=parametros)
    datos = respuesta.json()
    return datos
# UI para la comparación del market cap
st.title('Clasificacion en relacion al potencial crecimiento')

def activo_ya_registrado(nombre_cripto):
    try:
        with open('historial_criptomonedas.csv', 'r', newline='') as archivo:
            lector = csv.reader(archivo)
            for fila in lector:
                if nombre_cripto in fila:
                    return True
        return False
    except FileNotFoundError:
        # Si el archivo no existe, no hay datos previos, por lo que retorna False.
        return False


def guardar_resultado_en_archivo(nombre_cripto, score):
    if not activo_ya_registrado(nombre_cripto):
        with open('historial_criptomonedas.csv', 'a', newline='') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([nombre_cripto, score])
    else:
        print(f"El activo {nombre_cripto} ya está registrado.")


def calcular_calificacion(datos_cripto, nombre_cripto):
    datos_moneda = datos_cripto['data'][nombre_cripto]
    circulating_supply = datos_moneda.get('circulating_supply', 0)
    max_supply = datos_moneda.get('max_supply')
    market_cap = datos_moneda['quote']['USD']['market_cap']
    
    # Rangos de market cap adaptados a categorías generales
    muy_alta = 50000000000  # Ejemplo: mayor que 50 mil millones USD
    alta = 10000000000  # Ejemplo: mayor que 10 mil millones USD
    media = 1000000000   # Ejemplo: mayor que 1 mil millones USD
    baja = 100000000    # Ejemplo: mayor que 100 millones USD
    
    if max_supply:
        score = round((circulating_supply / max_supply) * 100)
        calificacion = f'Calificación de {nombre_cripto} basada en supply: {score} / 100'
    else:
        # Operación alternativa basada en market cap
        if market_cap >= muy_alta:
            calificacion = '<Excelente pero sin max supply'
            score = 90  # Alta confianza y adopción en el mercado
        elif market_cap >= alta and market_cap < muy_alta:
            calificacion = 'Muy buena pero sin max supply'
            score = 75  # Buena confianza y adopción en el mercado
        elif market_cap >= media and market_cap < alta:
            calificacion = 'buena pero sin max supply'
            score = 50  # Confianza y adopción moderadas en el mercado
        elif market_cap >= baja and market_cap < media:
            calificacion = 'mala y  sin max supply'
            score = 25  # Confianza y adopción bajas en el mercado
        else:
            calificacion = 'Muy mala y sin max supply'
            score = 10  # Mínima confianza y adopción en el mercado
    
    return calificacion, score

        
#testeo
def accion():
    nombre_cripto = st.session_state.nombre_cripto.upper()
    if nombre_cripto:
        datos_cripto = obtener_datos_criptomoneda(nombre_cripto)
        try:
            calificacion, score = calcular_calificacion(datos_cripto, nombre_cripto)
            st.markdown(f"<h1 style='text-align: center;'>{calificacion}</h1>", unsafe_allow_html=True)
            guardar_resultado_en_archivo(nombre_cripto, score)
            
            # Extraer los datos relevantes de la respuesta de la API después de calcular la calificación
            quote = datos_cripto['data'][nombre_cripto]['quote']['USD']
            precio = quote['price']
            cambio_24h = quote['percent_change_24h']
            market_cap = quote['market_cap']
            volumen_24h = quote['volume_24h']
            circulating_supply = datos_cripto['data'][nombre_cripto].get('circulating_supply', 0)
            fully_diluted_market_cap = quote.get('fully_diluted_market_cap', 'N/A')

            # Mostrar los datos adicionales de la criptomoneda
            st.write(f"**Precio actual (USD):** ${precio:,.2f}")
            st.write(f"**Cambio en 24h (%):** {cambio_24h}%")
            st.write(f"**Market Cap (USD):** ${market_cap:,.2f}")
            st.write(f"**Volumen 24h (USD):** ${volumen_24h:,.2f}")
            st.write(f"**Circulating Supply:** {circulating_supply}")
            st.write(f"**Fully Diluted Market Cap (USD):** ${fully_diluted_market_cap:,.2f}")

        except KeyError as e:
            st.error(f'Error al obtener datos de la criptomoneda: la clave {e} no se encontró.')
        except Exception as e:
            st.error(f'Error al procesar los datos de la criptomoneda: {e}')


# Función para calcular el precio potencial
def calcular_precio_potencial(market_cap_objetivo, circulating_supply_base):
    if circulating_supply_base == 0:
        return 0
    return market_cap_objetivo / circulating_supply_base


nombre_cripto = st.text_input('Introduce el símbolo de la criptomoneda (ejemplo: BTC, ETH):', key='nombre_cripto')
if st.button('Obtener Calificación') or nombre_cripto:
    accion()
  
st.header('Estimación del Market Cap de Una Criptomoneda Respecto a Otra')
cripto_base = st.text_input('Introduce el símbolo de la criptomoneda base (ejemplo: BTC):', key='cripto_base').upper()
cripto_objetivo = st.text_input('Introduce el símbolo de la criptomoneda objetivo (para el Market Cap):', key='cripto_objetivo').upper()

if st.button('Estimar', key='btn_comparar'):
    if cripto_base and cripto_objetivo:
        datos_base = obtener_datos_criptomoneda(cripto_base)
        datos_objetivo = obtener_datos_criptomoneda(cripto_objetivo)
        try:
            market_cap_objetivo = datos_objetivo['data'][cripto_objetivo]['quote']['USD']['market_cap']
            circulating_supply_base = datos_base['data'][cripto_base]['circulating_supply']
            precio_potencial = calcular_precio_potencial(market_cap_objetivo, circulating_supply_base)
            st.write(f"El precio potencial de {cripto_base} si tuviera el market cap de {cripto_objetivo} sería: ${precio_potencial:,.2f} USD")
        except KeyError as e:
            st.error(f'Error al obtener datos: la clave {e} no se encontró.')
        except Exception as e:
            st.error(f'Error al procesar los datos: {e}')

