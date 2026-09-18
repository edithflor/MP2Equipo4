Feature: Volumen vs compuerta (tramo F4)
  Scenario: política vs conteo real
    Given quality.yaml con mínimo 300 y severidad fail
    When cuento por clase después de colapsar duplicados
    Then con 300 el check de mínimo pasa
    And al duplicar una imagen quedan 299 y el gate falla

  Scenario: no se baja el umbral para pasar
    Then una política con mínimo 50 o severidad warn se rechaza

  Scenario: archivos no verificables
    Then imágenes ausentes o corruptas no permiten liberar el dataset
