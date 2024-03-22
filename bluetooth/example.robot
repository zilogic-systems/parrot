** Settings **

Library  parrot.ADBController
Library  parrot.BluetoothController

** Test Cases **

Bluetooth Connect Test
    ADB Select Device       RZCTA0SA72E
    ADB Open An Application  com.waylonhuang.bluetoothpair
    Bluetooth ON
    Bluetooth Connect Device  BC8-Android
    Bluetooth Wait For Device  BC8-Android  10
