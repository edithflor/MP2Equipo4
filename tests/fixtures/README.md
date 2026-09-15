# Muestra MP1 para SPEC-F2-01

`mp1-coco.json` procede de una consulta SELECT de solo lectura a la base
`image_repo` del contenedor local `proyecto1-mariadb`, el 14 de septiembre de 2026.
Contiene las 5 imágenes, 3 categorías y 8 anotaciones disponibles en esa consulta.
No se generaron ni modificaron cajas. Los valores de área se conservan sin recalcular.

Es una extracción adaptada a COCO del esquema antiguo, no una descarga del endpoint
del portal actual. Mapeo: `images.filename → file_name`, las cuatro columnas
`bbox_* → bbox`, e `iscrowd → iscrowd`. Se añadió `segmentation: []` porque la fuente
es detección por cajas. No se incluyeron storage keys, credenciales ni imágenes.

Incluye registros seed (`sample-red.png`, `sample-blue.png`). No acredita anotación
humana, contenido visual, integridad de los archivos ni el volumen A-01. Su propósito
es verificar el contrato de entrada con valores existentes del MP1.

Para reproducir la extracción, usar JSON_OBJECT/JSON_ARRAYAGG sobre las tablas
`images`, `categories`, `annotations`, aplicando el mapeo anterior, sin UPDATE ni INSERT.
