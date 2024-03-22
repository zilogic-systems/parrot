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
Author: code@zilogic.com
Requirements: robotframework,bs4
"""
import re
import subprocess
from time import sleep as delay

from bs4 import BeautifulSoup
from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.BuiltIn import RobotNotRunningError


class BluetoothError(Exception):
    """Represents an error in the Bluetooth Controller."""


class BluetoothController:
    """A library providing keywords to interact with the Bluetooth interface
    of the DUT using an Android Mobile.

    BluetoothController interacts with the Bluetooth interface of the DUT using
    an Android Mobile device. The Android Mobile device is accessed using the
    ``ADBController`` module.

    This BluetoothController requires additional support from an Android
    application called Bluetooth Pair. The application is available from
    https://bluetooth-pair.en.softonic.com/android The BluetootController was
    tested with version 2.8 of the Bluetooth Pair application. Install the
    application on the Android Mobile device, that will be used for interacting
    with the DUT. Use the ADBController to select the mobile device and open the
    Bluetooth Pair application.

    | ADB Select Device       | 127.0.0.1:5555 |
    | ADB Open An Application | com.waylonhuang.bluetoothpair |

    Bluetooth interface of the Android Mobile device should be turned ON. The
    DUT should be paired with Android Mobile device before making a connection.

    | Bluetooth ON                    |             |
    | Bluetooth Connect Device        | BC8-Android |
    | Bluetooth Wait For Device       | BC8-Android | 20 |

    `Bluetooth ON` keyword turns on the Bluetooth interface of the Android
    Mobile device. `Bluetooth Connect Device` keyword connects the Android
    Mobile device with the DUT. ``BC8-Android`` is name the DUT. The name to
    provided in the keyword, is the Bluetooth device name that shows-up when
    scanning for Bluetooth devices. Note that the DUT should have already been
    paired with the Android mobile device. Currently the BluetoothController
    does not provide an automated mechanism for pairing the device. The
    `Bluetooth Wait For Device` keyword waits for the Bluetooth connection to be
    established, for a timeout of `20` seconds.

    """

    ROBOT_AUTO_KEYWORDS = False
    ROBOT_LIBRARY_SCOPE = 'TEST'

    def __init__(self):
        try:
            self.adb_controller = BuiltIn().get_library_instance('parrot.ADBController')
        except RobotNotRunningError:
            self.adb_controller = None

    @staticmethod
    def _log_message(msg: str):
        """Captures log message.

        - logger.write print in report file.
        - logger.console print in console.

        - msg - Message to be printed.
        """
        logger.write(msg)

    def _click_button(self, x_axis: int, y_axis: int) -> bool:
        """Clicks Button with x and y Coordinates in the mobile app.

        - x_axis - Midpoint of the button width.
        - y_axis - Midpoint of button height.

        *Returns*

        bool - Returns the status of the execution of ADB Commands
        """
        cmd = ['input', 'tap', f"{x_axis}", f"{y_axis}"]
        self.adb_controller.adb_shell(cmd)
        return True

    @staticmethod
    def get_xy_axis(bounds: str) -> tuple:
        """Gets x and y coordinates from the given bounds.

        - bounds - Tuple of lower and upper bounds of x and y coordinates.

        *Returns*

        tuple  - Returns x and y coordinates in tuple format.
        """
        res = re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
        xmin, ymin = int(res.group(1)), int(res.group(2))
        xmax, ymax = int(res.group(3)), int(res.group(4))
        x_axis = (xmin + xmax) / 2
        y_axis = (ymin + ymax) / 2
        return  (x_axis, y_axis)

    @staticmethod
    def _load_screen_data(xml_file: str = "/tmp/view.xml") -> BeautifulSoup:
        """Creates a parse tree for parsed pages that can be used to extract data from XML File.

        - xml_file - Path for xml file. Defaults to ``/tmp/view.xml``.

        *Returns*

        BeautifulSoup - Returns BeautifulSoup Object.
        """
        with open(xml_file, 'r', encoding="utf-8") as f_point:
            page_data = f_point.read()

        parse_tree = BeautifulSoup(page_data, 'xml')
        return parse_tree

    def _find_buttons(self, device: str, parse_tree: BeautifulSoup) -> dict:
        """Finds xpaths from the parse tree.

        - device - Bluetooth Device Name.
        - parse_tree - BeautifulSoup Object.

        *Returns*

        dict - dict of buttons with bounds pair.
        """
        buttons = {}
        text_path = parse_tree.find("node", {"text": f"{device}"})
        if text_path:
            parent = text_path.find_parent().parent()
            parent = list(parent)
            buttons[parent[3]['text']] = parent[3]['bounds']
            if parent[3]['text'] != 'PAIR':
                buttons[parent[4]['text']] = parent[4]['bounds']
            return buttons
        self._log_message(f"{device} Device not found, Scrolling Down")
        return False

    def _turn_bluetooth(self, ble_on: bool = True) -> bool:
        """Turn ON/OFF Bluetooth.

        - ble_on - Turn ON/OFF Bluetooth. Defaults to ``True``.

        *Returns*

        bool - Returns the status of the bluetooth
        """
        status = "ENABLE" if ble_on else "DISABLE"
        cmd = ["am", "start", "-a", f"android.bluetooth.adapter.action.REQUEST_{status}"]
        self.adb_controller.adb_shell(cmd)
        _ = [self.adb_controller.adb_tab_key() for _ in range(2)]
        self.adb_controller.adb_enter_key()
        return True

    def _bluetooth_connection(self, device: str, connection: str) -> bool:
        """Connects to the given bluetooth device.

        - device - Bluetooth Device Name.
        - connection - Connection Type like ``pair/unpair/connect``.

        *Returns*

        bool - Returns the status of the bluetooth connection with device
        """
        self.adb_controller.adb_scroll_up()
        for _ in range(3):
            self.adb_controller.adb_pull_xml_screen("/tmp/view.xml")
            parse_tree = self._load_screen_data()
            buttons = self._find_buttons(device, parse_tree)
            if buttons and connection in buttons:
                bounds = buttons[connection]
                x_axis, y_axis = self.get_xy_axis(bounds)
                self._click_button(x_axis, y_axis)
                break
            self.adb_controller.adb_scroll_down()
        else:
            self._log_message(f"No Device with name {device}")
            return False
        return True

    @keyword("Bluetooth ON")
    def bluetooth_on(self) -> None:
        """Turns on the Bluetooth of the connected Android Device.

        It checks the Bluetooth status of the connected Android Device. If the
        Bluetooth is disabled, it turns it on. If the Bluetooth is already
        enabled, it logs a message indicating that Bluetooth is already enabled.

        *Example*

        | Bluetooth ON |
        """
        cmd = ["settings", "get", "global", "bluetooth_on"]
        bluetooth_status = self.adb_controller.adb_shell(cmd)
        bluetooth_status = int(bluetooth_status)
        if bluetooth_status == 0:
            self._turn_bluetooth()
            self._log_message("Bluetooth Enabled")
        else:
            self._log_message("Bluetooth Already Enabled")
        logger.console("Bluetooth Enabled")
        return

    @keyword("Bluetooth OFF")
    def bluetooth_off(self) -> None:
        """Turns off the Bluetooth of the connected Android Device.

        It checks the Bluetooth status of the connected Android Device. If the
        Bluetooth is enabled, it turns it off. If the Bluetooth is already
        disabled, it logs a message indicating that Bluetooth is already
        disabled.

        *Example*

        | Bluetooth OFF |

        """
        cmd = ["settings", "get", "global", "bluetooth_on"]
        bluetooth_status = self.adb_controller.adb_shell(cmd)
        bluetooth_status = int(bluetooth_status)
        if bluetooth_status:
            self._turn_bluetooth(ble_on=False)
            self._log_message("Bluetooth Disabled")
        else:
            self._log_message("Bluetooth Already Disabled")
        return

    @keyword("Bluetooth Find and Pair Device")
    def bluetooth_find_and_pair_decice(self, device: str) -> bool:
        """Finds and pairs with the specified Bluetooth device.

        ``device`` is the name of the Bluetooth Device / DUT to be paired to the
        Android device.

        Searches the specified Bluetooth device in the list of available
        Bluetooth devices and initiates the pairing process through an Android
        application. It will return the status of the bluetooth connection with
        connected Android device in the ``bool`` type.

        *Example*

        | Bluetooth Find and Pair Device    | BC8-Android |
        """
        return self._bluetooth_connection(device, "PAIR")

    @keyword("Bluetooth Connect Device")
    def bluetooth_connect_device(self, device: str) -> None:
        """Connects the Bluetooth device to the Android device.

        Searches for the specified Bluetooth device which is mentioned as
        ``device`` argument in the list of available devices and initiates the
        connection process through an Android application. Fails if the device
        is not found.


        NOTE: It is required to turn on the Bluetooth of the Android device
        using ``Bluetooth ON``, before connecting the device via Bluetooth.

        *Example*

        | Bluetooth Connect Device  | BC8-Android |

        """
        self._bluetooth_connection(device, "CONNECT")
        return

    @keyword("Bluetooth Unpair Device")
    def bluetooth_unpair_device(self, device: str) -> None:
        """Unpairs the specified Bluetooth device from the connected Android device.

        Searches the specified Bluetooth device which was mentioned as ``device`` argument
        and initiates the unpairing process through an Android application.

        *Example*

        | Bluetooth Unpair Device   | BC8-Android |
        """
        self._bluetooth_connection(device, "UNPAIR")
        return

    @keyword("Bluetooth Wait For Device")
    def bluetooth_wait_for_device(self, device: str, timeout: int) -> None:
        """Waits for the Bluetooth device to be connected to the Android device.

        ``device`` is the name of the Bluetooth Device / DUT being connected to.
        ``timeout`` is the maximum time to wait for the connection to be
        established.

        Passes if the device is connected within the specified ``timeout``,
        fails otherwise.

        *Example*

        | Bluetooth Wait For Device | BC8-Android   | 20 |
        """
        adb_cmd = ["adb", "-s", self.adb_controller.device, "shell", "dumpsys", "bluetooth_manager", "|", "grep", device]
        for _ in range(timeout):
            delay(1)
            try:
                bluetooth_status = subprocess.run(adb_cmd, stdout=subprocess.DEVNULL,
                                                  stderr=subprocess.DEVNULL, check=False)
                if bluetooth_status.returncode == 0:
                    msg = f"Bluetooth Connected: {device}"
                    logger.console(msg)
                    self._log_message(msg)
                    return
            except subprocess.CalledProcessError:
                continue

        raise BluetoothError("Bluetooth Device Not Connected")
