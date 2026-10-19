# generate_script.py
"""Script generator using OpenRouter cascade with emergency fallback.
Generates powerful, viral prayer scripts for YouTube Shorts AND long videos.
Channel: Oraciones que transforman.
"""
import json
import os
import random
import logging

import requests
from retrying import retry

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import (
    OPENROUTER_API_KEY, OPENROUTER_MODELS, MODEL_TIMEOUT,
    SHORT_MAX_WORDS, LONG_MIN_SEGMENTS, LONG_MAX_SEGMENTS, LONG_WORDS_PER_SEGMENT,
)

logging.basicConfig(level=logging.INFO)

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Emergency SHORT scripts (12 unique prayers) ────────────────────────
EMERGENCY_SHORTS = [
    "Señor, hoy pongo mi vida en tus manos. "
    "Sé que tienes un plan perfecto para mí. "
    "Abre puertas que nadie puede cerrar. "
    "Cubre a mi familia con tu manto de protección. "
    "Comenta AMÉN si recibes esta bendición.",

    "Padre celestial, rompe toda cadena que me ata. "
    "Libérame de la ansiedad, del miedo y de la duda. "
    "Llena mi corazón de tu paz que sobrepasa todo entendimiento. "
    "Suscríbete y comenta AMÉN.",

    "Dios todopoderoso, te pido sanación. "
    "Sana mi cuerpo, sana mi mente, sana mi alma. "
    "Donde hay dolor, trae tu consuelo. "
    "Donde hay enfermedad, trae tu poder sanador. "
    "Comenta SALUD si necesitas este milagro.",

    "Señor, abre caminos donde no los hay. "
    "Provee donde falta. Restaura lo que está roto. "
    "Yo confío en que tu tiempo es perfecto. "
    "Lo que parece imposible, tú lo haces posible. "
    "Comenta FE si crees en su poder.",

    "Espíritu Santo, lléname de tu presencia. "
    "Guía mis pasos hoy y siempre. "
    "Dame sabiduría para tomar las decisiones correctas. "
    "Y fortaleza para no rendirme nunca. "
    "Suscríbete y comenta FUERZA.",

    "Padre, te pido por mi familia. "
    "Protege a mis hijos, a mis padres, a los que amo. "
    "Que ningún mal se acerque a nuestro hogar. "
    "Cúbrenos con la sangre de Cristo. "
    "Comenta PROTECCIÓN si clamas por tu familia.",

    "Señor, hoy declaro que soy más que vencedor. "
    "Ninguna arma forjada contra mí prosperará. "
    "Tú peleas mis batallas y yo descanso en tu poder. "
    "Todo lo puedo en Cristo que me fortalece. "
    "Comenta AMÉN y comparte esta declaración.",

    "Dios mío, en este momento de dificultad, "
    "yo sé que tú no me has abandonado. "
    "Tú conviertes las pruebas en testimonios. "
    "Lo que el enemigo planeó para mal, tú lo usas para bien. "
    "Comenta TESTIMONIO si lo crees.",

    "Padre, gracias por este nuevo día. "
    "Gracias por el aire que respiro, por la vida que me das. "
    "Hoy elijo la gratitud sobre la queja. "
    "La fe sobre el miedo. El amor sobre el odio. "
    "Suscríbete y comenta GRATITUD.",

    "Señor Jesús, te entrego mis preocupaciones. "
    "Tú dijiste: no se angustien por nada. "
    "Hoy decido confiar en tu promesa. "
    "Tú cuidas de las aves del cielo, cuánto más de mí. "
    "Comenta PAZ si necesitas su presencia.",

    "Oración de la noche: Señor, antes de dormir, "
    "te doy gracias por todo lo vivido hoy. "
    "Perdona mis errores y renueva mis fuerzas para mañana. "
    "Que tus ángeles guarden mi sueño. "
    "Comenta AMÉN y descansa en su amor.",

    "Padre, hoy oro por los que están solos. "
    "Por los que lloran en silencio. "
    "Por los que sienten que nadie los entiende. "
    "Tú eres el Dios que ve, que escucha y que consuela. "
    "Comenta CONSUELO y comparte con alguien que lo necesite.",
]

# ── Emergency LONG video segments ──────────────────────────────────────
EMERGENCY_LONG_SEGMENTS = [
    {
        "title": "Oración de apertura",
        "text": (
            "Padre celestial, vengo ante tu presencia con un corazón humilde. "
            "Sé que tú conoces cada una de mis necesidades antes de que las pronuncie. "
            "Hoy me presento ante ti con fe, sabiendo que escuchas cada palabra "
            "que sale de mi corazón. Abre mis ojos espirituales para ver tu gloria."
        ),
    },
    {
        "title": "Oración de protección",
        "text": (
            "Señor, cubre a mi familia y a mí con tu manto de protección. "
            "Que ningún arma forjada contra nosotros prospere. "
            "Envía tus ángeles a custodiar nuestro camino. "
            "Que tu sangre preciosa selle cada puerta por donde el enemigo quiera entrar."
        ),
    },
    {
        "title": "Oración de sanación",
        "text": (
            "Dios todopoderoso, tú que sanaste al ciego, al leproso y al paralítico, "
            "hoy te pido sanación para todo aquel que sufre. "
            "Sana cuerpos, mentes y corazones rotos. "
            "Donde la medicina no llega, que llegue tu poder sobrenatural."
        ),
    },
    {
        "title": "Oración de fortaleza",
        "text": (
            "Espíritu Santo, cuando siento que mis fuerzas se agotan, "
            "recuérdame que tu poder se perfecciona en mi debilidad. "
            "Dame la resistencia del águila que renueva sus fuerzas. "
            "Que pueda correr sin cansarme y caminar sin desmayar."
        ),
    },
    {
        "title": "Oración de provisión",
        "text": (
            "Señor, tú eres Jehová Jireh, mi proveedor. "
            "Tú alimentaste a miles con cinco panes y dos peces. "
            "Hoy confío en que proveerás para todas mis necesidades. "
            "Abre las ventanas del cielo y derrama bendición hasta que sobreabunde."
        ),
    },
    {
        "title": "Oración de perdón",
        "text": (
            "Padre, hoy vengo a pedirte perdón por mis faltas. "
            "Lava mi corazón de toda impureza y renueva un espíritu recto dentro de mí. "
            "Ayúdame también a perdonar a quienes me han herido. "
            "Libérame del rencor y llena ese espacio con tu amor."
        ),
    },
    {
        "title": "Oración de agradecimiento",
        "text": (
            "Gracias Señor por cada bendición, las que veo y las que no. "
            "Gracias por la vida, por la salud, por mi familia. "
            "Gracias por las pruebas que me hicieron más fuerte. "
            "Gracias porque aun en la tormenta, tú nunca me soltaste."
        ),
    },
    {
        "title": "Oración de cierre",
        "text": (
            "Señor, sello esta oración con la sangre de Cristo. "
            "Que cada palabra dicha aquí tenga poder en el mundo espiritual. "
            "Confío en que ya estás obrando en mi vida. "
            "En el nombre de Jesús. Amén y amén."
        ),
    },
]


@retry(stop_max_attempt_number=2, wait_exponential_multiplier=500, wait_exponential_max=4000)
def call_model(model, prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
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


def generate_short_script(topic: str) -> str:
    """Generate a SHORT prayer script (max 60 words)."""
    prompt = (
        "Eres un creador VIRAL de YouTube Shorts en español. "
        "Canal: 'Oraciones que transforman'.\n"
        f"Genera una oración CORTA (máximo {SHORT_MAX_WORDS} palabras) sobre:\n"
        f"'{topic}'\n\n"
        "REGLAS:\n"
        "1. HOOK emocional en las primeras 2 líneas que enganche INMEDIATAMENTE.\n"
        "2. Oración íntima, poderosa, que provoque escalofríos.\n"
        "3. CTA final potente: 'Comenta AMÉN', 'Suscríbete', o 'Comparte'.\n"
        "4. SOLO el texto de la oración. Sin títulos, marcas ni emojis.\n"
        "5. Que sea ÚNICA — no uses frases genéricas ni clichés repetidos.\n"
        "6. Incluye un elemento sorprendente o una imagen poderosa.\n"
    )
    return _generate_with_cascade(prompt, EMERGENCY_SHORTS)


def generate_long_script(topic: str) -> list:
    """Generate a LONG prayer script as a list of segments.
    Each segment = {"title": str, "text": str}.
    Returns list of 6-12 segments.
    """
    num_segments = random.randint(LONG_MIN_SEGMENTS, LONG_MAX_SEGMENTS)
    prompt = (
        "Eres un creador de contenido espiritual profundo en español. "
        "Canal: 'Oraciones que transforman'.\n"
        f"Genera una oración LARGA dividida en {num_segments} capítulos sobre:\n"
        f"'{topic}'\n\n"
        "FORMATO de respuesta (JSON array):\n"
        '[{"title": "Nombre del capítulo", "text": "Texto de la oración (~80 palabras)"}]\n\n'
        "REGLAS:\n"
        "1. Cada capítulo tiene un título descriptivo y un texto de ~80 palabras.\n"
        "2. La oración debe tener una progresión emocional (inicio suave → clímax → paz).\n"
        "3. Usa lenguaje poderoso, imágenes vívidas, referencias bíblicas.\n"
        "4. Cada capítulo aborda un aspecto diferente del tema.\n"
        "5. El último capítulo cierra con un AMÉN poderoso y un CTA.\n"
        "6. NO repitas frases entre capítulos.\n"
        "7. Devuelve SOLO el JSON array, sin markdown ni comentarios.\n"
    )

    for model in OPENROUTER_MODELS:
        try:
            logging.info(f"[LONG] Intentando modelo {model}...")
            resp = call_model(model, prompt)
            text = extract_text(resp)
            if text:
                # Try to parse as JSON
                # Clean potential markdown fences
                text = text.strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                segments = json.loads(text)
                if isinstance(segments, list) and len(segments) >= 3:
                    logging.info(f"[LONG] Modelo {model} exitoso — {len(segments)} segmentos.")
                    return segments
        except Exception as e:
            logging.warning(f"[LONG] Modelo {model} falló: {e}")
            continue

    logging.error("[LONG] Todos los modelos fallaron. Usando segmentos de emergencia.")
    # Shuffle and pick a subset of emergency segments
    shuffled = random.sample(EMERGENCY_LONG_SEGMENTS, min(num_segments, len(EMERGENCY_LONG_SEGMENTS)))
    return shuffled


def _generate_with_cascade(prompt: str, emergency_list: list) -> str:
    """Try each model in cascade, fall back to emergency scripts."""
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
    return random.choice(emergency_list)


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "Oración de protección para la familia"
    fmt = sys.argv[2] if len(sys.argv) > 2 else "short"
    if fmt == "long":
        segments = generate_long_script(topic)
        for s in segments:
            print(f"\n--- {s['title']} ---")
            print(s["text"])
    else:
        print(generate_short_script(topic))
