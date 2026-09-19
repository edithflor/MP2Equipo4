# Evidencia local A-01 (2026-09-18)

Estado: **gate superado (exit 0)** con la política versionada de 300/fail.
Fuente: Dataset recolectado y verificado con F4 (Quality Gate M3).

Comando reproducible sobre la copia local:

```bash
python -m dataset_quality.gate --coco data/validated/coco.json --images-dir data/images --policy quality.yaml --output data/reports/quality.json
```


## A-01 — Volumen después de pHash

Umbral: 300; severidad: fail; distancia pHash <= 5.

| ID | Clase | Crudo | Cajas válidas | n verificado tras pHash | Faltan |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | person | 350 | 350 | 320 | 0 |
| 2 | car | 330 | 330 | 305 | 0 |

Estado del check mínimo: PASS min_images_per_class: observed=300, threshold=300, severity=fail.