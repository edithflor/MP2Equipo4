Feature: Settings persiste la política

  Scenario: guardar cambia el YAML
    Given quality.yaml versionado
    When cambio min_images_per_class (u otro umbral) en Settings
    Then el archivo quality.yaml en disco cambió
    And no solo cambió el estado de React

  Scenario: el gate lee lo guardado
    When corro el comando del gate
    Then usa el umbral nuevo (F4-01)
    And sin tocar código Python

  Scenario: UI sin drivers
    Then Settings no abre BD ni S3 ni MinIO
