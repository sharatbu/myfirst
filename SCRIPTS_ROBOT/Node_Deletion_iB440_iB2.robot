*** Settings ***
| Library | Process
*** Test Cases ***

| Test Case 1-Bulk Node Deletion - iB440/iB2
| | ${result}= | run process | python | C:\\Python_Scale_Automation\\SCALE_AUTOMATION\\SCRIPTS\\Node_Deletion_iB440_iB2.py | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt
| | Should be equal as integers | ${result.rc} | 0
| | Should Not Contain | ${result.stdout} | FAIL


