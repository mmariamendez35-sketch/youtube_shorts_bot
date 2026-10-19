# generate_script.py
"""Script generator using OpenRouter cascade with emergency fallback."""
import json
import os
import random
import logging

import requests
from retrying import retry

# Use relative path for imports when run from project root
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import OPENROUTER_API_KEY, OPENROUTER_MODELS, MODEL_TIMEOUT

logging.basicConfig(level=logging.INFO)

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Emergency scripts (high-retention biblical stories) ─────────────────
EMERGENCY_SCRIPTS = [
    "¿Sabías que David era solo un pastor cuando derrotó a Goliat? "
    "Un niño con una piedra venció a un gigante. "
    "Dios no mira tu tamaño, mira tu fe. "
    "Comenta AMÉN si crees en los milagros.",

    "Job lo perdió TODO. Familia, salud, riqueza. "
    "Pero nunca perdió su fe en Dios. "
    "Y Dios le devolvió el DOBLE de todo lo que tenía. "
    "Suscríbete si necesitas esa bendición.",

    "Jesús multiplicó 5 panes y 2 peces para alimentar a 5000 personas. "
    "Cuando crees que no te alcanza, Dios multiplica. "
    "Comenta AMÉN y comparte con alguien que necesita este milagro.",

    "Abraham esperó 25 AÑOS por la promesa de Dios. "
    "A los 100 años nació su hijo Isaac. "
    "Lo que Dios prometió, lo cumple. No importa cuánto tardes. "
    "Comenta FE si estás esperando tu promesa.",

    "Daniel fue lanzado a un foso lleno de leones hambrientos. "
    "Pero Dios cerró la boca de cada león. "
    "Cuando caminas con Dios, ningún enemigo puede tocarte. "
    "Suscríbete para más historias que fortalecen tu fe.",

    "José fue vendido por sus propios hermanos. "
    "Fue esclavo. Fue prisionero. "
    "Pero Dios lo convirtió en el segundo hombre más poderoso de Egipto. "
    "Lo que el enemigo planeó para mal, Dios lo usó para bien. Comenta AMÉN.",

    "Moisés abrió el Mar Rojo con el poder de Dios. "
    "Miles de personas cruzaron por tierra seca. "
    "Cuando sientes que no hay salida, Dios abre camino donde no lo hay. "
    "Suscríbete y comenta FUERZA.",

    "La viuda tenía solo una vasija de aceite y deudas enormes. "
    "Eliseo le dijo que consiguiera vasijas vacías. "
    "Dios multiplicó el aceite hasta llenar TODAS las vasijas. "
    "Tu escasez es la oportunidad de Dios. Comenta PROVISIÓN.",

    "Pedro caminó sobre el agua hacia Jesús. "
    "Pero cuando miró las olas, comenzó a hundirse. "
    "Jesús lo tomó de la mano y le dijo: hombre de poca fe. "
    "No mires el problema, mira a Dios. Comenta AMÉN.",

    "Lázaro llevaba 4 días muerto. "
    "Todos dijeron que era imposible. "
    "Jesús dijo: ¡Lázaro, sal fuera! Y resucitó. "
    "Para Dios no existe lo imposible. Suscríbete y comenta MILAGRO.",
]


def select_emergency_script():
    """Return a random emergency script when all models fail."""
    return random.choice(EMERGENCY_SCRIPTS)


@retry(stop_max_attempt_number=2, wait_exponential_multiplier=500, wait_exponential_max=4000)
def call_model(model, prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=MODEL_TIMEOUT)
    response.raise_for_status()
    return response.json()


def extract_text(response_json):
    """Extract text from content or reasoning fields."""
    try:
        content = response_json["choices"][0]["message"]["content"]
        if content and content.strip():
            return content.strip()
    except (KeyError, IndexError, TypeError):
        pass
    try:
        reasoning = response_json.get("reasoning", "")
        if reasoning and reasoning.strip():
            return reasoning.strip()
    except (AttributeError, TypeError):
        pass
    return ""


def generate_script(topic):
    """Generate a short script using cascading models with emergency fallback."""
    prompt = (
        "Eres un creador VIRAL de YouTube Shorts en español sobre la Biblia.\n"
        "Necesito un guion CORTO (máximo 50 palabras) sobre este tema bíblico:\n"
        f"'{topic}'\n\n"
        "REGLAS OBLIGATORIAS:\n"
        "1. Empieza con un HOOK impactante (pregunta o dato sorprendente).\n"
        "2. Cuenta la historia con tensión dramática.\n"
        "3. Termina con una moraleja y un CTA: 'Comenta AMÉN' o 'Suscríbete'.\n"
        "4. Devuelve SOLO el texto del guion, sin marcas ni comentarios.\n"
    )

    for model in OPENROUTER_MODELS:
        try:
            logging.info(f"Intentando modelo {model}...")
            resp = call_model(model, prompt)
            script = extract_text(resp)
            if script and len(script) > 20:
                logging.info(f"Modelo {model} exitoso.")
                return script
        except Exception as e:
            logging.warning(f"Modelo {model} falló: {e}")
            continue

    logging.error("Todos los modelos fallaron. Usando guion de emergencia.")
    return select_emergency_script()


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "El milagro del pan y los peces"
    script = generate_script(topic)
    print(script)
