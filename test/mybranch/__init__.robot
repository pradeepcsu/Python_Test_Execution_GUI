*** Settings ***
Library           Selenium2Library
#Resource          mybranch_keywords.robot
Documentation     Test documentation for myBranch test suite.
#Suite Setup       Open myBranch    # Load the web page based on the region and the browser based by the type.
Suite Teardown    Close All Browsers    # Close all open browsers.
