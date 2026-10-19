# 🙏 Oraciones que transforman — Bot Autónomo de YouTube

Bot 100% autónomo que genera y publica **videos cortos (Shorts)** y **videos largos** con oraciones poderosas diarias. Cada video es **visualmente único** para evitar detección de spam.

## ¿Qué hace?

### 📱 Shorts (4 por día)
- Oraciones cortas de ~50 palabras con máximo impacto
- Hook emocional en los primeros 2 segundos
- CTA variado (AMÉN, Suscríbete, Comparte, FE...)
- Duración: 30-58 segundos

### 🎬 Videos Largos (1 por día)
- Oraciones profundas divididas en 6-12 capítulos
- Cada capítulo con título animado y fondo único
- Timestamps automáticos en la descripción
- Duración: 8-15 minutos

## 🛡️ Sistema Anti-Spam
- **Rotación de temas**: 25 temas shorts + 15 temas largos, sin repetir
- **Fingerprinting**: cada guion se hashea para evitar duplicados
- **Estilos visuales rotativos**: 10 paletas de colores diferentes
- **CTAs variados**: 8 frases diferentes que rotan
- **Historial**: registra cada publicación para no repetir

## 🎨 Efectos Visuales
- **Ken Burns**: zoom/pan animado con keyframes únicos
- **Gradientes animados**: fondos con colores que pulsan y cambian
- **Subtítulos estilizados**: 5 estilos diferentes que rotan
- **Títulos de capítulo**: animados con fade in/out (videos largos)
- **Música de fondo**: mezcla suave opcional

## ⏰ Horarios de publicación
| Hora (Colombia) | Tipo | Descripción |
|-----------------|------|-------------|
| 🌅 8:00 AM | Short | Oración de la mañana |
| 🌤️ 10:00 AM | Largo | Oración profunda del día |
| ☀️ 12:00 PM | Short | Oración del mediodía |
| 🌆 5:00 PM | Short | Oración de la tarde |
| 🌙 9:00 PM | Short | Oración de la noche |

## 📁 Estructura del proyecto
```
├── .github/workflows/
│   └── publish_shorts.yml     # Workflow (cron + manual dispatch)
├── assets/                    # Media opcional (se autogenera si falta)
│   ├── music.mp3              # Música de fondo suave
│   └── thumbnail.jpg          # Miniatura personalizada
├── scripts/
│   ├── main.py                # Orquestador (short/long)
│   ├── generate_script.py     # Generador IA de oraciones
│   ├── generate_audio.py      # Texto a voz + subtítulos SRT
│   ├── assemble_video.py      # Video con keyframes y efectos
│   ├── publish_youtube.py     # Publicación en YouTube
│   ├── anti_spam.py           # Control anti-repetición
│   ├── lock.py                # Cooldown entre publicaciones
│   └── __init__.py
├── auth_youtube.py            # Autorización OAuth (ejecutar 1 vez)
├── config.py                  # Configuración del canal
├── requirements.txt           # Dependencias Python
└── README.md
```

## 🔐 Secretos de GitHub necesarios
| Secreto | Descripción |
|---------|------------|
| `OPENROUTER_API_KEY` | Clave de API de OpenRouter (genera guiones con IA) |
| `CLIENT_SECRET_JSON` | Contenido del client_secret.json (OAuth de GCP) |
| `YOUTUBE_TOKEN_JSON` | Token OAuth generado por auth_youtube.py |

## 🚀 Configuración
1. Habilita YouTube Data API v3 en Google Cloud Console.
2. Crea credenciales OAuth (Aplicación de escritorio).
3. Ejecuta `python auth_youtube.py` para autorizar tu canal.
4. Configura los 3 secretos en Settings → Secrets → Actions.
5. Activa el workflow en la pestaña Actions.
6. ¡El bot publicará automáticamente!

---
*Oraciones que transforman — Cada día una oración que toca el corazón* 🙏
