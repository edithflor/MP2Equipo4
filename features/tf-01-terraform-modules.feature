Feature: Terraform por capas
  Scenario: módulos
    Then existen módulos de red, cómputo, datos y almacenamiento
    And no es un único main.tf monolítico
  Scenario: entornos
    Then hay dev y prod separados
  Scenario: validate
    When corro terraform fmt -check -recursive
    And corro init sin backend y validate en ambos entornos
    Then terminan 0
  Scenario: sin secretos
    Then no hay claves AWS en archivos tf
    And tfstate está ignorado y no versionado
