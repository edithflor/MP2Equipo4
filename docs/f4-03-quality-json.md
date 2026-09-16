# F4-03 — Reporte `quality.json`

La compuerta escribe un objeto por cada check definido en `quality.yaml`. Cada
objeto contiene:

- `status`: `pass`, `warn` o `fail`;
- `observed`: valor calculado por F2/F3;
- `threshold`: umbral cargado desde YAML;
- `offending_samples`: IDs o detalles de ofensores, o una lista vacía.

La ruta predeterminada es `data/reports/quality.json`. Se configura con
`QUALITY_REPORT_PATH` en `.env` o con `--output`. El directorio `data/` está
montado en el servicio `app`, por lo que el archivo permanece disponible en el
host después de terminar el contenedor temporal.

## Ejecutar con Docker Compose

```powershell
docker compose build app
docker compose run --rm app python -m dataset_quality.gate --coco data/validated/coco.json --images-dir data/images --policy quality.yaml
Write-Host "exit=$LASTEXITCODE"
```

El directorio de imágenes permite que `duplicate_pairs` use F3-03/pHash con los
archivos reales. También puede configurarse mediante `COCO_IMAGES_PATH`.

Aunque el gate termine con código `1`, primero escribe `quality.json`, de modo
que el reporte conserva la evidencia del fallo y puede ser leído por Overview.

## Verificar

```powershell
docker compose run --rm app pytest tests/test_f4_01_quality_yaml.py tests/test_f4_02_gate_blocks.py tests/test_f4_03_quality_json.py -q
```
