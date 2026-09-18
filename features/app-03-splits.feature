Feature: UI Splits

  Scenario: distribución por clase
    Given splits.json de una corrida real
    When abro Splits
    Then veo conteos por clase en train, val y test
    And coinciden con F5-01 / F5-04

  Scenario: leakage
    Given splits.json de una corrida real
    When abro Splits
    Then el check de pares cruzados coincide con F5-03
    And si hay 0 leaked pairs, los pares pHash están en el mismo split

  Scenario: UI sin drivers
    Then la vista no abre BD ni MinIO ni S3

  Scenario: compuerta bloqueada ante fail
    Given un gate en fail
    When abro Splits
    Then esta pantalla muestra "no hay split / bloqueado", no un train/val/test fake
