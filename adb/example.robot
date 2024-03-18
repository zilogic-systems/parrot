** Settings **

Library  parrot.ADBController

** Test Cases **

ADB USB Screenshot Test
    ADB Select Device  RZCTA0SA72E
    ADB Take Screenshot  output1.png

ADB WiFi Screenshot Test
    ADB IP Connect  192.168.1.111:5555
    ADB Take Screenshot  output2.png
