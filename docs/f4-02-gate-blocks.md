# F4-02 — La compuerta bloquea el pipeline

El comando de la compuerta evalúa el COCO contra `quality.yaml` y muestra cada
check. Un estado `fail` se imprime en rojo y hace que el proceso termine con
código `1`. Los checks `warn` se muestran, pero no bloquean las etapas
posteriores.

## Comando

```bash
docker compose run --rm app python -m dataset_quality.gate --coco data/validated/coco.json --images-dir data/images --policy quality.yaml
echo "exit=$?"
```

En PowerShell, usa `$LASTEXITCODE` para ver el código del último proceso:

```powershell
docker compose run --rm app python -m dataset_quality.gate --coco data/validated/coco.json --images-dir data/images --policy quality.yaml
Write-Host "exit=$LASTEXITCODE"
```

Con el COCO final que cumple la política, el valor es `exit=0`. Si se cambia
solamente `min_images_per_class.threshold` a `99999`, el check queda en `FAIL`
y el comando termina con `exit=1`.

La función `continue_after_gate` es el límite de orquestación para las etapas
posteriores: ante un `fail` no llama split, exportación ni promoción a PROD.
F4-02 no implementa esas etapas; sólo garantiza que no pueden ejecutarse tras
un fallo.
