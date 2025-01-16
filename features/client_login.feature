Feature: Client Login Authentication
  As a registered client
  I want to be able to login to the system
  So that I can access my account securely

  Background:
    Given I am a registered user

  Scenario: Successful login with email
    When I login with valid email
    Then I should receive a valid JWT token

  Scenario: Successful login with username
    When I login with valid username
    Then I should receive a valid JWT token

  Scenario: Failed login with incorrect password
    When I attempt to login with incorrect credentials
    Then I should receive an authentication error

  Scenario Outline: Login with different valid credentials
    Given I have a registered user with valid credentials
    When I send a POST request to "/client_login" with the valid credentials
    Then I should receive a valid JWT token

    Examples:
      | credential_type |
      | email          |
      | username       |

  Scenario: Small scale concurrent login test
    Given I register "3" test users
    When I test concurrent user logins
    Then all login requests should succeed with valid tokens

  Scenario: Medium scale concurrent login test
    Given I register "10" test users
    When I test concurrent user logins
    Then all login requests should succeed with valid tokens

  Scenario: Large scale concurrent login test
    Given I register "50" test users
    When I test concurrent user logins
    Then all login requests should succeed with valid tokens

  @performance
  Scenario: Performance test with high concurrent load
    Given I register "100" test users
    When I test concurrent user logins
    Then all login requests should succeed with valid tokens