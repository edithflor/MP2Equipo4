Feature: Sesgo espacial y descriptiva

Scenario: media mediana percentiles
  Given un set de áreas conocido
  When corro el analizador
  Then reporta media
  And mediana
  And al menos p25 y p75 o p90

Scenario: sesgo espacial
  Given cajas concentradas en un cuadrante
  Then el reporte refleja esa concentración
  And no es solo la media del área

Scenario: coinciden con un recálculo
  Then media/mediana/percentiles cuadran con el test