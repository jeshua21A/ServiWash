"""
Cliente HTTP de la API de Servicios de ServiWash
Este módulo proporciona una clase `ServiciosAPIClient` que permite interactuar con la API de Servicios
"""
import requests
from requests.exceptions import RequestException

SERVICIOS_API_URL = "http://localhost:5002/api/v1/servicios"  # URL base de la API de Servicios

def cotizar_servicio(metrica, datos):
    endpoints = {
        "KILO": "/cotizar/kilo",
        "USO": "/cotizar/uso",
        "PRENDA_Especial": "/cotizar/prenda-especial"
    }

    endpoint = endpoints.get(metrica.upper(), None)

    if not endpoint:
        raise ValueError(f"Métrica desconocida: {metrica}. Métricas válidas: KILO, USO, PRENDA_Especial")

    respuesta = requests.post(f"{SERVICIOS_API_URL}{endpoint}", json=datos) # Realizar la solicitud POST a la API de Servicios

    if not respuesta.ok:
        raise Exception(
            f"Error al cotizar el servicio: {respuesta.status_code} - {respuesta.text}"
        )

    return respuesta.json()  # Devolver la respuesta JSON de la API de Servicios