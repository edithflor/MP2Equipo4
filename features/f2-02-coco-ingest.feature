Feature: Ingesta del COCO

  Scenario: COCO válido se ingesta
    Given un JSON COCO que pasa F2-01
    When corro la ingesta
    Then termina 0
    And queda un artefacto de entrada para analizadores
    And no se versionan las imágenes en git

  Scenario: COCO inválido no se ingesta
    Given un JSON con bbox de 3 elementos
    When corro la ingesta
    Then termina distinto de 0
    And el error nombra el campo
    And no queda artefacto válido a medias

  Scenario: la ruta sale del env
    Given un JSON COCO que pasa F2-01
    And configuro rutas de ingesta por variables de entorno
    When corro la ingesta
    Then usa las rutas configuradas
