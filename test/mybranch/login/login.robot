*** Settings ***
Library           Selenium2Library
Resource          ../custom_keywords.robot

*** Keywords ***
    

*** Test Cases ***
Login - Check Login
    [Documentation]    Verify if login page is opening fine
    [Tags]    test_suite    login
    open browser    https://www.google.com      chrome
    Maximize Browser Window
    sleep   3
    close browser
    
Login - Check Login - 1
    [Documentation]    Verify if login page is opening fine 1
    [Tags]    test_suite1    login
    open browser    https://www.google.com      chrome
    Maximize Browser Window
    sleep   3
    close browser

Login - Check Login - 2
    [Documentation]    Verify if login page is opening fine 2
    [Tags]    test_suite2    login
    open browser    https://www.google.com      chrome
    Maximize Browser Window
    sleep   3
    close browser

Login - Check Login - 3
    [Documentation]    Verify if login page is opening fine 3
    [Tags]    test_suite3    login
    open browser    https://www.google.com      chrome
    Maximize Browser Window
    sleep   3
    close browser