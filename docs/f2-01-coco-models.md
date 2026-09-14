# F2-01 — Contrato COCO de entrada

Entrada pública: `dataset_quality.coco.CocoDataset`. Es un módulo Python puro,
sin conexión a MariaDB, MinIO ni FastAPI. F2-02 se encarga de leer el archivo y
localizar las imágenes. F2-04 calcula el volumen; validar este modelo no acredita A-01.

```python
from pathlib import Path
from pydantic import ValidationError
from dataset_quality.coco import CocoDataset

try:
    dataset = CocoDataset.model_validate_json(Path("annotations_coco.json").read_bytes())
except ValidationError as error:
    for issue in error.errors():
        print(issue["loc"], issue["msg"])
    raise
```

Para un diccionario ya leído: `CocoDataset.model_validate(payload)`.
Para serializar: `dataset.model_dump(mode="json")` o `dataset.model_dump_json()`.

## Reglas y límites

- `images`, `categories` y `annotations` son obligatorios; pueden estar vacíos.
- IDs enteros no negativos, únicos dentro de cada colección. Se acepta cero para
  interoperabilidad COCO; el portal MP1 normalmente genera IDs desde uno.
- Cada anotación referencia una imagen y categoría existentes. Los errores
  incluyen colección, índice y campo, por ejemplo `annotations.0.image_id`.
- Dimensiones de imagen enteras positivas; nombres con contenido.
- `bbox` contiene exactamente cuatro números finitos `[x, y, width, height]`.
  `area` es finita e `iscrowd` solo admite los enteros 0 y 1.
- No se convierten strings ni booleanos a números. Se aceptan enteros en campos
  de coordenadas y área porque el exportador MP1 los produce.
- Se preservan coordenadas negativas, cajas fuera de límites, tamaños cero o
  negativos y áreas inconsistentes para que el futuro analizador los reporte.
  No se corrigen ni descartan silenciosamente. No usar este contrato como gate.
- Metadatos adicionales se conservan. `info`, `licenses`, `date_captured`,
  `supercategory`, `iscrowd` y `segmentation` tienen valores opcionales/default.
- Alcance: COCO detection exportado por MP1 y segmentación por listas de polígonos.
  Las máscaras RLE no forman parte de este contrato.
- `file_name` es metadato, no una ruta segura ni una clave MinIO. F2-02 debe
  resolverlo con el mapeo `image_id → object_key` del portal y comprobar archivos.

## Pruebas

`python -m pytest tests/test_coco.py` cubre compatibilidad de JSON/diccionario,
serialización, errores estructurales y de referencias, IDs repetidos y conservación
de defectos para análisis. La muestra es sintética; no es evidencia de anotación humana.

Referencia: https://docs.pydantic.dev/latest/concepts/validators/
