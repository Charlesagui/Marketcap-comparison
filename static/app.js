document.addEventListener('DOMContentLoaded', () => {
    // Asegúrate de que el botón exista antes de agregarle el event listener
    const obtenerDatosBtn = document.getElementById('obtenerDatosBtn');
    if (obtenerDatosBtn) {
        obtenerDatosBtn.addEventListener('click', obtenerDatosCriptomonedaHandler);
    } else {
        console.error('El botón obtenerDatosBtn no se encontró.');
    }
    const estimarBtn = document.getElementById('estimarBtn');
    if (estimarBtn) {
        estimarBtn.addEventListener('click', estimarPrecioPotencial);
    } else {
        console.error('El botón estimarBtn no se encontró.');
    }
});


async function obtenerDatosCriptomonedaHandler() {
    const inputNombreCripto = document.getElementById('nombre_cripto');
    const nombreCripto = inputNombreCripto ? inputNombreCripto.value.toUpperCase() : '';
    console.log('Nombre de la criptomoneda solicitada:', nombreCripto);
    if (nombreCripto) {
        const datos = await obtenerDatosCriptomoneda(nombreCripto);
        if (datos && datos.data && datos.data[nombreCripto]) {
            mostrarDatosCriptomoneda(datos, nombreCripto);
            // Llamada a calcular calificación
            calcularCalificacion(nombreCripto, datos);
        } else {
            console.error('No se pudieron obtener los datos de la criptomoneda.');
            document.getElementById('datos_cripto').innerHTML = `<p>No se pudieron obtener los datos de ${nombreCripto}.</p>`;
        }
    }
}

// Obtener referencia al input del nombre de la criptomoneda
const inputNombreCripto = document.getElementById('nombre_cripto');

// Agregar event listener para el evento 'keyup'
inputNombreCripto.addEventListener('keyup', function(event) {
  // Verificar si la tecla presionada es Enter (código de tecla 13)
  if (event.keyCode === 13) {
    // Llamar a la función que obtiene los datos de la criptomoneda
    obtenerDatosCriptomonedaHandler();
  }
});



async function obtenerDatosCriptomoneda(nombreCripto) {
    try {
        const url = `/api/obtener_datos_criptomoneda/${nombreCripto}`;
        const respuesta = await fetch(url);
        if (!respuesta.ok) {
            throw new Error(`HTTP error! status: ${respuesta.status}`);
        }
        return await respuesta.json();
    } catch (error) {
        console.error('Error en fetch:', error);
    }
}


async function guardarResultado(nombreCripto, score) {
    try {
        console.log(`Intentando guardar resultado para: ${nombreCripto} con score: ${score}`);
        const respuesta = await fetch('/api/guardar_resultado', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nombre_cripto: nombreCripto, score }),
        });
        if (!respuesta.ok) {
            throw new Error(`HTTP error! status: ${respuesta.status}`);
        }
        const resultado = await respuesta.json();
        console.log("Mensaje de guardarResultado:", resultado.mensaje);
    } catch (error) {
        console.error('Error en guardarResultado:', error);
    }
}

async function calcularCalificacion(nombreCripto, datosCripto) {
    console.log(`Calculando calificación para: ${nombreCripto}`);
    try {
        const respuesta = await fetch('/api/calcular_calificacion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre_cripto: nombreCripto, datos_cripto: { data: { [nombreCripto]: datosCripto.data[nombreCripto] } } })
        });
        if (respuesta.ok) {
            const { calificacion, score } = await respuesta.json();
            console.log(`Calificación recibida: ${calificacion}, Score: ${score}`);
            document.getElementById('calificacion').innerHTML = `<h3>Calificación: ${calificacion}, Score: ${score}</h3>`;

            // Llamada a guardar resultado
            await guardarResultado(nombreCripto, score);
        } else {
            console.error('Error al recibir calificación:', await respuesta.text());
        }
    } catch (error) {
        console.error('Error al calcular calificación:', error);
    }
}


function formatearNumeroConEscala(numero) {
    const escalas = ['', 'mil', 'millón', 'billón', 'trillón', 'cuatrillón', 'quintillón', 'sextillón', 'septillón', 'octillón', 'nonillón', 'decillón'];
    let escalaNumerica = 0;
    let numeroFormateado = numero;
    let partes = [];

    if (numero < 0.000001) {
        return `$${numero.toExponential(5)}`;
    }

    while (numeroFormateado >= 1000) {
        const parte = Math.floor(numeroFormateado % 1000);
        partes.unshift(parte);
        numeroFormateado = Math.floor(numeroFormateado / 1000);
        escalaNumerica++;
    }

    partes.unshift(numeroFormateado);

    const numeroCompleto = partes.join(',');
    const escala = escalas[escalaNumerica];
    const escalaNombre = escala ? ` (${numeroFormateado} ${escala}${numeroFormateado !== 1 ? 'es' : ''})` : '';

    if (numero >= 0.000001 && numero < 1) {
        return `$${numero.toFixed(8)}`;
    } else {
        return `$${numeroCompleto}${escalaNombre}`;
    }
}




function mostrarDatosCriptomoneda(datos, nombreCripto) {
    const monedaData = datos.data[nombreCripto];
    if (!monedaData) {
    console.error('Datos de la criptomoneda no encontrados en la respuesta de la API');
    return;
    }
    
    const quote = monedaData.quote.USD;
    const divDatosCriptomoneda = document.getElementById('datos_cripto');
    if (!divDatosCriptomoneda) {
        console.error('El elemento para mostrar los datos de la criptomoneda no se encontró.');
        return;
    }
    
    divDatosCriptomoneda.innerHTML = `
        <h3>Datos de ${nombreCripto.toUpperCase()}</h3>
        <p><strong>Precio actual (USD):</strong> ${quote.price}</p>
        <p><strong>Cambio en 24h (%):</strong> ${quote.percent_change_24h.toFixed(2)}%</p>
        <p><strong>Market Cap (USD):</strong> ${formatearNumeroConEscala(quote.market_cap)}</p>
        <p><strong>Volumen 24h (USD):</strong> ${formatearNumeroConEscala(quote.volume_24h)}</p>
        <p><strong>Circulating Supply:</strong> ${formatearNumeroConEscala(monedaData.circulating_supply)}</p>
        <p><strong>Fully Diluted Market Cap (USD):</strong> ${quote.fully_diluted_market_cap ? `${formatearNumeroConEscala(quote.fully_diluted_market_cap)}` : 'N/A'}</p>
    `;
    
    }


async function enviarDatosParaCalificacion(nombreCripto, datosCripto) {
    // Asegúrate de que 'datosCripto' tiene la estructura correcta esperada por tu endpoint
    console.log('Enviando para calificación:', nombreCripto, datosCripto);
    try {
        const respuesta = await fetch('/api/calcular_calificacion', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({nombre_cripto: nombreCripto, datos_cripto: datosCripto})
        });
        const data = await respuesta.json();
        if (respuesta.ok) {
            console.log('Respuesta de calificación:', data);
            document.getElementById('calificacion').innerHTML = `Calificación: ${data.calificacion}, Score: ${data.score}`;
        } else {
            console.error('Respuesta error de calificación:', data);
        }
    } catch (error) {
        console.error('Error en enviar para calificación:', error);
    }
}

 
async function estimarPrecioPotencial() {
    const criptoBase = document.getElementById('cripto_base').value;
    const criptoObjetivo = document.getElementById('cripto_objetivo').value;

    fetch('/api/estimar_precio_potencial', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cripto_base: criptoBase, cripto_objetivo: criptoObjetivo }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.precio_potencial !== undefined) {
                document.getElementById('resultado_comparacion').innerText = `El precio potencial es: ${data.precio_potencial}`;
            } else {
                document.getElementById('resultado_comparacion').innerText = 'Error al calcular el precio potencial.';
            }
        })
        .catch(error => console.error('Error:', error));
}
