Feature: Splits reproducibles

Scenario: misma semilla, mismos IDs
  Given seed = 42
  When corro el split dos veces
  Then train_a == train_b
  And val_a == val_b
  And test_a == test_b
  And un diff de los JSON/archivos está vacío

Scenario: otra semilla cambia el particionado
  When corro con seed distinto
  Then al menos un split difiere