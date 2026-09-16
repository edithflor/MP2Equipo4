# APP-05 — Settings persistente

Settings permite editar todos los umbrales y severidades de `quality.yaml`. Al
presionar **Guardar política**, la UI valida los valores con Pydantic y escribe
el archivo montado en disco; no conserva el cambio sólo en el estado de la
interfaz.

## Ejecutar con Docker Compose

```powershell
docker compose up --build ui
```

Abre `http://localhost:8501`. El formulario incluye, como mínimo, **Mínimo de
imágenes por clase**. El valor entregable inicial se mantiene en `300` y con
severidad `fail`.

Después de guardar, la siguiente corrida usa la política nueva:

```powershell
docker compose run --rm app python -m dataset_quality.gate --coco data/validated/coco.json --images-dir data/images --policy quality.yaml
Write-Host "exit=$LASTEXITCODE"
```

Settings no abre MariaDB, S3 ni MinIO. Sólo usa el archivo local de política.

## Verificar

```powershell
docker compose run --rm app pytest tests/test_app_05_settings.py -q
```
