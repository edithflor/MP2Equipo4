# Proyecto 2 — calidad y versionado de datasets

Repositorio nuevo para convertir el COCO producido por el Proyecto 1 en un dataset validado,
particionado y versionado. El portal anterior se conserva para anotación; no se copió su historial
ni se reescribió su canvas en este repositorio.

## Control 1: arrancar desde cero

Requisitos: Git, Docker Desktop y Docker Compose. No hace falta instalar Python para levantar el
stack; la imagen usa Python 3.12.

```bash
git clone https://github.com/edithflor/MP2Equipo4.git
cd MP2Equipo4
docker compose up --build --wait
```

Verificación:

```bash
docker compose ps
curl http://localhost:8000/health
```

El JSON debe indicar `"ok": true`. También quedan disponibles:

- API y documentación: <http://localhost:8000/docs>
- MariaDB: `localhost:3307`
- MinIO API: <http://localhost:9010>
- Consola MinIO: <http://localhost:9011>

Para apagar sin borrar datos:

```bash
docker compose down
```

Para borrar los volúmenes locales deliberadamente:

```bash
docker compose down --volumes
```

## Configuración

Compose incluye valores locales no sensibles para que el primer arranque sea de un comando. Para
sobrescribirlos, copia `.env.example` a `.env`; `.env` está ignorado por Git. Nunca se deben
versionar credenciales reales, archivos `.tfstate` ni datos descargados.

La configuración de la aplicación se valida con `pydantic-settings` en
`src/dataset_quality/settings.py`.

## Desarrollo local

El proyecto exige Python 3.12. La `.venv` nunca se versiona.

```bash
python3.12 -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install ".[dev]"
ruff check .
ruff format --check .
pytest
python scripts/check_repo_hygiene.py

# Para levantar la interfaz web:
streamlit run src/dataset_quality/ui/app.py
```

La CI ejecuta esos tres controles con Python 3.12 en cada push a `main` y en cada pull request.

El alcance y la evidencia del primer control están detallados en `docs/control-1.md`.

Las imágenes base de Python, MariaDB y MinIO están fijadas por digest. De esa manera el mismo
commit no cambia silenciosamente de infraestructura aunque una etiqueta del registro se actualice.

## Contratos congelados

Los consumidores de UI y MCP pueden trabajar desde ahora contra:

- `examples/quality.json`
- `examples/splits.json`
- `examples/versions.json`

Son ejemplos de contrato, no resultados reales del pipeline ni evidencia del volumen anotado.

## DVC

El repositorio se inicializa con DVC, pero los datos y los remotes se configurarán en el frente de
versionado. La configuración local y las credenciales de remotes nunca se suben a Git.

```bash
dvc status
```

## Carril de anotación (Proyecto 1)

La anotación humana continúa en `../First_Project_MLOps`; este repo consumirá después su exportación
COCO (JSON y las imágenes de MinIO). No se deben crear cajas mediante scripts.

El conteo válido es el número de **imágenes distintas** que contienen al menos una caja de cada
clase, no el número de cajas:

```sql
SELECT c.name, COUNT(DISTINCT a.image_id) AS annotated_images
FROM annotations AS a
JOIN categories AS c ON c.id = a.category_id
GROUP BY c.id, c.name
ORDER BY annotated_images DESC;
```

Metas del plan: 150 imágenes distintas por clase el 11 de septiembre y 300 por clase antes del
release, en al menos dos clases. El conteo definitivo se recalcula después de colapsar duplicados.


## TF-01 — Terraform por capas

Ver [módulos, entornos dev/prod y comandos](terraform/README.md) y
[evidencia de validación](docs/tf-01-validation.md).

## F2-01 — Modelos COCO

Ver el [contrato COCO, escenarios y límites](docs/f2-01-coco-models.md).
F2-01 y TF-01 no acreditan el volumen de anotación A-01.

## F2-02 — Ingesta del COCO validado

La ingesta recibe el JSON COCO exportado desde el Proyecto 1, lo valida usando
`dataset_quality.coco.CocoDataset` y genera un artefacto validado para las
siguientes etapas del pipeline.

El dataset real y las imágenes deben permanecer fuera de Git. El directorio
`data/` está ignorado por `.gitignore`.

Configura las rutas en `.env`:

```env
COCO_INPUT_PATH=data/raw/annotations_coco.json
COCO_VALIDATED_PATH=data/validated/coco.json
```

Ejecuta la ingesta con:

```bash
python -m dataset_quality.ingest
```

Si el coco es válido, el comando termina con código 0 y genera el artefacto
validado, si el coco es inválido termina con código distinto de 0 y muestra
el campo que falló

## APP-02 — Analizadores

La interfaz incluye las cinco pestañas de calidad y consume las salidas reales
de los analizadores F3. Consulta [la guía de APP-02](docs/app-02-analyzers.md)
para conocer las fuentes de datos, correspondencia de pestañas y verificación.

## F4-01 — Política de calidad

Los umbrales y severidades de la compuerta están versionados en `quality.yaml`.
Ver [política y demostración](docs/f4-01-quality-yaml.md).

## F4-02 — Compuerta bloqueante

Ejecuta `docker compose run --rm app python -m dataset_quality.gate --coco
data/validated/coco.json` antes de cualquier etapa posterior. Ver
[comando, códigos de salida y bloqueo](docs/f4-02-gate-blocks.md).

## F4-03 — Reporte `quality.json`

El gate escribe el contrato de calidad en `data/reports/quality.json`, o en la
ruta configurada mediante `QUALITY_REPORT_PATH`. Ver
[campos, evidencia y ejecución con Compose](docs/f4-03-quality-json.md).

## F4-04 — Warn no bloqueante

Los checks `warn` conservan su evidencia en `quality.json` y dejan el proceso
en `exit=0`. Ver [demostración de warn frente a fail](docs/f4-04-warn.md).

## APP-05 — Settings de la política

La UI de Settings persiste cambios validados en `quality.yaml`. Iníciala con
`docker compose up --build ui` y consulta la [guía de persistencia](docs/app-05-settings.md).
