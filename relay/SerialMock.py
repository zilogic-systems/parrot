import unittest.mock

import serial
from robot.api.logger import console

class SerialMock:
    ROBOT_LIBRARY_SCOPE = "TEST"

    def setup(self):
        self.serial_patcher = unittest.mock.patch("serial.Serial")
        self.MockSerial = self.serial_patcher.start()

    def set_device_response(self, resp):
        s = self.MockSerial()
        s.read_until.return_value = resp.encode("utf-8")

    def teardown(self):
        self.serial_patcher.stop()
