Feature: Near-duplicates por pHash

Scenario: copia recomprimida
  Given una imagen del dataset
  And una copia JPEG recomprimida con otro file_name
  When corro el analizador
  Then el par aparece
  And trae distancia o similitud

Scenario: umbral de distancia configurable
  When bajo el umbral
  Then hay menos pares
  When lo subo
  Then hay más pares

Scenario: no es solo MD5
  Given dos archivos con bytes distintos pero visualmente iguales
  Then pHash los empareja

Scenario: función pura sobre datos ya leídos
  Then el analizador no abre MinIO por su cuenta