# auth_youtube.py
"""
Script de autenticación OAuth de YouTube (ejecutar UNA SOLA VEZ).

Instrucciones:
1. Ve a https://console.cloud.google.com/
2. Crea un proyecto nuevo (o usa uno existente).
3. Habilita la "YouTube Data API v3" en APIs & Services > Library.
4. Ve a APIs & Services > Credentials > Create Credentials > OAuth client ID.
5. Tipo de aplicación: "Desktop app".
6. Descarga el archivo JSON y guárdalo como "client_secret.json" en esta carpeta.
7. Ejecuta este script: python auth_youtube.py
8. Se abrirá tu navegador para autorizar la app con tu cuenta de YouTube.
9. El script generará "youtube_token.json" con el refresh_token.
10. Copia el CONTENIDO de ambos archivos como GitHub Secrets:
    - CLIENT_SECRET_JSON  = contenido de client_secret.json
    - YOUTUBE_TOKEN_JSON  = contenido de youtube_token.json
"""
import json
import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_OUTPUT_FILE = "youtube_token.json"


def main():
    if not Path(CLIENT_SECRET_FILE).exists():
        print("=" * 60)
        print("ERROR: No se encontró 'client_secret.json'")
        print()
        print("Sigue estos pasos:")
        print("1. Ve a https://console.cloud.google.com/")
        print("2. Crea un proyecto (o selecciona uno existente).")
        print("3. Habilita 'YouTube Data API v3':")
        print("   APIs & Services > Library > busca 'YouTube Data API v3' > Enable")
        print("4. Crea credenciales OAuth:")
        print("   APIs & Services > Credentials > Create Credentials > OAuth client ID")
        print("   Tipo: 'Desktop app'")
        print("5. Descarga el JSON y guárdalo como 'client_secret.json' aquí.")
        print("6. Ejecuta este script de nuevo.")
        print("=" * 60)
        return

    print("Iniciando flujo de autorización de YouTube...")
    print("Se abrirá tu navegador. Inicia sesión con la cuenta de tu canal.")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

    # Intenta abrir el navegador automáticamente
    try:
        creds = flow.run_local_server(port=8080, prompt="consent")
    except Exception:
        # Si no hay interfaz gráfica, usa el modo consola
        creds = flow.run_console()

    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    }

    Path(TOKEN_OUTPUT_FILE).write_text(json.dumps(token_data, indent=2), encoding="utf-8")

    print()
    print("=" * 60)
    print("¡ÉXITO! Token guardado en:", TOKEN_OUTPUT_FILE)
    print("=" * 60)
    print()
    print("AHORA copia el CONTENIDO de estos archivos como GitHub Secrets:")
    print()
    print(f"  Secret: CLIENT_SECRET_JSON")
    print(f"  Valor:  (contenido de {CLIENT_SECRET_FILE})")
    print()
    print(f"  Secret: YOUTUBE_TOKEN_JSON")
    print(f"  Valor:  (contenido de {TOKEN_OUTPUT_FILE})")
    print()
    print("Enlace directo para crear secrets:")
    print("  https://github.com/mmariamendez35-sketch/youtube_shorts_bot/settings/secrets/actions/new")
    print()
    print("=" * 60)
    print()
    print("Contenido de YOUTUBE_TOKEN_JSON (copia esto):")
    print()
    print(json.dumps(token_data, indent=2))


if __name__ == "__main__":
    main()
