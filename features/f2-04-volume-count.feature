Feature: Conteo M3

Scenario: imágenes no cajas
  Given 1 imagen con 7 cajas de car
  Then car tiene 1 imagen

Scenario: una imagen cuenta en dos clases
  Given 1 imagen con car y person
  Then suma 1 a car y 1 a person

Scenario: sin caja no cuenta
  Given una image sin annotations
  Then no suma a ninguna clase

Scenario: caja degenerada no cuenta
  Given una sola caja con width <= 0
  Then esa imagen no suma a esa clase