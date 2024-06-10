from kivy.app import App
from kivy.uix.label import Label
from xmlrpc.server import SimpleXMLRPCServer
from kivy.logger import Logger
from kivy.core.window import Window
import threading
from bluetooth_interface import BluetoothInterface
from permission_controller import PermissionController

class AndroidAgent(App):
    
    def __init__(self, port:int=8080, host:str="0.0.0.0"):
        super().__init__()
        self.server = SimpleXMLRPCServer((host,port))
        self.bluetooth_interface = BluetoothInterface()
        self.permission_controller = PermissionController()
        self._register_methods()
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        
    def _register_methods(self):
        self.server.register_function(self.bluetooth_interface.enable,'enable')
        self.server.register_function(self.bluetooth_interface.disable,'disable')
        self.server.register_function(self.bluetooth_interface.get_state,'get_state')
        self.server.register_function(self.bluetooth_interface.start_scan,'scan')
        self.server.register_function(self.bluetooth_interface.paired_device,'paired_device')
        self.server.register_function(self.bluetooth_interface.un_pair,'un_pair')
        self.server.register_function(self.bluetooth_interface.get_pair_state, 'pair_state')
        self.server.register_function(self.bluetooth_interface.get_scan_state, 'scan_state')
        self.server.register_function(self.bluetooth_interface.cancel_scan,'cancel_scan')
        self.server.register_function(self.bluetooth_interface.start_pair,'start_pair')

    def build(self):
        self.server_thread.start()
        Window.bind(on_request_close=self.on_request_close)
        self.permission_controller.request_bluetooth_permissions()
        return Label(text='Zilogic Systems')

    def on_request_close(self,*args):
        self.server_thread.join()
        self.server_thread = None

if __name__ == "__main__":
    AndroidAgent().run()

