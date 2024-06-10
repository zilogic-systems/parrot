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
        pass

    @keyword("Bluetooth ON")
    def bluetooth_on(self) -> None:
        # 1. XML-RPC Bluetooth On
        pass

    @keyword("Bluetooth OFF")
    def bluetooth_off(self) -> None:
        pass

    @keyword("Bluetooth Find and Pair Device")
    def bluetooth_find_and_pair_decice(self, device: str) -> bool:
        # 1. XML-RPC Scan
        # 2. XML-RPC Pair
        # 3. Answer Pairing Pop-up using Appium
        pass

    @keyword("Bluetooth Connect Device")
    def bluetooth_connect_device(self, device: str) -> None:
        # Dummy Implementation
        pass

    @keyword("Bluetooth Unpair Device")
    def bluetooth_unpair_device(self, device: str) -> None:
        pass

    @keyword("Bluetooth Wait For Device")
    def bluetooth_wait_for_device(self, device: str, timeout: int) -> None:
        pass
