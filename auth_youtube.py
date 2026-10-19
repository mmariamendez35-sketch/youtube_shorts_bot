import json
import sys
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if "code" in qs:
            auth_code = qs["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Autenticacion completada con exito! Ya puedes cerrar esta ventana.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: no se recibio codigo de autorizacion.")

def main():
    global auth_code
    with open("client_secret.json", "r", encoding="utf-8") as f:
        data = json.load(f)["installed"]
    
    client_id = data["client_id"]
    client_secret = data["client_secret"]
    token_uri = data.get("token_uri", "https://oauth2.googleapis.com/token")
    redirect_uri = "http://localhost:8080/"

    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&"
        f"scope={'+'.join(SCOPES)}&prompt=consent&access_type=offline"
    )

    print("AUTH_URL:" + auth_url, flush=True)
    print("READY_HTTP_SERVER", flush=True)

    httpd = HTTPServer(("127.0.0.1", 8080), OAuthHandler)
    while auth_code is None:
        httpd.handle_request()

    print("CODE_RECEIVED, intercambiando por tokens...", flush=True)
    # Intercambiar code por refresh_token directamente via POST
    token_resp = requests.post(
        token_uri,
        data={
            "code": auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    tokens = token_resp.json()
    if "error" in tokens:
        print(f"Error canjeando token: {tokens}", flush=True)
        sys.exit(1)

    token_data = {
        "token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "token_uri": token_uri,
        "client_id": client_id,
        "client_secret": client_secret,
        "scopes": SCOPES,
    }
    Path("youtube_token.json").write_text(json.dumps(token_data, indent=2), encoding="utf-8")
    print("TOKEN_SAVED_SUCCESSFULLY", flush=True)

if __name__ == "__main__":
    main()
