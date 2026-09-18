# Evidencia local A-01 (2026-09-17)

Estado: **gate bloqueado (exit 1)** con la política versionada de 300/fail.
Fuente: snapshot de solo lectura de `image_repo` en `proyecto1-mariadb` y
los objetos del bucket `image-annotations` de `proyecto1-minio`.
Se descargaron 5 imágenes y 8 anotaciones; no se cambiaron los datos del MP1.
Esta copia contiene archivos de semilla y no acredita autoría humana ni que
sea el dataset vigente del equipo. Confirmar el export vigente antes de cerrar A-01.

Comando reproducible sobre la copia local (no incluida en Git):

```powershell
python -m dataset_quality.gate --coco data/a01-audit/coco.json --images-dir data/a01-audit/images --policy quality.yaml --output data/a01-audit/quality.json
```

## A-01 — Volumen después de pHash

Umbral: 300; severidad: fail; distancia pHash <= 5.

| ID | Clase | Crudo | Cajas válidas | n verificado tras pHash | Faltan |
| --- | --- | ---: | ---: | ---: | ---: |
| 2 | car | 1 | 1 | 1 | 299 |
| 3 | dog | 2 | 2 | 2 | 298 |
| 1 | person | 1 | 1 | 1 | 299 |

Archivos no verificables: 0.
Anotaciones con created_at: 8/8.
La presencia de fechas no demuestra autoría humana. Revisar el portal y sus lotes.
Asignar responsable y lote a las imágenes faltantes; no reducir el YAML.

COCO SHA256: 454e38aa2ecca07842123a3bbd1f3f4567fc7e36d42d06e6078e389dd28709b1

Estado del check mínimo: fail.

Pendiente: pegar esta evidencia en el issue, confirmar el export vigente y registrar lotes humanos hasta cerrar los faltantes.
