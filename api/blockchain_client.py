import requests

BASE = "https://blockstream.info/api"


def get_latest_block():
    url = f"{BASE}/blocks/tip"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()[0]
    except Exception as e:
        print(f"Error fetching latest block: {e}")
        return None


def get_block(block_hash):
    url = f"{BASE}/block/{block_hash}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching block {block_hash}: {e}")
        return None


def get_block_header_hex(block_hash):
    url = f"{BASE}/block/{block_hash}/header"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"Error fetching header for {block_hash}: {e}")
        return None


def get_last_n_blocks(n=50):
    """Return the last N blocks as a list of dicts (height, timestamp, difficulty, nonce, id, bits)."""
    blocks = []
    try:
        response = requests.get(f"{BASE}/blocks/tip", timeout=10)
        response.raise_for_status()
        blocks.extend(response.json())

        while len(blocks) < n:
            next_height = blocks[-1]["height"] - 1
            response = requests.get(f"{BASE}/blocks/{next_height}", timeout=10)
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            blocks.extend(batch)

    except Exception as e:
        print(f"Error fetching last {n} blocks: {e}")

    return [
        {
            "height": b["height"],
            "timestamp": b["timestamp"],
            "difficulty": b.get("difficulty"),
            "nonce": b.get("nonce"),
            "id": b.get("id"),
            "bits": b.get("bits"),
        }
        for b in blocks[:n]
    ]


def get_difficulty_history(n_periods=10):
    """Return the last n_periods difficulty-adjustment data points from blockchain.info.

    Each entry: {"x": unix_timestamp, "y": difficulty}
    """
    url = "https://blockchain.info/charts/difficulty?timespan=all&format=json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        values = response.json().get("values", [])
        return values[-n_periods:] if len(values) >= n_periods else values
    except Exception as e:
        print(f"Error fetching difficulty history: {e}")
        return []


if __name__ == "__main__":
    block = get_latest_block()
    if block:
        print("--- ÚLTIMO BLOQUE ---")
        print(f"Altura:     {block.get('height')}")
        print(f"Hash:       {block.get('id')}")
        print(f"Dificultad: {block.get('difficulty')}")
        print(f"Nonce:      {block.get('nonce')}")
    else:
        print("No se pudieron obtener datos.")
