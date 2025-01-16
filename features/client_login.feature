Feature: Client Login

  Scenario: Successful login
    Given I have a registered user with valid credentials
    When I send a POST request to "/client_login" with the valid credentials
    Then I should receive a 200 response
    And the user should be authenticated successfully

  Scenario: Login with invalid credentials
    Given I have an unregistered user or invalid credentials
    When I send a POST request to "/client_login" with the invalid credentials
    Then I should receive a 401 response
    And an error message should be displayed

  Scenario: Login with missing fields
    Given I have a login request with missing fields
    When I send a POST request to "/client_login"
    Then I should receive a 400 response
    And an appropriate error message should be displayed
