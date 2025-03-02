*** Settings ***

Library    OperatingSystem

*** Test Cases ***
TEST

    Log    This is my test case
    Count Items In Directory    C:\\Temp
