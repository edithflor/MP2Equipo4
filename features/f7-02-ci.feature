Feature: CI que falla de verdad

Scenario: el workflow existe
  Given .github/workflows
  Then corre ruff (o lint)
  And corre pytest
  And corre el quality gate

Scenario: un fail pone el build en rojo
  Given un check fail (umbral imposible en una rama de prueba)
  Then el job termina distinto de 0
  And no hay continue-on-error en esos pasos

Scenario: último run en default
  Then main/default tiene un run reciente