Feature: Cero fuga

Scenario: IDs disjuntos
  When genero los splits
  Then train ∩ val es vacío
  And train ∩ test es vacío
  And val ∩ test es vacío
  And la unión de los tres es el set de imágenes del dataset (las que entran al split)

Scenario: near-duplicates juntos
  Given pares pHash del analizador
  When genero los splits
  Then para cada par ambas imágenes están en el mismo split

Scenario: par cruzado se detecta
  Given un fixture donde el splitter ignorara pHash
  Then el test de fuga falla