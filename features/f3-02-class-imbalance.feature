Feature: Desbalance de clases

Scenario: ratio mayor / menor
  Given clase A con 400 imágenes y B con 100
  When corro el analizador
  Then el ratio es 4.0

Scenario: clases bajo el mínimo
  Given min_images_per_class = 300
  And una clase con 250 imágenes distintas
  Then esa clase aparece bajo el mínimo

Scenario: cuenta imágenes no cajas
  Given una imagen con 7 cajas de la misma clase
  Then aporta 1 a esa clase