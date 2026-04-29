import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def _fetch_period_block(period_height):
    """Fetch the block closest to period_height. Returns (period_height, block_dict or None)."""
    try:
        resp = requests.get(f"{BASE}/blocks/{period_height}", timeout=10)
        resp.raise_for_status()
        batch = resp.json()
        return period_height, batch[0] if batch else None
    except Exception as e:
        print(f"Error fetching block at height {period_height}: {e}")
        return period_height, None


def get_difficulty_history(n_periods=10):
    """Return difficulty adjustment data from Blockstream (one entry per 2016-block period).

    Each entry: {"height": int, "timestamp": int, "difficulty": float, "ratio": float}
    ratio = real_period_seconds / (600 * 2016)  — < 1 means faster, > 1 means slower.
    """
    try:
        resp = requests.get(f"{BASE}/blocks/tip", timeout=10)
        resp.raise_for_status()
        current_height = resp.json()[0]["height"]

        last_adj = (current_height // 2016) * 2016
        # Fetch n_periods + 1 blocks (need one extra to compute first ratio)
        targets = [
            last_adj - i * 2016
            for i in range(n_periods + 1)
            if last_adj - i * 2016 >= 0
        ]

        # Parallel fetch with limited concurrency to avoid rate-limiting
        period_blocks = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(_fetch_period_block, h): h for h in targets}
            for future in as_completed(futures):
                h, block = future.result()
                if block is not None:
                    period_blocks[h] = block

        # Sort most-recent first
        sorted_heights = sorted(period_blocks.keys(), reverse=True)
        periods = [period_blocks[h] for h in sorted_heights]

        result = []
        for i in range(len(periods) - 1):
            curr = periods[i]
            prev = periods[i + 1]
            delta_s = curr["timestamp"] - prev["timestamp"]
            ratio = delta_s / (600 * 2016) if delta_s > 0 else 1.0
            result.append({
                "height": curr["height"],
                "timestamp": curr["timestamp"],
                "difficulty": curr.get("difficulty", 0.0),
                "ratio": ratio,
            })

        return result

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
