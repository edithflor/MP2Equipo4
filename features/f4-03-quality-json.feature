Feature: quality.json

  Scenario: campos por check
    When corre el gate
    Then quality.json lista cada check
    And incluye observed
    And incluye threshold
    And incluye ids ofensores o lista vacía

  Scenario: coincide con los analizadores
    When corre el gate
    Then los valores observed cuadran con F3-01..05 sobre el mismo COCO
