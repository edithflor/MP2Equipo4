import io
from itertools import combinations
from typing import Any

import imagehash
from PIL import Image


def analyze_duplicates(images: dict[str, bytes], threshold: int = 5) -> dict[str, Any]:
    """
    Analiza un diccionario de imágenes para encontrar near-duplicates usando pHash.
    Cumple con SPEC-F3-03: Función pura que no abre el almacenamiento externo.
    """
    hashes = {}

    for img_id, img_bytes in images.items():
        try:
            img = Image.open(io.BytesIO(img_bytes))
            hashes[img_id] = imagehash.phash(img)
        except Exception:
            continue

    pairs = []

    for (id1, hash1), (id2, hash2) in combinations(hashes.items(), 2):
        distance = hash1 - hash2

        if distance <= threshold:
            pairs.append({"image1": id1, "image2": id2, "distance": distance})

    return {"pairs": pairs}
