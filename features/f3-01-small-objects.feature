Feature: Analizador de objetos pequeños

Scenario: umbral por defecto 32x32
  Given bboxes de 16x16 y de 64x64
  When corro el analizador con config default
  Then el de 16x16 es ofensor
  And el de 64x64 no
  
Scenario: umbral configurable sin tocar código
  Given el mismo COCO
  When cambio el umbral por config
  Then cambian el porcentaje y la lista de ofensores
  
Scenario: reporta porcentaje, clase más afectada y muestras
  Then el resultado incluye porcentaje
  And la clase más afectada
  And ids de muestras ofensoras
  
Scenario: función pura
  Then el módulo no lee env ni abre BD ni MinIO