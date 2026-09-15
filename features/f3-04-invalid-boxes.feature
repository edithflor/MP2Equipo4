Feature: Cajas inválidas

Scenario: ancho negativo
  Given width < 0
  When corro el analizador
  Then se reporta como inválida
  
Scenario: height <= 0
  Given height 0 o negativo
  Then se reporta
  
Scenario: fuera de la imagen
  Given una caja que se sale de width/height de su image
  Then se reporta
  
Scenario: area incoherente
  Given bbox 10x10 y area 999
  Then se reporta