*** Settings ***
| Library | Process
*** Test Cases ***

| Test Case 1-Node Profile Update - AU/AS
| | ${result}= | run process | python | C:\\Python_Scale_Automation\\SCALE_AUTOMATION\\SCRIPTS\\Node_Profiles_Update_AU_AS.py | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt
| | Should be equal as integers | ${result.rc} | 0
| | Should Not Contain | ${result.stdout} | FAIL


