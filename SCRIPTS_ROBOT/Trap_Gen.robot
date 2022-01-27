*** Settings ***
| Library | Process
*** Test Cases ***

| Test Case 1-Trap Generation
| | ${result}= | run process | python | C:\\Python_Scale_Automation\\SCALE_AUTOMATION\\SCRIPTS\\Trap_Gen.py | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt
| | Should be equal as integers | ${result.rc} | 0
| | Should Not Contain | ${result.stdout} | FAIL



