Feature: Ruff de entrega

Scenario: config versionada
  Then ruff está en pyproject.toml o ruff.toml
  And hay reglas elegidas por el equipo
  
Scenario: limpio
  When corro ruff check .
  And ruff format --check .
  Then ambos terminan 0