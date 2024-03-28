** Settings **

Library  MockUtil.SerialMock
Library  parrot.USBSwitchController
Test Setup  Setup
Test Teardown  Teardown

** Test Cases **
Test Switch Connect USB Device Port to Host Port Success
    Set Device Response  OK
    Switch Connect  /dev/ttyUSB1
    Switch Connect USB Device Port to Host Port  0  1
    Verify Command  H0\rO01\r

Test Switch Connect USB Device Port to Host Port Timeout
    Set Device Response  ${EMPTY}
    Switch Connect  /dev/ttyUSB1
    Run Keyword And Expect Error  *  Switch Connect USB Device Port to Host Port  0  1

Test Switch Disconnect USB Device Port to Host Port Success
    Set Device Response  OK
    Switch Connect  /dev/ttyUSB1
    Switch Disconnect USB Device Port to Host Port  1
    Verify Command  F01\r

Test Switch Disconnect USB Device Port to Host Port Timeout
    Set Device Response  ${EMPTY}
    Switch Connect  /dev/ttyUSB1
    Run Keyword And Expect Error  *  Switch Disconnect USB Device Port to Host Port  1

Test All Switch Reset Success
    Set Device Response  OK
    Switch Connect  /dev/ttyUSB1
    Switch Reset All
    Verify Command  A\r

Test All Switch Reset Timeout
    Set Device Response  ${EMPTY}
    Switch Connect  /dev/ttyUSB1
    Run Keyword And Expect Error  *  Switch Reset All
