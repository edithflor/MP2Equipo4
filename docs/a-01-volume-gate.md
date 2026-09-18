# A-01 — Volumen y compuerta F4

El mínimo de entrega es **300 imágenes por clase después de pHash**, con
severidad `fail`. Tener 300 filas en el COCO no demuestra que se cumpla.
El gate cuenta una vez por clase cada componente conectado de imágenes con
distancia pHash ≤ 5. Una imagen con varias cajas de la misma clase cuenta una vez;
un componente con varias clases puede contribuir una vez a cada clase.
Solo se acreditan imágenes legibles con cajas válidas para esa clase.

Si falta alguna imagen o no se puede decodificar, la verificación queda incompleta
y el gate bloquea. No se interpreta la ausencia de archivos como ausencia de duplicados.
El conteo F2-04 previo a pHash sigue disponible, pero no es el mínimo del release.

## Política y ejecución

`quality.yaml` conserva `min_images_per_class.threshold: 300` y `severity: fail`.
Pydantic y Settings impiden reducir este mínimo por debajo de 300 o cambiarlo a
`warn`. Se puede aumentar el umbral. Las otras reglas mantienen su configuración.

Desde la raíz del repositorio, con el entorno Python activado:

```powershell
python -m dataset_quality.gate --coco data/validated/coco.json --images-dir data/images --policy quality.yaml --output data/reports/quality.json
$LASTEXITCODE
```

Cada `file_name` del COCO debe existir bajo `--images-dir`. El comando genera:

- `quality.json`: mantiene los seis checks y añade la auditoría `volume` dentro
  de `min_images_per_class`, con conteo y faltante por clase.
- `volume.md`: tabla para copiar en el issue, SHA256 del COCO, cobertura de archivos,
  presencia de `created_at` y estado del check mínimo. Se puede elegir otra ruta
  con `--volume-report`.

Con `n < umbral`, el mínimo falla y el proceso termina en 1. Con todas las clases
en `n >= umbral` y todos los archivos verificables, pasa ese check; otro check
con severidad `fail` todavía puede bloquear el release.

## Evidencia y trabajo humano pendiente

La [auditoría local](a-01-local-evidence.md) corresponde a una copia de MariaDB y
MinIO del MP1, no acredita que sea el dataset más reciente de todo el equipo.
Los datos descargados están en `data/a01-audit/`, excluido de Git.

Para completar la evidencia del issue:

1. Confirmar qué export del equipo es el vigente y ejecutar el comando con sus imágenes.
2. Pegar `volume.md` en el issue A-01; mientras haya faltantes, mantener explícito
   que el gate está en rojo. No reducir el YAML para conseguir verde.
3. Repartir lotes entre los tres integrantes y anotar en el portal del MP1.
   Conservar las fechas reales `created_at` de las anotaciones y la referencia
   al lote/responsable. No rellenar fechas artificialmente al exportar.
4. Exportar nuevamente y recalcular pHash después de cada lote, hasta cerrar
   el faltante de cada clase. Agregar 50 archivos no garantiza 50 imágenes nuevas
   después de pHash.

Plantilla de seguimiento; completar con el trabajo efectivamente realizado:

| Lote | Responsable | Clase | IDs de imágenes | Anotaciones / created_at | Export | n tras pHash | Faltan |
| --- | --- | --- | --- | --- | --- | ---: | ---: |
| Pendiente | Por asignar | Por confirmar | Pendiente | Pendiente | Pendiente | — | — |

La presencia de `created_at` prueba que hay fechas, no que una persona dibujó las
cajas. Revisar su origen en el portal; las semillas de desarrollo no son evidencia
de anotación humana. Las imágenes aleatorias de los tests son exclusivamente
fixtures y no forman parte del dataset entregable.

## Verificación automatizada

`features/a-01-volume-gate.feature` y `tests/test_a01_volume_gate.py` cubren
300→pass, duplicado→299→fail, archivos ausentes/corruptos, rechazo de mínimo 50
o severidad warn, agrupación transitiva y escritura de reportes con duplicados.
Las pruebas APP-05/F4 usan ahora archivos reales generados en directorios temporales,
para que sus casos positivos también pasen la verificación pHash.

Validación local del cambio: `pytest -o addopts='' -q -rs` terminó con
114 pruebas aprobadas y una omitida (Terraform no instalado en PATH).
`ruff check .`, `ruff format --check .` y `git diff --check` pasaron.
La ejecución sobre el snapshot del MP1 terminó en 1 por volumen insuficiente,
como corresponde; este resultado no equivale a completar la anotación humana.
