*** Settings ***
| Library | Process
*** Test Cases ***

| Test Case 1-NBIF Soap Calls AS AU
| | ${result}= | run process | python | C:\\Python_Scale_Automation\\SCALE_AUTOMATION\\SCRIPTS\\NBIF_Soap_Call_AS_AU.py | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt
| | Should be equal as integers | ${result.rc} | 0
| | Should Not Contain | ${result.stdout} | FAIL



