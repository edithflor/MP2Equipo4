# F4-01 — Política `quality.yaml`

`quality.yaml` es la fuente versionada de los umbrales y severidades de la
compuerta de calidad. La política actual exige al menos 300 imágenes distintas
por clase y marca ese incumplimiento como `fail`.

Incluye una regla para cada analizador F3 disponible:

| Check | Valor observado | Dirección |
| --- | --- | --- |
| `small_objects_percentage` | porcentaje de objetos pequeños | máximo |
| `class_imbalance_ratio` | razón máximo/mínimo de clases | máximo |
| `duplicate_pairs` | pares pHash detectados | máximo |
| `invalid_boxes` | cajas inválidas | máximo |
| `spatial_bias_percentage` | porcentaje del cuadrante dominante | máximo |

`min_images_per_class` complementa esas reglas con el mínimo de imágenes por
clase de F2. La función `load_quality_policy` convierte el resultado de YAML a
`QualityPolicyConfig` de Pydantic antes de usarlo; la compuerta no recibe el
diccionario crudo de `yaml.safe_load`.

## Demostración

Cambiar sólo este valor en `quality.yaml`:

```yaml
min_images_per_class:
  threshold: 99999
  severity: fail
```

hace fallar ese check para un dataset que antes pasaba. La decisión sobre el
código de salida se implementará en F4-02.
