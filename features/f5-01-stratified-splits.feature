Feature: Splits estratificados

Scenario: proporción por clase dentro de tolerancia
  Given un COCO con al menos 2 clases y config de tolerancia
  When genero train/val/test
  Then para cada clase la fracción en cada split
  And está dentro de la tolerancia declarada

Scenario: val y test no pierden clases
  Given las mismas clases que el dataset
  When genero los splits
  Then cada clase tiene al menos 1 imagen en val
  And cada clase tiene al menos 1 imagen en test

Scenario: el evaluador puede recalcular
  Then los conteos por clase y split coinciden con un recuento independiente