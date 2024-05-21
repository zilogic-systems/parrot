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
        self._enable_permission()
        self._register_methods()
        self.server_thread = threading.Thread(target=self.server.serve_forever)

    def _enable_permission(self):
        permission_controller = PermissionController()
        permission_controller.request_bluetooth()
        permission_controller.request_location()
        
    def _register_methods(self):
        bluetooth_interface = BluetoothInterface()
        self.server.register_function(bluetooth_interface.enable,'enable')
        self.server.register_function(bluetooth_interface.disable,'disable')
        self.server.register_function(bluetooth_interface.get_state,'get_state')

    def build(self):
        self.server_thread.start()
        Window.bind(on_request_close=self.on_request_close)
        return Label(text='Zilogic Systems')

    def on_request_close(self,*args):
        self.server_thread.join()
        self.server_thread = None

if __name__ == "__main__":
    AndroidAgent().run()

