Feature: Client Registration and Authentication
  As a new client
  I want to register for an account and verify my credentials
  So that I can securely access the system

  Scenario: Basic user registration and login with email
    Given I am a newly registered user
    When I login with valid email and password
    Then I should receive a JWT token
    And the token should contain correct user information

  Scenario: User registration and login with username
    Given I am a newly registered user
    When I login with valid username and password
    Then I should receive a JWT token
    And the token should contain correct user information

  Scenario: Failed login attempt after registration
    Given I am a newly registered user
    When I login with incorrect password
    Then I should receive an authentication error

  @concurrent
  Scenario: Small batch registration and login test
    Given there are "5" registered users
    When all users attempt to login simultaneously
    Then login requests should complete successfully

  @concurrent
  Scenario: Medium batch registration and login test
    Given there are "20" registered users
    When all users attempt to login simultaneously
    Then login requests should complete successfully

  @concurrent @performance
  Scenario: Large batch registration and login test
    Given there are "50" registered users
    When all users attempt to login simultaneously
    Then login requests should complete successfully

  @performance
  Scenario Outline: Batch registration performance test
    Given there are "<user_count>" registered users
    When all users attempt to login simultaneously
    Then login requests should complete successfully

    Examples:
      | user_count |
      | 10        |
      | 25        |
      | 75        |
      | 100       |

  @security
  Scenario: Verify JWT token content after registration
    Given I am a newly registered user
    When I login with valid email and password
    Then I should receive a JWT token
    And the token should contain correct user information

  @security
  Scenario: Invalid login attempts after registration
    Given I am a newly registered user
    When I login with incorrect password
    Then I should receive an authentication error

  @regression
  Scenario: Registration and alternate login methods
    Given I am a newly registered user
    When I login with valid email and password
    Then I should receive a JWT token
    And the token should contain correct user information
    When I login with valid username and password
    Then I should receive a JWT token
    And the token should contain correct user information