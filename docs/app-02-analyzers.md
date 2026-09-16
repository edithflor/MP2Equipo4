# APP-02 — Analizadores

La aplicación expone cinco pestañas independientes y alimentadas por los
analizadores de F3:

| Pestaña | Analizador | Visualización | Muestras ofensoras |
| --- | --- | --- | --- |
| Objetos pequeños | `small_objects` | porcentaje y conteo por clase | id y archivo de imagen |
| Desbalance | `class_imbalance` | conteo por clase | clases bajo el mínimo |
| Duplicados | `phash` | pares detectados | par de archivos e ids |
| Cajas inválidas | `invalid_boxes` | conteo por motivo | anotación, imagen y motivo |
| Sesgo espacial | `spatial_bias` | distribución por cuadrante | imágenes del cuadrante dominante |

La UI carga `data/validated/coco.json` cuando existe. En un entorno nuevo usa
`tests/fixtures/mp1-coco.json`, que es un ejemplo COCO versionado y no una serie
inventada en la vista. Para calcular duplicados con pHash se cargan también las
imágenes desde el selector de la aplicación.

Las vistas no importan controladores de MariaDB ni MinIO; sólo consumen datos en
memoria y funciones Python de F3.

## Ejecutar

```bash
streamlit run src/dataset_quality/ui/app.py
```

## Verificar

```bash
pytest tests/test_app_02_analyzers.py -q
ruff check src/dataset_quality/ui tests/test_app_02_analyzers.py
```
