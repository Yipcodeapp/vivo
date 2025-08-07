# test_access.py
import requests
import re
import time

def get_valid_stream_url():
    """Obtiene la URL del stream directamente del HTML (sin scraping avanzado)"""
    url = "https://envivofy.com/canal.php?stream=winplus"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Referer": "https://envivofy.com/",
        "Origin": "https://envivofy.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate"
    }
    
    try:
        # Paso 1: Obtener página principal
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Paso 2: Extraer URL del stream usando regex (ignora CDN variable)
        # Busca cualquier dominio que termine en vivozytv.com
        pattern = r'https://cdn\d+\.vivozytv\.com[^"\']+\.m3u8[^\s"]*'
        match = re.search(pattern, response.text)
        
        if not match:
            return "❌ No se encontró URL del stream en la página"
        
        stream_url = match.group(0)
        print(f"✅ URL del stream encontrada:\n{stream_url}")
        
        # Paso 3: Verificar accesibilidad del stream
        print("\n🔍 Verificando accesibilidad del stream...")
        stream_response = requests.get(
            stream_url,
            headers={
                "User-Agent": headers["User-Agent"],
                "Referer": "https://envivofy.com/",
                "Origin": "https://envivofy.com"
            }
        )
        
        if stream_response.status_code == 200:
            print(f"🎉 ¡Éxito! Stream accesible (HTTP 200)")
            print(f"Tamaño del playlist: {len(stream_response.text)} bytes")
            return stream_url
        else:
            return f"❌ Error al acceder al stream: HTTP {stream_response.status_code}"
    
    except Exception as e:
        return f"🚨 Error crítico: {str(e)}"

if __name__ == "__main__":
    print("="*50)
    print("TEST DE ACCESO AL STREAM - WINPLUS")
    print(f"Tiempo: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    result = get_valid_stream_url()
    print("\n" + "="*50)
    print("RESULTADO FINAL:")
    print(result)
    print("="*50)