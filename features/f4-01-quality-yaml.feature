Feature: Política quality.yaml

  Scenario: mínimo del curso
    Given quality.yaml
    Then min_images_per_class >= 300
    And su severidad es fail

  Scenario: cambiar YAML cambia el gate
    Given un dataset que pasaba
    When pongo min_images_per_class: 99999
    Then ese check falla
    And no cambié código Python

  Scenario: yaml validado con Pydantic
    When el YAML está malformado
    Then pydantic nombra el campo
    And no se usa el dict crudo de yaml.safe_load como config
