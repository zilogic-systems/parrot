** Settings **

Library  SerialMock
Library  parrot.RelayController
Test Setup  Setup
Test Teardown  Teardown

** Test Cases **

Single Relay Test
       Set Device Response  ${EMPTY}
       Relay Connect  /dev/ttyUSB0
       Relay ON  1
       Relay OFF  1

All Relay Test
       Set Device Response  OK
       Relay Connect  /dev/ttyUSB0
       Relay Switch All
       Relay Reset All
