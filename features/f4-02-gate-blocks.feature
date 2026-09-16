Feature: Fail bloquea el pipeline

  Scenario: exit code
    Given un fail inducido (umbral imposible)
    When corro el comando del gate
    Then el exit code es distinto de 0

  Scenario: no sigue la etapa siguiente
    Given el orquestador (CLI o dvc.yaml)
    When el gate falla
    Then split no se ejecuta
    And no hay promoción a PROD

  Scenario: FAIL impreso con exit 0 no cuenta
    Then no se continúa el pipeline después de un fail
