Feature: Analyzers

  Scenario: cinco pestañas enrutadas
    Then existen las cinco rutas o tabs
    And no es un único placeholder

  Scenario: datos de los analizadores
    Given la salida de F3 o quality.json
    Then cada pestaña muestra gráfica o tabla coherente con ese analizador
    And las muestras ofensoras se pueden abrir o listar

  Scenario: mutar el COCO de test mueve las gráficas
    Given la salida de F3 o quality.json
    When cambio datos y regenero el reporte
    Then la UI no sigue mostrando series fijas

  Scenario: UI sin drivers
    Then no importa boto3, Minio ni pymysql en las vistas

