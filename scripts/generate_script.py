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
    SHORT_MIN_WORDS, SHORT_MAX_WORDS,
    LONG_MIN_SEGMENTS, LONG_MAX_SEGMENTS, LONG_WORDS_PER_SEGMENT,
)

logging.basicConfig(level=logging.INFO)

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Emergency SHORT scripts (Extensas para durar entre 42 y 54 segundos a ritmo normal) ──
EMERGENCY_SHORTS = [
    (
        "Padre celestial y misericordioso, en este día vengo a tus pies a entregar todas mis cargas, dudas y preocupaciones. "
        "Sé que las batallas que enfrento a veces parecen imposibles a los ojos humanos, pero en tu santa palabra encuentro mi refugio, "
        "mi roca inconmovible y mi mayor fortaleza. Te pido que extiendas tu mano sanadora sobre mi vida y sobre mi hogar. "
        "Bendice a cada miembro de mi hermosa familia, aleja cualquier sombra de maldad, tristeza o escasez, y renueva nuestras fuerzas hoy. "
        "Abre caminos de luz y esperanza donde las puertas estaban cerradas, derrama abundancia, salud y trabajo digno, y llena mi corazón con tu paz infinita. "
        "En el nombre poderoso de Jesús declaro victoria. Escribe AMÉN en los comentarios con toda tu fe y suscríbete para bendecir tu día."
    ),
    (
        "Señor Jesús, hoy me detengo en silencio para darte gracias por el milagro de respirar y por tu fidelidad inquebrantable. "
        "Tú conoces los suspiros más íntimos de mi alma y las lágrimas que he derramado en soledad. "
        "Por eso hoy decido no temer al mañana, porque sé que tú ya estás allá preparando el terreno para mi bendición. "
        "Rompe toda atadura de miedo, sana toda herida del pasado y levanta mi espíritu con nuevo entusiasmo y propósito. "
        "Derrama tu favor sobre mi trabajo, cuida las entradas y salidas de mis seres amados y que en mi mesa nunca falte el pan de tu provisión. "
        "Declaro que esta semana será de milagros y respuestas celestiales. Deja tu AMÉN con fervor y comparte este mensaje de esperanza."
    ),
    (
        "Espíritu Santo de Dios, fuego consolador y guía divina, desciende con poder en este preciso momento sobre mi vida. "
        "Limpia mi mente de pensamientos de angustia, lléname de serenidad y dame la sabiduría necesaria para tomar las mejores decisiones. "
        "Envía a tus santos ángeles guardianes a acampar alrededor de mi casa, para que ningún peligro, envidia o enfermedad toque a los míos. "
        "Confío plenamente en que tu tiempo es perfecto y que lo que hoy parece una prueba difícil, mañana será mi testimonio más grande de fe. "
        "Recibo con los brazos abiertos la paz, la sanación y la prosperidad que solo provienen de ti. "
        "Comenta AMÉN si crees firmemente en el poder de Dios y suscríbete para recibir tu oración diaria."
    ),
    (
        "San Miguel Arcángel, príncipe de la milicia celestial, defiéndenos en la batalla y sé nuestro amparo contra la maldad y las asechanzas del enemigo. "
        "Con tu espada de luz divina corta todo lazo de desánimo, toda opresión espiritual y todo plan oscuro en contra de mi familia y mi destino. "
        "Padre eterno, sella con la preciosa sangre de Cristo mi hogar, mis proyectos y a cada uno de mis hijos. "
        "Que tu luz resplandezca en medio de las tinieblas y que la paz de Dios que sobrepasa todo entendimiento guarde nuestros corazones hoy y siempre. "
        "Me declaro bendecido, protegido y guiado por la mano del Altísimo en todo momento. "
        "Escribe FUERZA y AMÉN en los comentarios para sellar esta poderosa protección en tu vida."
    ),
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
            "recuéradme que tu poder se perfecciona en mi debilidad. "
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


def generate_short_script(topic: str) -> str:
    """Generate a SHORT prayer script designed to last between 42 and 52 seconds (100-120 words)."""
    prompt = (
        "Eres un creador VIRAL de YouTube Shorts en español del canal 'Oraciones que transforman'.\n"
        f"Genera una oración PODEROSA Y COMPLETA de exactamente entre {SHORT_MIN_WORDS} y {SHORT_MAX_WORDS} palabras sobre:\n"
        f"'{topic}'\n\n"
        "REQUISITOS CRÍTICOS:\n"
        f"1. LONGITUD: Debe contener entre {SHORT_MIN_WORDS} y {SHORT_MAX_WORDS} palabras (NUNCA menos de {SHORT_MIN_WORDS} palabras porque el audio debe durar mínimo 40 segundos).\n"
        "2. ESTRUCTURA:\n"
        "   - Apertura / Hook emocional que atrape en los primeros 3 segundos.\n"
        "   - Cuerpo de la oración con súplicas profundas, fe inquebrantable y bendiciones para el hogar y la salud.\n"
        "   - Cierre con declaración de fe y llamada a la acción: 'Escribe AMÉN en los comentarios si recibes esta bendición y suscríbete'.\n"
        "3. FORMATO: Devuelve ÚNICAMENTE el texto narrado de la oración. Sin títulos, sin asteriscos, sin comillas, sin emojis ni notas explicativas.\n"
    )
    script = _generate_with_cascade(prompt, EMERGENCY_SHORTS)
    words = script.split()
    
    # Validar que cumpla la extension minima
    if len(words) < SHORT_MIN_WORDS:
        logging.warning(f"Script muy corto ({len(words)} palabras). Usando guion de respaldo enriquecido.")
        script = random.choice(EMERGENCY_SHORTS)

    return script


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
    shuffled = random.sample(EMERGENCY_LONG_SEGMENTS, min(num_segments, len(EMERGENCY_LONG_SEGMENTS)))
    return shuffled


def _generate_with_cascade(prompt: str, emergency_list: list) -> str:
    """Try each model in cascade, fall back to emergency scripts."""
    for model in OPENROUTER_MODELS:
        try:
            logging.info(f"Intentando modelo {model}...")
            resp = call_model(model, prompt)
            script = extract_text(resp)
            if script and len(script.split()) >= SHORT_MIN_WORDS:
                logging.info(f"Modelo {model} exitoso con {len(script.split())} palabras.")
                return script
        except Exception as e:
            logging.warning(f"Modelo {model} falló: {e}")
            continue

    logging.error("Modelos insuficientes o muy cortos. Usando guion de emergencia extenso.")
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
        sc = generate_short_script(topic)
        print(f"Total palabras: {len(sc.split())}\n{sc}")
