Feature: Client Registration

  Scenario: Successful registration
    Given I have a valid user registration payload
    When I send a POST request to "/client_registeration"
    Then I should receive a 200 response
    And the user should be registered successfully

  Scenario: Registration with an invalid email
    Given I have a registration payload with an invalid email
    When I send a POST request to "/client_registeration"
    Then I should receive a 400 response
    And an error message should be displayed
