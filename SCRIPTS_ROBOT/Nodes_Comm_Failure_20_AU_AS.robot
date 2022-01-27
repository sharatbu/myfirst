*** Settings ***
| Library | Process
*** Test Cases ***

| Test Case 1-Nodes Communication Failure 20% AU AS
| | ${result}= | run process | python | C:\\Python_Scale_Automation\\SCALE_AUTOMATION\\SCRIPTS\\Nodes_Comm_Failure_20_AU_AS.py | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt
| | Should be equal as integers | ${result.rc} | 0
| | Should Not Contain | ${result.stdout} | FAIL



