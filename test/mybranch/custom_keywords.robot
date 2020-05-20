*** Settings ***
Library           Selenium2Library
#Library           MyBranch

*** Variables ***

${QA}    http://mybranch-qa.bank.org
${UAT2}    http://web-uat.bank.org


*** Keywords ***
Open myBranch
    # [Arguments]    ${REGION}
#    ${URL}    Set Variable If
#    ...    "${REGION}" == "QA"    ${QA}
#    ...    "${REGION}" == "UAT2"    ${UAT2}
#    Set Global Variable    ${URL}
    # Set Global Variable    ${REMOTE_URL}
    # Log    remote url: ${REMOTE_URL}
    # Open Browser    ${URL}    ${BROWSER}    ${REMOTE_URL}
    # Load Browser
    # Log    ${browser}

Log In myBranch
    [Arguments]    ${username}    ${password}
    Load Browser
    Maximize Browser Window
    Enter Text    LogIn_UserID    ${username}
    Enter Text    LogIn_Password    ${password}
    Click On    LogIn_LogIn
    ${Error_Message} =     check exists    Account_Locked
    Run Keyword If    ${Error_Message} == ${True}    Fail    ${username}/${password} Account is Locked
    Enter Text    LogInSecurity_Answer    test
    Click On    LogIn_LogIn
