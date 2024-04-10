import unittest.mock
import serial
import pytesseract
import pyzbar
import subprocess
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

class TesseractMock:
    ROBOT_LIBRARY_SCOPE = "TEST"

    def setup(self):
        self.open_patcher = unittest.mock.patch("PIL.Image.open")
        self.image_to_data_patcher = unittest.mock.patch("pytesseract.image_to_data")
        self.mock_open = self.open_patcher.start()
        self.mock_image_to_data = self.image_to_data_patcher.start()

    def set_image_data(self, data):
        self.mock_image_to_data.return_value = {"text" : data.split(" ")}

    def teardown(self):
        self.open_patcher.stop()
        self.image_to_data_patcher.stop()

class PyzbarMock:
    ROBOT_LIBRARY_SCOPE = "TEST"

    def setup(self):
        self.open_patcher = unittest.mock.patch("PIL.Image.open")
        self.qr_decode_patcher = unittest.mock.patch("pyzbar.pyzbar.decode")
        self.mock_open = self.open_patcher.start()
        self.mock_qr_decode = self.qr_decode_patcher.start()

    def set_qrcode_data(self, data):
        self.mock_obj = unittest.mock.Mock()
        self.mock_obj.data = data.encode()
        self.mock_qr_decode.return_value = [self.mock_obj]

    def teardown(self):
        self.open_patcher.stop()
        self.qr_decode_patcher.stop()

class SubprocessMock:
    ROBOT_LIBRARY_SCOPE = "TEST"

    def setup(self):
        self.subprocess_patcher = unittest.mock.patch("subprocess.run")
        self.mock_run = self.subprocess_patcher.start()

    def set_adb_response(self, returncode: int, stdout:str=""):
        mock_resp = unittest.mock.Mock()
        mock_resp.stdout = stdout
        mock_resp.stderr = ""
        mock_resp.returncode = returncode
        self.mock_run.return_value = mock_resp

    def verify_adb_command(self, cmd: list):
        written = []
        for call in self.mock_run.call_args_list:
            written.append(call[0][0])
        if cmd in written:
            position = written.index(cmd)
            if cmd != written[position]:
                raise Error(f"Command expected is {cmd} for got {written[position]}")
        self.mock_run.call_args_list.clear()

    def teardown(self):
        self.subprocess_patcher.stop()
