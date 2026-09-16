Feature: Warn no bloquea

  Scenario: solo warns
    Given checks en warn y ninguno en fail
    When corro el gate
    Then exit es 0
    And quality.json registra los warn
    And observed vs threshold siguen presentes
