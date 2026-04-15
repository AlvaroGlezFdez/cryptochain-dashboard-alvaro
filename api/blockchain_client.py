import requests

# =========================================================
# MILESTONE 2: Primera llamada a la API (Bitcoin)
# Este script recupera datos reales del último bloque.
# Máximo 10 líneas de lógica principal.
# =========================================================

def get_latest_block():
    # Usamos la API de Blockstream sugerida en el PDF
    url = "https://blockstream.info/api/blocks/tip"
    try:
        response = requests.get(url, timeout=10)
        # La API devuelve una lista, tomamos el primer bloque [0]
        data = response.json()[0]
        return data
    except Exception as e:
        print(f"Error conectando a la API: {e}")
        return None

if __name__ == "__main__":
    block = get_latest_block()
    if block:
        print("--- DATOS DEL ÚLTIMO BLOQUE ---")
        print(f"Altura (Height): {block.get('height')}")
        print(f"Hash del Bloque: {block.get('id')}")
        print(f"Dificultad:     {block.get('difficulty')}")
        print(f"Nonce:          {block.get('nonce')}")
        print(f"Transacciones:  {block.get('tx_count')}")
        
        # OBSERVACIONES TEÓRICAS (Milestone 2):
        # 1. El Hash (ID) muestra ceros a la izquierda, indicando que cumple
        #    con el target de dificultad requerido por el Proof of Work.
        # 2. El campo 'bits' codifica el umbral (target) que debe superar el hash.
    else:
        print("No se pudieron obtener datos.")