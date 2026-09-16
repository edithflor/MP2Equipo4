# F4-04 — Los `warn` no bloquean

Un check con severidad `warn` queda registrado en `quality.json` con su valor
`observed`, su `threshold` y sus muestras ofensoras, pero no provoca un código
de salida distinto de cero. Sólo la severidad `fail` bloquea la compuerta.

```powershell
docker compose run --rm app pytest tests/test_f4_04_warn.py -q
```

La prueba configura `small_objects_percentage` como `warn` con umbral `0`: el
resultado es `WARN` y `exit=0`. Luego eleva el mínimo de imágenes a `99999` y
verifica que el mismo dataset se vuelve `FAIL` con exit distinto de cero.
