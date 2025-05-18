import socketio
import requests
import json
import os

# Configuración
BASE_URL = "http://localhost:5000"
PLATE = "ABC124"


def iniciar_tracking():
    url = f"{BASE_URL}/motorcycles/stop/{PLATE}"
    try:
        print(f" Enviando solicitud POST a {url}")
        response = requests.post(url)
        response.raise_for_status()
        print(f" Respuesta del servidor: {response.json()}")
    except requests.RequestException as e:
        print(f" Error al iniciar el tracking: {e}")
        return False
    return True


iniciar_tracking()
