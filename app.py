# main.py
from flask import Flask, Response, redirect, abort, request  
import yt_dlp
import os
import urllib.parse

app = Flask(__name__)

# === CONFIGURACIÓN ===
BASE_URL = "https://www.youtube.com/watch?v="
VPS_BASE_URL = "https://tu-subdominio.onrender.com"  # Render asigna: tu-proyecto.onrender.com

# Ruta base para streams
STREAM_PATH = "/app4"

# Directorio temporal
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


def obtener_hls_url(video_id):
    """Obtiene la URL HLS usando cookies para evitar el bloqueo de 'bot'"""
    url = BASE_URL + video_id

    if not os.path.exists("cookies.txt"):
        print("[!] cookies.txt no encontrado. Requerido para evitar bloqueo.")
        return None

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'noplaylist': True,
        'extract_flat': True,
        'cookiefile': 'cookies.txt',  # ← AQUÍ SE USAN LAS COOKIES
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info.get('is_live') or info.get('live_status') == 'is_live':
                formats = info.get('formats', [])
                for f in formats:
                    murl = f.get('manifest_url')
                    if murl and 'm3u8' in murl:
                        return murl
                # Último recurso
                streaming_url = info.get('url')
                if streaming_url and '.m3u8' in streaming_url:
                    return streaming_url
    except Exception as e:
        print(f"[ERROR] No se pudo obtener HLS para {video_id}: {str(e)}")
        return None
    return None


def leer_canales():
    """Lee el archivo canales.txt"""
    canales = []
    if not os.path.exists("canales.txt"):
        print("[!] canales.txt no encontrado")
        return canales
    with open("canales.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "|" in line:
                nombre, video_id = line.split("|", 1)
                canales.append((nombre.strip(), video_id.strip()))
    return canales


@app.route("/tv.m3u")
def lista_m3u():
    """Genera una lista M3U con la URL base dinámica del servidor"""
    # Detecta automáticamente el esquema (http/https) y dominio
    base_url = request.host_url.rstrip("/")  # Ej: https://tu-app.onrender.com
    stream_base_url = f"{base_url}{STREAM_PATH}"

    canales = leer_canales()
    m3u_lines = ["#EXTM3U"]
    for nombre, video_id in canales:
        safe_nombre = urllib.parse.quote(nombre)
        proxy_url = f"{stream_base_url}/{safe_nombre}.m3u8"
        m3u_lines.append(f"#EXTINF:-1,{nombre}")
        m3u_lines.append(proxy_url)

    return Response("\n".join(m3u_lines), mimetype="application/x-mpegurl")


@app.route(f"{STREAM_PATH}/<path:filename>")
def proxy_stream(filename):
    """Redirige a la URL HLS real de YouTube (actualizada en tiempo real)"""
    if not filename.endswith(".m3u8"):
        abort(404)

    # Extraer nombre del canal (sin .m3u8)
    nombre_canal = os.path.splitext(filename)[0]
    nombre_canal = urllib.parse.unquote(nombre_canal)

    # Buscar el video_id en canales.txt
    canales = leer_canales()
    video_id = None
    for nombre, vid in canales:
        if nombre == nombre_canal:
            video_id = vid
            break

    if not video_id:
        abort(404)

    hls_url = obtener_hls_url(video_id)
    if not hls_url:
        return "Stream no disponible", 500

    # Opción 1: Redirigir directamente
    return redirect(hls_url)

    # Opción 2: (Alternativa) Servir como archivo m3u8 embebido
    # return Response(f"#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2000000\n{hls_url}",
    #                 mimetype="application/x-mpegurl")


@app.route("/")
def home():
    return """
    <h1>YouTube Live Proxy</h1>
    <p>Usa <a href="/tv.m3u">/tv.m3u</a> para obtener la lista.</p>
    <p>Cada enlace actualiza la URL HLS en tiempo real.</p>
    """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
