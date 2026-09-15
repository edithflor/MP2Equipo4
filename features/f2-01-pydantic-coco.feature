Feature: Validación Pydantic v2 del COCO
  Scenario: COCO válido se acepta
    Given un JSON con images, annotations, categories coherentes
    When lo parseo
    Then obtengo modelos v2

  Scenario: bbox de 3 elementos
    Given un JSON con images, annotations, categories coherentes
    When inyecto bbox de 3 elementos
    Then falla y el error nombra bbox
    And no es un KeyError crudo

  Scenario: category_id inexistente
    Given un JSON con images, annotations, categories coherentes
    When una annotation apunta a una categoría que no está
    Then falla y el error nombra category_id

  Scenario: image_id huérfano
    Given un JSON con images, annotations, categories coherentes
    When una annotation apunta a una imagen que no está
    Then falla y el error nombra image_id

  Scenario: es v2 de verdad
    Given el código
    Then no usa pydantic.v1 ni validator ni dict de v1
