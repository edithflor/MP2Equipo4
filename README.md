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


## Desarrollo local

El proyecto exige Python 3.12. La `.venv` nunca se versiona.

### 1. Crear y activar el entorno virtual
En Linux / macOS:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
