import requests
import re
import sys
import time

def get_valid_stream_url():
    """Obtiene la URL del stream ignorando CDN variable"""
    url = "https://librefutboltv.su/tyc-sports/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Referer": "https://envivofy.com/",
        "Origin": "https://envivofy.com"
    }
    
    try:
        # Paso 1: Obtener página principal
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Paso 2: Extraer URL del stream (ignora CDN variable)
        pattern = r'https://cdn\d+\.vivozytv\.com[^"\']+\.m3u8[^\s"]*'
        match = re.search(pattern, response.text)
        
        if not match:
            print("❌ No se encontró URL del stream en la página")
            return False
        
        stream_url = match.group(0)
        print(f"✅ URL del stream encontrada:\n{stream_url}")
        
        # Paso 3: Verificar accesibilidad
        stream_response = requests.get(
            stream_url,
            headers={
                "User-Agent": headers["User-Agent"],
                "Referer": "https://envivofy.com/",
                "Origin": "https://envivofy.com"
            },
            timeout=10
        )
        
        if stream_response.status_code == 200:
            print(f"🎉 ¡Éxito! Stream accesible (HTTP 200)")
            print(f"Tamaño del playlist: {len(stream_response.text)} bytes")
            return True
        else:
            print(f"❌ Error al acceder al stream: HTTP {stream_response.status_code}")
            return False
    
    except Exception as e:
        print(f"🚨 Error crítico: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("TEST DE ACCESO AL STREAM - WINPLUS")
    print(f"Tiempo: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    success = get_valid_stream_url()
    
    print("\n" + "="*50)
    print("RESULTADO FINAL:", "✅ ÉXITO" if success else "❌ FALLO")
    print("="*50)
    
    # Salir con código 0 si funciona, 1 si falla (para Render)
    sys.exit(0 if success else 1)
