Feature: Proporciones de split

Scenario: default 70/15/15
  Given config default
  When spliteo N imágenes
  Then |train|+|val|+|test| = N
  And las proporciones están cerca de 0.70/0.15/0.15 dentro de redondeo

Scenario: config cambia tamaños
  Given train=0.80 val=0.10 test=0.10
  When spliteo N imágenes
  Then los tamaños cambian acorde
  And no toqué el algoritmo, solo config

Scenario: proporciones inválidas se rechazan
  Given train+val+test != 1
  Then Pydantic/ingesta de config falla (F2-03)