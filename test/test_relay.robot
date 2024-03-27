** Settings **

Library  SerialMock
Library  parrot.RelayController
Test Setup  Setup
Test Teardown  Teardown

** Test Cases **
Test Relay ON with Command Success
       Set Device Response  OK
       Relay Connect  /dev/ttyUSB0
       Relay ON  1
       Verify Command  S1\r\n

Test Relay ON with Command Timeout
       Set Device Response  ${EMPTY}
       Relay Connect  /dev/ttyUSB0
       Run Keyword And Expect Error  *  Relay ON  1

Test Relay OFF with Command Success
       Set Device Response  OK
       Relay Connect  /dev/ttyUSB0
       Relay OFF  1
       Verify Command  C1\r\n

Test Relay OFF with Command Timeout
       Set Device Response  ${EMPTY}
       Relay Connect  /dev/ttyUSB0
       Run Keyword And Expect Error  *  Relay OFF  1

Test Relay Toggle with Command Success
       Set Device Response  OK
       Relay Connect  /dev/ttyUSB0
       Relay Toggle  1
       Verify Command  T1\r\n

Test Relay Toggle with Command Timeout
       Set Device Response  ${EMPTY}
       Run Keyword And Expect Error  *  Relay Toggle  1

Test Relay Switch All with Command Success
       Set Device Response  OK
       Relay Connect  /dev/ttyUSB0
       Relay Switch All
       Verify Command  SA\r\n

Test Relay Switch All with Command Timeout
       Set Device Response  ${EMPTY}
       Relay Connect  /dev/ttyUSB0
       Run Keyword And Expect Error  *  Relay Switch All

Test Relay Reset All with Command Success
       Set Device Response  OK
       Relay Connect  /dev/ttyUSB0
       Relay Reset All
       Verify Command  CA\r\n

Test Relay Reset All with Command Timeout
       Set Device Response  ${EMPTY}
       Relay Connect  /dev/ttyUSB0
       Run Keyword And Expect Error  *  Relay Reset All
