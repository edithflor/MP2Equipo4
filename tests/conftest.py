"""Imágenes sintéticas exclusivas de pruebas; nunca son evidencia de A-01."""

import io
import random
from functools import lru_cache

import pytest
from PIL import Image


@lru_cache(maxsize=1200)
def synthetic_png(seed):
    buffer = io.BytesIO()
    Image.frombytes("RGB", (100, 100), random.Random(seed).randbytes(30000)).save(
        buffer, format="PNG"
    )
    return buffer.getvalue()


@pytest.fixture
def attach_images():
    def attach(coco, directory=None):
        result = {}
        if directory is not None:
            directory.mkdir(parents=True, exist_ok=True)
        for image in coco["images"]:
            image["file_name"] = f"{image['id']}.png"
            data = synthetic_png(image["id"])
            result[str(image["id"])] = data
            if directory is not None:
                (directory / image["file_name"]).write_bytes(data)
        return result

    return attach
