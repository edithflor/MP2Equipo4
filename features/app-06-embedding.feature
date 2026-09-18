Feature: Exploración dimensional

  Scenario: offline
    Given un artefacto precomputado
    When abro la vista de embeddings
    Then no se calcula t-SNE/PCA/UMAP en ese GET

  Scenario: hover y filtro
    Given la vista de embeddings cargada
    When hago hover en un punto
    Then veo la imagen correspondiente
    When filtro por clase
    Then no recarga la página completa
