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
from time import sleep as delay

import argparse
import serial

from robot.api.deco import keyword


class RelayError(Exception):
    """Represents an error in the Relay Controller."""


class RelayController:
    """A library providing keywords for the ZUS-Relay Controller."""

    ROBOT_AUTO_KEYWORDS = False
    ROBOT_LIBRARY_SCOPE = 'TEST'

    def __init__(self):
        self.relay_interface = None

    @keyword("Relay Connect")
    def relay_connect(self, device):
        """Opens connection to the Relay Controller.

        The Relay Controller to connect to is specified by ``device``. This is
        generally the device name of the serial device corresponding to the USB
        Relay. An example of serial device name in Linux, is "/dev/ttyUSB0".

        *Example*

        | Relay Connect | /dev/ttyUSB0 |
        | Relay Connect | COM1         |
        """
        try:
            self.relay_interface = serial.Serial(
                device,
                baudrate=115200,
                timeout=2,
                write_timeout=2,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
            )

        except (serial.SerialException, ValueError) as err:
            raise RelayError(f"Connection Failed {device}") from err

    @keyword("Relay Disconnect")
    def relay_disconnect(self):
        """Closes connection to the Relay Controller."""
        try:
            self.relay_interface.close()

        except (AttributeError, serial.serialutil.PortNotOpenError) as error:
            raise RelayError("No Device Connected") from error

    def _relay(self, port: int, turn_on=None) -> bool:
        """Converts cmd to hex and writes to serial Device.

        - port - Switch ON the specified Relay.
        - turn_on - Passing `toggle`/True/False. Defaults to ``True``.

        *Returns*

        _bytes_ - Returns bytes to Serial device.
        """
        if turn_on == "on":
            cmd = f"S{port}"
        elif turn_on == "off":
            cmd = f"C{port}"
        else: # Toggle ON/OFF
            cmd = f"T{port}"

        self.relay_interface.reset_output_buffer()
        self.relay_interface.reset_input_buffer()
        self.relay_interface.write(cmd.encode())
        delay(0.1)
        self.relay_interface.write("\r\n".encode())
        expect = "OK".encode()
        output = self.relay_interface.read_until(expect)
        if expect in output:
            return True
        return False

    @keyword("Relay ON")
    def relay_on(self, port: int) -> None:
        """Turn ON the relay specified by ``port``.

        ``port`` must be a value in the range 1 to 8.

        *Example*

        | Relay ON |  1 |
        | Relay ON |  5 |
        """
        if self._relay(port, "on"):
            return
        raise RelayError(f"Invalid command \n Unable to turn on port {port}")

    @keyword("Relay OFF")
    def relay_off(self, port: int) -> None:
        """Turn OFF the relay switch specified by ``port``.

        ``port`` must be a value in the range 1 to 8.

        *Example*

        | Relay OFF | 2 |
        | Relay OFF | 4 |
        """
        if self._relay(port, "off"):
            return
        raise RelayError(f"Invalid command \n Unable to turn off port {port}")

    @keyword("Relay Toggle")
    def relay_toggle(self, port: int) -> None:
        """Toggle ON/OFF the relay switch specified by ``port``.

        ``port`` must be a value in the range 1 to 8.

        *Example*
        | Relay Toggle | 2 |
        | Relay Toggle | 3 |
        """
        if self._relay(port):
            return
        raise RelayError(f"Invalid command \n Unable to toggle port {port}")

    @keyword("Relay Switch All")
    def relay_switch_all(self) -> None:
        """Sets all relays to ON state."""
        if self._relay("A", "on"):
            return
        raise RelayError("Unable to turn on all ports")

    @keyword("Relay Reset All")
    def relay_reset_all(self) -> None:
        """Sets all relays to OFF state."""
        if self._relay("A", "off"):
            return
        raise RelayError("Unable to turn off all ports")


def command_line_args():
    """
    Method for getting command line arguments

    *Returns*

        _Namespace_
    """

    parser = argparse.ArgumentParser(description='A command line utility to control ZUR- 8 Port USB RELAY.')
    parser.add_argument('-d', '--device',
                        help='Specify ZUR USB Relay device [/dev/ttyUSB0]')
    parser.add_argument('-a', '--action',
                        type=str,
                        help="on/off/toggle")
    parser.add_argument('-p', '--port',
                        type=int,
                        choices=list(range(1, 9)),
                        help="ports to connect/disconnect from 1 to 8.")
    parser.add_argument('--reset',
                        action='store_true',
                        help='Switch off all the Relays.')
    parser.add_argument('--all',
                        action='store_true',
                        help='Switch on all the Relays')
    return parser.parse_args()


if __name__ == "__main__":

    args = command_line_args()

    if not args.device:
        raise RelayError("Please Specify the device.")

    relay = RelayController()
    relay.relay_connect(args.device)

    if args.all:
        relay.relay_switch_all()

    if args.reset:
        relay.relay_reset_all()

    if args.action == "on" and args.port:
        relay.relay_on(args.port)
    if args.action == "off" and args.port:
        relay.relay_off(args.port)
    if args.action == "toggle" and args.port:
        relay.relay_toggle(args.port)

    relay.relay_disconnect()
