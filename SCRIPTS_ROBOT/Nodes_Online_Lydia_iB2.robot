*** Settings ***
| Library | Process
*** Test Cases ***

| Test Case 1-Nodes Online and Offline iB2
| | ${result}= | run process | python | C:\\Python_Scale_Automation\\SCALE_AUTOMATION\\SCRIPTS\\Nodes_Online_Lydia_iB2.py | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt
| | Should be equal as integers | ${result.rc} | 0
| | Should Not Contain | ${result.stdout} | FAIL



