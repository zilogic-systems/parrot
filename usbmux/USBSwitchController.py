#
# Copyright 2024 Zilogic Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Author: Zilogic Systems <code@zilogic.com>
Requirements: robotframework, pyserial
"""

import re

import argparse

import serial
from robot.api.deco import keyword


class Error(Exception):
    """Represents an error in the USB Switch Controller."""


class USBSwitchController:
    """A library providing keywords for USB Switch Controller.

    The USB Switch can switch 8 device ports to one of the 2 host ports.
    """

    ROBOT_AUTO_KEYWORDS = False
    ROBOT_LIBRARY_SCOPE = 'TEST'

    def __init__(self):
        self.serial_interface = None

    def _verify_execution(self, validation_data: str = "OK") -> bool:
        """
        To verify the response from the serial port.

            - ``validation_data``: Expected response. Defaults to ``OK``.
        """
        validate_pattern = r"\bOK\b"
        verified_string = (self.serial_interface.read_until(validation_data.encode()))
        decode_data = verified_string.decode("utf-8")
        validate_data = decode_data.strip()
        validate_flag = re.IGNORECASE
        data = re.search(validate_pattern, validate_data, validate_flag)

        if data and data.group() == validation_data:
            return True
        return False

    def _switch(self, cmd) -> bool:
        """
        Writes the serial command to the USB switch.

            - ``cmd``: Serial command.
        """
        self.serial_interface.write(f"{cmd}\r".encode())
        return self._verify_execution()

    @keyword("Switch Connect")
    def switch_connect(self, device: str = "/dev/ttyUSB0") -> bool:
        """Opens connection to Switch Controller.

        The Switch Controller to connect to is specified by ``device``. This is
        generally the device name of the serial device corresponding to the USB
        Switch. An example of serial device name in Linux, is ``/dev/ttyUSB0``.
        Passes if it is connected.

        *Example*

        | Switch Connect    | /dev/ttyUSB1 |
        | Switch Connect    | COM1   |
        """
        try:
            self.serial_interface = serial.Serial(
                device,
                baudrate=9600,
                timeout=10,
                write_timeout=1,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
            )

        except (serial.SerialException, FileNotFoundError) as error:
            raise Error("Serial Connection Failed") from error
        return True

    @keyword("Switch Disconnect")
    def switch_disconnect(self) -> bool:
        """Closes connection to the Switch Controller."""

        try:
            self.serial_interface.close()

        except (serial.SerialException, AttributeError) as error:
            raise Error("No Device Connected") from error
        return True

    @keyword("Switch Connect USB Device Port to Host Port")
    def switch_connect_usb_device_to_host(self, host_port='0', device_port='00') -> bool:
        """Connects the host with the device port.

            - ``host_port``: Host port  is either ``0`` or ``1``.
            - ``device_port``: Device port is two digit number from ``00 - 07``.

        *Example*

        | Switch Connect USB Device Port to Host Port   | 0 | 01 |

        """
        if self._switch(f"H{host_port}"):
            return self._switch(f"O{device_port}")
        return False

    @keyword("Switch Disconnect USB Device Port to Host Port")
    def switch_disconnect_usb_device_to_host(self, device_port="00") -> bool:
        """Disconnects the USB device port from the host port.

            - ``device_port``: Device port is two digit number from ``00 - 07``.

        *Example*

        | Switch Disconnect USB Device Port to Host Port    | 01 |

        """
        return self._switch(f"F{device_port}")

    @keyword("Switch Reset All")
    def switch_reset_all(self) -> bool:
        """Resets the USB switch and disables all device ports.

        This keyword ``Switch Reset All`` should be used at the beginning and
        the end of the test case. By resetting all Switch it does not affect the
        next test case.
        """
        return self._switch("A")


def command_line_args():

    parser = argparse.ArgumentParser(description='A command line utility to control ZS-USBSwitch.')

    parser.add_argument('-d', '--device',
                        default='/dev/ttyUSB0',
                        help='Specify ZS-USB device.')
    parser.add_argument('-a','--action',
                        choices=['connect', 'disconnect'],
                        type=str,
                        help="Action to perform connect/disconnect.")
    parser.add_argument('--host',
                        choices=[0,1],
                        type=int,
                        help='Specify the host 0 or 1.')
    parser.add_argument('-p', '--port',
                        type=int,
                        choices=[i for i in range(8)],
                        help="ports to connect/disconnect from 0 to 7.")
    parser.add_argument('--reset',
                        action='store_true',
                        help='Reset the switch.')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = command_line_args()

    switch = USBSwitchController()
    switch.switch_connect(args.device)

    if args.reset:
        print("RESET: ZUS - 8 PORT USB SWITCH")
        switch.switch_reset_all()
        exit(0)

    host = args.host
    port = f'0{args.port}'

    if args.action == "connect":
        switch.switch_connect_usb_device_to_host(host, port)
    if args.action == "disconnect":
        switch.switch_disconnect_usb_device_to_host(port)

    switch.switch_disconnect()
