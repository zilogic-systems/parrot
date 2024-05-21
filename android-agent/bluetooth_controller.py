from jnius import autoclass, cast
from android.broadcast import BroadcastReceiver
from typing import Any,Union
from kivy.logger import Logger
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')

class BluetoothController:

    class BluethoothDevice:
        def __init__(self, name ="", address= "") -> None:
            self.name = name
            self.address = address

        def __eq__(self, other):
            return isinstance(other, BluetoothController.BluethoothDevice) and (self.name == other.name and self.address == other.address)

        def __hash__(self):
            return hash((self.name, self.address))

    def __init__(self) -> None:
        # Change based on android docs
        self.BluetoothAdapter = autoclass("android.bluetooth.BluetoothAdapter")
        self.UUID = "00001101-0000-1000-8000-00805F9B34FB"

        self.ble_adapter = self.BluetoothAdapter.getDefaultAdapter()
        self.device_scanned_count = 0
        self.scanned_devices = set()
        self.connected_device = None
        self.is_connected = False
        self.FOUND = BluetoothDevice.ACTION_FOUND
        self.STARTED = self.BluetoothAdapter.ACTION_DISCOVERY_STARTED
        self.FINISHED = self.BluetoothAdapter.ACTION_DISCOVERY_FINISHED

    def on_scanning(self, context, intent):
        action = intent.getAction()
        if action == self.STARTED:
            self.device_scanned_count = 0
            self.scanned_devices = None
            self.scanned_devices = set()
            print("SCANNING STARTED ")

        elif action == self.FOUND:
            device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
            name = intent.getExtra(BluetoothDevice.EXTRA_NAME)
            self.device_scanned_count =+ 1
            if device:
                print("SCANNING : ", name, device.toString())
                if not name:
                    name = ""
            self.scanned_devices.add(BluetoothController.BluethoothDevice(name, device.toString()))

        elif action == self.FINISHED:
            self.ble_adapter.cancelDiscovery()
            self.boardcast_receiver.stop()
            self.boardcast_receiver = None
            print("SCANNING STOPED")

    def enable_adapter(self) -> bool:
        if (self.ble_adapter and not self.ble_adapter.isEnabled()):
            return self.ble_adapter.enable()

    def disable_adapter(self)->bool:
        if (self.ble_adapter and self.ble_adapter.isEnabled()):
            return self.ble_adapter.disable()

    def paired_devices(self):
        if self.ble_adapter:
            bounded_devices = self.ble_adapter.getBondedDevices().toArray()
            response = {}
            for device in bounded_devices:
                response = {**response , device.getName() : device.getAddress()}
        return response

    def scan(self):
        actions = [self.FOUND, self.STARTED, self.FINISHED]
        self.boardcast_receiver = BroadcastReceiver(self.on_scanning, actions=actions)
        self.boardcast_receiver.start()
        self.ble_adapter.startDiscovery()

    def is_device_paired(self, remote_info: dict) -> bool:
        name = remote_info.get("name", "").lower()
        mac_address = remote_info.get("mac_address","").lower()
        bounded_devices = self.ble_adapter.getBondedDevices().toArray()

        def equals(device):
            if name == device.getName().lower() or mac_address == device.getAddress().lower():
                return True
            return False

        filtered_devices = filter(equals, bounded_devices)
        return (True,filtered_devices[0]) if len(filtered_devices) else (False, None)

    def pair(self, mac_address: str):
        if self.ble_adapter and mac_address.strip() != "":
            device = self.ble_adapter.getRemoteDevice(mac_address)
            if device and device.getBondState() != BluetoothDevice.BOND_BONDED:
                device.createBond()

    def connect(self, device_info: dict = {}):
        self.connected_device = None
        device = self.ble_adapter.getRemoteDevice(device_info.get("address"))
        if device and device.getBondState()  != BluetoothDevice.BOND_NONE:
            UUID = autoclass('java.util.UUID')
            self.connected_device = device.createRfcommSocketToServiceRecord(UUID.fromString(self.UUID))
            self.connected_device.getInputStream()
            self.connected_device.getOutputStream()
            self.connected_device.connect()
            print("CONNECTED DEVICE : ", self.connected_device.isConnected(), self.connected_device.getRemoteDevice().toString())

    def disconnect(self):
        if self.connected_device:
            print("DISCONNECTED : ", self.connected_device.isConnected())
            self.connected_device.close()
            self.is_connected = False
            self.connected_device = None

    def unpair(self, address: Union[str, Any]):
        if self.ble_adapter and address.strip():
            device = self.ble_adapter.getRemoteDevice(address)
            if (device.getBondState() == BluetoothDevice.BOND_BONDED):
                   device.removeBond();
    
    def get_state(self):
        device = self.ble_adapter.getState()

        return device