from kivy.logger import Logger
from bluetooth_controller import BluetoothController

class BluetoothInterface:
    def __init__(self) -> None:
        self.bluetooth_controller = BluetoothController()

    def enable(self):
        Logger.info("Turn on Bluetooth adapter")
        return self.bluetooth_controller.enable_adapter()
    
    def disable(self):
        Logger.info("Turn off Bluetooth adapter")
        return self.bluetooth_controller.disable_adapter()
    
    def get_state(self):
        Logger.info("Current state of the local Bluetooth adapter")
        return self.bluetooth_controller.get_state()

    def start_scan(self):
        Logger.info("Start Remote device discovery")
        return self.bluetooth_controller.scan()

    def paired_device(self):
        Logger.info("Bonded devices")
        return self.bluetooth_controller.paired_devices()

    def un_pair(self, address):
        Logger.info("Un pair device")
        return self.bluetooth_controller.unpair(address)

    def get_pair_state(self, mac_address: str):
        Logger.info("Gets the device bonding state with the Remote device")
        return self.bluetooth_controller.get_pair_state(mac_address)

    def get_scan_state(self):
        Logger.info("Gets the current device discovery state")
        return self.bluetooth_controller.get_scan_state()
