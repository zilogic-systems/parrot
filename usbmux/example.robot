*** Settings ***

Library  parrot.USBSwitchController

*** Test Cases ***

Switch Device 0 to Host 0
       Switch Connect  /dev/ttyUSB0
       Switch Connect USB Device Port to Host Port  0  00

Switch Device 1 to Host 1
       Switch Connect  /dev/ttyUSB0
       Switch Connect USB Device Port to Host Port  1  01
