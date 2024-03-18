** Settings **

Library  parrot.RelayController

** Test Cases **

Single Relay Test
       Relay Connect  /dev/ttyUSB0
       Relay ON  1
       Relay OFF  1

All Relay Test
       Relay Connect  /dev/ttyUSB0
       Relay Switch All
       Relay Reset All
