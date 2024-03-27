import unittest.mock

import serial
from robot.api.logger import console

class Error(Exception):
    """Represents an error in the Relay Controller."""

class SerialMock:
    ROBOT_LIBRARY_SCOPE = "TEST"

    def setup(self):
        self.serial_patcher = unittest.mock.patch("serial.Serial")
        self.MockSerial = self.serial_patcher.start()

    def set_device_response(self, resp):
        s = self.MockSerial()
        s.read_until.return_value = resp.encode("utf-8")

    def verify_command(self, expected):
        s = self.MockSerial()
        written = []
        for call in s.write.call_args_list:
            written.append(call[0][0])
        written = b"".join(written)
        expected = expected.encode("utf-8")
        if expected != written:
            raise Error(f"Command expected is '{expected}' for got '{written}'")

        s.write.call_args_list.clear()

    def teardown(self):
        self.serial_patcher.stop()
