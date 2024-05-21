from kivy.logger import Logger
from bluetooth_controller import BluetoothController

class BluetoothInterface:
    def __init__(self) -> None:
        self.bluetooth_controller = BluetoothController()

    def enable(self):
        Logger.info("enable bluetooth adapter")
        return self.bluetooth_controller.enable_adapter()
    
    def disable(self):
        Logger.info("disable bluetooth adapter")
        return self.bluetooth_controller.disable_adapter()
    
    def get_state(self):
        return self.bluetooth_controller.get_state()