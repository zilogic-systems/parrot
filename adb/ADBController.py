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
Requirements: robotframework, subprocess
"""
import base64
import subprocess

from robot.api import logger
from robot.api.deco import keyword

class ADBError(Exception):
    """Represents an error in the ADB Controller."""

class ADBController:
    """A library providing keywords for controlling an Android device through ADB.

    == ADB Background ==

    ADB includes the following components:

    - Client - runs on the PC, and sends commands to the server
    - Daemon - runs on the Android device, and processes the commands from the PC
    - Server - runs on the PC, receives commands from the client and sends them
      to the daemon running on the device.

    See https://developer.android.com/tools/adb for more details about ADB, and
    how to install it on your PC. "USB Debugging" should have been enabled on
    the Android device for ADB to work. See
    https://developer.android.com/studio/debug/dev-options#enable for more
    details on how to this for an Android phone.

    == How ADBController Works ==

    ADBController invokes the ADB client running on the PC. And provides two
    types of keywords.

    - Keywords to send commands for execution on the device
    - Keywords to control the device selection

    == Accessing Android Device over USB ==

    If the Android device is connected to the PC via USB. Ensure that developer
    mode is enabled on the Android device. The following keyword sequence can
    then be used to take a screenshot of the Android device.

    | ADB Select Device   | 5A3C000600000001 |
    | ADB Take Screenshot | screenshot.png   |

    The ``ADB Select Device`` keyword causes subsequent commands to be sent to the
    specified Android device. The ``5A3C000600000001`` is the name of the device
    as provided by `adb devices` command output.

    == Accessing Android Device over Network ==

    If the Android device is connected over the network / WiFi. Ensure that
    developer mode is enabled on the Android device. Setup the Android device
    for remote access using the ``adb tcpip 5555`` command. Here ``5555``, is
    the port on which the remote Android daemon should listen for commands. The
    following sequence can be used to take a screenshot of the Android device.

    | ADB IP Connect      | 10.23.0.245:5555    |
    | ADB Take Screenshot | screenshot.png      |

    The `ADB IP Connect` keyword causes the ADB server to connect to a remote
    Android daemon, running at IP ``10.23.0.245:5555``. It also automatically
    selects the device, so that subsequent commands are sent to the Android
    device.

    == Handling Multiple Android Devices ==

    The ADB server is capable of handling multiple Android devices
    simultaneously. The user can switch between the Android devices as shown
    below.

    | ADB IP Connect      | 10.23.0.245:5555 |
    | ADB Select Device   | 5A3C000600000001 |
    | ADB Take Screenshot | dev1.png         |
    | ADB Select Device   | 10.23.0.245:5555 |
    | ADB Take Screenshot | dev2.png         |

    The above keyword sequences first connects to the remote Android device
    ``10.23.0.245:5555``. Selects a local Android device. Takes a screenshot in
    the local Android device. Then selects the remote Android device. Takes a
    screenshot in the remote Android device.

    """

    ROBOT_AUTO_KEYWORDS = False
    ROBOT_LIBRARY_SCOPE = 'TEST'


    def __init__(self, adb_port=5037) -> None:
        """ADBController allows import time configuration.

        If the library is imported without any arguments, then the ADB port is assumed to be 5037.

        | Library | ADBController |

        To use a port other than 5037, specify the ADB port as argument.

        | Library | ADBController | 5000 |
        """

        self.device = None
        self.port = adb_port

    @staticmethod
    def _execute_command(cmd: list, output=False) -> dict:
        """Executes the commands in the terminal as a subprocess.

        - cmd : Commands to be executed.
        - output : True or False. Defaults to ``False``.

        Returns the status of the result if it passes. But if it fails, it returns an error.
        """
        if not output:
            output = subprocess.PIPE
        adb_output = subprocess.run(cmd, stdout=output,
                                    stderr=subprocess.PIPE, text=True, check=False)
        adb_stdout = f"{adb_output.stdout}\n{adb_output.stderr}"
        status = adb_output.returncode == 0

        result = {"success": status,
                  "stdout" : adb_stdout}
        return result

    def _device_connection(self, device: str, connect=True) -> bool:
        """Connects or Disconnects the ADB Device.

        - device : IP Address of the ADB device.
        - connect : True or False. Defaults to ``True``.

        Raises ADB Error when the device connection or disconnection get failed.

        """
        state = "connect" if connect else "disconnect"
        cmd = ["adb", state, device]
        adb_out = self._execute_command(cmd=cmd)
        for error_msg in ['error', 'No route', 'timed out', 'Connection refused']:
            if error_msg in adb_out['stdout']:
                logger.console(adb_out)
                raise ADBError(f"Failed to {state} ADB: {device}: {error_msg}")
        return True

    def _run_server(self, start=True) -> bool:
        """Starts or stops the server.

        - start : True or False. Defaults to ``True``.

        Raises ADBError when the start or stop the server gets failed;
        but it passes when it is executed.

        """
        status = "start-server" if start else "kill-server"
        start_cmd = ["adb", status, "-p", f'{self.port}']
        adb_out = self._execute_command(start_cmd)
        if adb_out['success']:
            return True
        raise ADBError(f"Failed to adb {status}")

    @staticmethod
    def _log_message(msg: str) -> bool:
        """Displays the log message in the HTML file.

        ``msg`` is the message to be printed.

        """
        print(msg)

    @keyword("ADB Shell")
    def adb_shell(self, cmd: list) -> str:
        """Executes the command in the ADB Shell.

        Returns the output of the ADB command.

        *Example*

        | ADB Shell | ['input', 'keyevent', '85'] |
        | ADB Shell | ['input', 'keyevent', '126'] |
        """
        adb_cmd = ["adb", "-s", self.device, "shell", *cmd]
        adb_out = self._execute_command(adb_cmd)
        if adb_out['success']:
            return adb_out['stdout']
        raise ADBError(f"Failed to execute \n{' '.join(cmd)} in {self.device}")

    @keyword("ADB IP Connect")
    def adb_ip_connect(self, device: str) -> None:
        """Establishes a connection with a remote Android device.

        This is required when ADB is connected over WiFi. The IP address of the
        Android device to connect is specified as ``device``. The Android device
        should have already been configured to accept ADB connections over the
        network using the `adb tcpip <port>` command.

        *Example*

        | ADB IP Connect | 10.23.0.245 |
        | ADB IP Connect | 10.42.0.206 |

        """
        self._device_connection(device=device, connect=True)
        cmd = ["adb", "-s", device, "wait-for-device"]
        self._execute_command(cmd=cmd)
        self.device = device
        message = "ADB IP Connect"
        self._log_message(message)
        return

    @keyword("ADB IP Disconnect")
    def adb_ip_disconnect(self, device: str) -> None:
        """Disconnects the specified remote Android device.

        The IP address of the Android device to disconnect is specified as
        ``device``.

        *Example*

        | ADB IP Disconnect | 10.23.0.345 |
        | ADB IP Disconnect | 10.42.0.206 |
        """
        self._device_connection(device=device, connect=False)
        message = "ADB IP Disconnect"
        self._log_message(message)
        return

    @keyword("ADB Disconnect All")
    def adb_disconnect_all(self) -> None:
        """Disconnects all the remote Android devices.

        Disconnects all remote Android devices previously connected using the
        "ADB IP Connect" keyword.
        """
        cmd = ["adb", "disconnect"]
        self._execute_command(cmd)
        message = "ADB Disconnect All"
        self._log_message(message)
        return

    @keyword("ADB Start Server")
    def adb_start_server(self) -> None:
        """Starts the ADB Server.

        The ADB server runs as a background process on the PC / development
        machine. The ADB server communicates with the daemon running in the
        Android device. The commands are issued to the deamon running in the
        Android device through the ADB server.
        """
        self._run_server(start=True)
        message = "ADB Start server"
        self._log_message(message)
        return

    @keyword("ADB Stop Server")
    def adb_stop_server(self) -> None:
        """Stops the ADB Server.

        See "ADB Start Server" for more information.
        """
        self._run_server(start=False)
        message = "ADB Stop server"
        self._log_message(message)
        return

    @keyword("ADB Select Device")
    def adb_select_device(self, device_name: str) -> None:
        """Selects the particular Android Device.

        The ADB server can have access to more than one Android device
        simultaneosuly. One of these devices can be selected to receive
        subsequent ADB commands. The device is specified using the
        ``device_name`` argument.

        The ``device_name`` can be an IP address in case of a remote Android
        device or the device ID string obtained from `adb devices` command.

        *Example*

        | ADB Select Device | 10.32.0.234      |
        | ADB Select Device | 5A3C000600000001 |

        """
        self.device = device_name
        return

    @keyword("ADB Lock Screen")
    def adb_lock_screen(self) -> None:
        """Locks the Android Device screen.

        Remotely locks the Android device's screen, even if it is not currently
        locked. It simulates the action of locking the screen by hitting the
        device's power button.
        """
        cmd = ['input', 'keyevent', '223']
        self.adb_shell(cmd)
        return

    @keyword("ADB Wake Screen")
    def adb_wake_screen(self) -> None:
        """Wakes the screen of the connected Android Device.

        If the display is turned off, this keyword will wakeup the device and
        turn on the display. If the Android device is already awake, this
        keyword will have no effect.

        This will generally be the first keyword in a UI based test case.
        """
        cmd = ['input', 'keyevent', '224']
        self.adb_shell(cmd)
        return

    @keyword("ADB Install APK")
    def adb_install_apk(self, apk: str) -> None:
        """Installs the provided APK.

        The APK to be installed is specified by the ``apk`` argument, which is a
        path to the APK file in the PC. This keyword performs the installation
        process by first pushing the APK from the PC to the Android device.

        *Example*

        | ADB Install APK | /home/user/Downloads/camserve.apk |

        """
        cmd = ['adb', "-s", self.device, 'install', apk]
        self._execute_command(cmd)
        return

    @keyword("ADB Uninstall Package")
    def adb_uninstall_package(self, apk: str) -> None:
        """Uninstalls the specified Android application.

        Uninstall the Android application specified by the ``apk`` argument,
        which is the package name of the application to be uninstalled. It
        searches for and finds the specified package name and uninstalls it only
        if the package is installed on the Android device. If the application is
        not installed the keyword has no effect.

        *Example*

        | ADB Uninstall Package | com.manash.purplle |
        | ADB Uninstall Package | com.rapido.passenger |

        """
        cmd = ['adb', "-s", self.device, 'uninstall', apk]
        self._execute_command(cmd)
        return

    @keyword("ADB Play MP3 File")
    def adb_play_mp3_file(self, mp3file: str) -> None:
        """Plays the specified MP3 file.

        It will play the MP3 file in default Music player in the Android Device.
        ``mp3file`` specifies the path of the MP3 file, within the Android
        device.

        It is not necessary to install a specific music application to play the
        MP3 File.

        *Example*

        | ADB Play MP3 File | /storage/emulated/Downloads/song.mp3 |
        | ADB Play MP3 File | /storage/emulated/0/audio/song.mp3 |

        """
        cmd = ['am', 'start', '-a', 'android.intent.action.VIEW', '-d', f'file:///{mp3file}', '-t', 'audio/mp3']
        self.adb_shell(cmd)
        cmd = ['input', 'keyevent', '126']
        self.adb_shell(cmd)
        return

    @keyword("ADB Play Pause Music File")
    def adb_play_pause_music_file(self) -> None:
        """Plays or pauses the music file.

        Toggles between play or pause by sending a key event to the Android
        Device. The media will either play or pause, depending on whether it is
        currently playing.
        """
        cmd = ['input', 'keyevent', '85']
        self.adb_shell(cmd)
        return

    @keyword("ADB Mute Volume")
    def adb_mute_volume(self) -> None:
        """Mutes the volume.

        Mutes the volume by sending a key event to the Android device.
        """
        cmd = ['input', 'keyevent', '164']
        self.adb_shell(cmd)
        return

    @keyword("ADB Increase Volume")
    def adb_increase_volume(self) -> None:
        """Increases the volume.

        Increases the volume by sending a key event to the Android device.

        NOTE: when `ADB Increse Volume` is executed after the `ADB Mute Volume`,
        it will increase the volume according to the volume before it is muted.
        """
        #
        # FIXME: The keyword definition and the code is contradicting. We should
        # probably have a separate keyword to set the volume to maximum.
        #
        cmd = ['input', 'keyevent', '24']
        for _ in range(15):
            self.adb_shell(cmd)
        return

    @keyword("ADB Reduce Volume")
    def adb_reduce_volume(self) -> None:
        """Decreases the volume.

        Decreases the volume by sending a key event to the Android device.
        """
        cmd = ['input', 'keyevent', '25']
        self.adb_shell(cmd)
        return

    @keyword("ADB Take Screenshot")
    def adb_take_screenshot(self, outputfile: str) -> None:
        """Takes the screenshot of the current screen.

        This keyword captures and stores the current screen in the path
        specified by ``outputfile``. The path specifies a file in the PC.

        *Example*

        | ADB Take Screenshot | screen_capture.png |
        | ADB Take Screenshot | capture_page.png  |

        """
        cmd = ['adb', '-s', self.device, 'exec-out', 'screencap', '-p']
        with open(outputfile, "wb") as img:
            self._execute_command(cmd, output=img) # type: ignore # py
        with open(outputfile, 'rb') as outputimage:
            b64_fbuffer = base64.b64encode(outputimage.read())
        outputfile = f'<img controls src="data:img/png;base64,{b64_fbuffer.decode()}" width = "200"></img>'
        logger.write(outputfile, html=True)
        return

    @keyword("ADB Close Current Application")
    def adb_close_current_application(self) -> None:
        """Closes the current application.

        Identifies the application running the foreground, and stops the
        application. The application running in the foreground is identified
        using `dumpsys activity` command. And application is terminated using
        the `am force-stop` command.

        Closing the application can be achieved by using `ADB Home` keyword,
        but this might not close the app completely depending on its
        implementation.
        """
        cmd = ['dumpsys', 'activity', '|', 'grep', 'top-activity']
        result = self.adb_shell(cmd)
        package_name = result.split("/")[-2].split(":")[-1]
        cmd = ['am', 'force-stop', f'{package_name}']
        self.adb_shell(cmd)
        return

    @keyword("ADB Copy To Android")
    def adb_copy_to_android(self, pc_path: str, android_path: str) -> None:
        """Copies the file from the PC to the Android device.

        Copies the file from the PC, specified by ``pc_path`` to the path in the
        Android device, specified by ``android_path``.

        *Example*

        | ADB Copy To Android | /home/user/Documents/letter.pdf | /storage/emulated/0/Documents/ |
        | ADB Copy To Android | /home/user/song/melody.mp3 | /storage/emulated/0/Music/ |

        """
        cmd = ["adb", "-s", self.device, "push", pc_path, android_path]
        self._execute_command(cmd)
        return

    @keyword("ADB Copy To PC")
    def adb_copy_to_pc(self, android_path: str, pc_path: str) -> None:
        """Copies the file from the Android Device to PC.

        Copies the file from the Android device, specifed by ``android_path`` to
        the path in the PC, specified by ``pc_path``.

        *Example*

        | ADB Copy To PC | /storage/emualated/0/Video/Movie.mp4 | /home/user/Videos/ |
        | ADB Copy To PC | /storage/emualated/0/Music/melody.mp3 | /home/user/song/ |

        """
        cmd = ["adb", "-s", self.device, "pull", android_path, pc_path]
        self._execute_command(cmd)
        return

    @keyword("ADB Open An Application")
    def adb_open_an_application(self, package_name: str) -> None:
        """Opens the specified Application in the Android Device.

        The application specified by `package_name` is opened.

        NOTE: No applications need to be closed before the execution of the
        ``ADB Open an Application``

        *Example*

        | ADB Open an Application | com.vivo.gallery |

        """
        cmd = ['monkey', '-p', f'{package_name}', '-v', '20']
        self.adb_shell(cmd)
        return

    @keyword("ADB Send Tab Key")
    def adb_tab_key(self) -> None:
        """Sends a Tab key.

        Sends a Tab key to the Android device by emulating a key event. This
        keyword can be use for changing focus from on UI element to the next.
        """
        cmd = ["input", "keyevent", "61"]
        self.adb_shell(cmd)
        return

    @keyword("ADB Send Enter Key")
    def adb_enter_key(self) -> None:
        """Sends an Enter key.

        Sends an Enter key to the Android device by emulating a key event.
        """
        cmd = ["input", "keyevent", "66"]
        self.adb_shell(cmd)
        return


    @keyword("ADB Chrome")
    def adb_chrome(self, file_path: str) -> None:
        """Opens the specified file in Chrome on the Android device.

        - ``file_path``: Path to the file in the Android device.

        Chrome may be used to open a variety of file types, including documents,
        audio files, and music. The basis for opening files using Chrome browser
        is that not every Android device has the same installed application.

        NOTE: For opening the file in the Chrome needs appropriate permissions.

        *Example*

        | ADB Chrome | /storage/emulated/0/manual.pdf |
        """
        cmd = ['am', 'start', '-n', 'com.android.chrome/com.google.android.apps.chrome.Main', '-d', f'file:///{file_path}']
        self.adb_shell(cmd)
        return

    @keyword("ADB Get Current Application Package Name")
    def get_current_application_package_name(self) -> str:
        """Gets the package name of current application.

        Gets only the top application package name, even if
        numerous applications are running in the background.

        """
        cmd = ['dumpsys', 'activity', '|', 'grep', 'top-activity']
        result = self.adb_shell(cmd)
        package_name = result.split("/")[-2].split(":")[-1]
        return package_name

    @keyword("ADB Media Play Key")
    def adb_media_play_key(self) -> None:
        """Plays the media.

        It won't accomplish anything if the media is already playing.
        If any media has already been paused, it begins to play.
        """
        cmd = ["input", "keyevent", "126"]
        self.adb_shell(cmd)
        return

    @keyword("ADB Scroll Down")
    def adb_scroll_down(self) -> None:
        """Scrolls the screen downward.

        Swiping down is not advised in every situation unless if you absolutely
        need to scroll down the screen in Android device. If there is no screen
        at all, it won't raise errors.
        """
        cmd = ["input", "swipe", "500", "1000", "300", "300"]
        self.adb_shell(cmd)
        return

    @keyword("ADB Scroll Up")
    def adb_scroll_up(self) -> None:
        """Scrolls the screen upward.

        Swiping up is not advised in every situation unless
        if you absolutely need to scroll up the screen in android device.
        If there is no screen at all, it won't raise errors.
        """
        cmd = ["input", "swipe", "300", "700", "500", "1500"]
        self.adb_shell(cmd)
        return

    @keyword("ADB Pull XML Screen")
    def adb_pull_xml_screen(self, output_file) -> None:
        """Generates an XML file containing the UI hierarchy of current Android screen.

        This is required to dump the UI hierarchy of current Android screen. It
        generates an XML file with a dump of the current UI hierarchy. It will
        store the Screen in the path which is specified to ``output_file``.

        *Example*

        | ADB Pull XML Screen | /home/user/Downloads/ |
        | ADB Pull XML Screen | /home/user/Documents/ |

        """
        cmd = ["uiautomator", "dump", "/sdcard/view.xml"]
        self.adb_shell(cmd)
        self.adb_copy_to_pc("/sdcard/view.xml", output_file)
        return

    @keyword("ADB Send Message")
    def send_message(self, msg: str, phone_number: str) -> None:
        """Sends the message to the specified phone number.

        - ``msg``: Message to be sent.
        - ``phone_number``: Phone number to send the message to.

        *Example*

        | ADB Send Message | Hello | 6379321000 |
        | ADB Send Message | Hi | 9876543210 |
        """
        cmd = ["service", "call", "isms", "5", "i32", "0", "s16", "com.android.mms.service", "s16", "null", "s16", f"{phone_number}", "s16", "null", "s16", f"{msg}"]
        self.adb_shell(cmd)
        return

    @keyword("ADB Home")
    def adb_home(self) -> None:
        """Gets back to Home Screen in the Android Device.

        Use keyevent to transmit a virtual key press that simulates
        pressing the real Home button.
        """
        cmd = ["input", "keyevent", "3"]
        self.adb_shell(cmd)
        return

    @keyword("ADB Swipe Right To Left")
    def adb_swipe_right_to_left(self) -> None:
        """Swipes the Android screen from right to left.

        Swiping right to left is not advised in every situation unless
        if you absolutely need to swipe the screen in android device.
        If there is no screen at all, it won't raise errors.
        """
        cmd = ["input", "swipe", "1000", "500", "300", "300"]
        self.adb_shell(cmd)
        return

    @keyword("ADB Swipe Left To Right")
    def adb_swipe_left_to_right(self) -> None:
        """Swipes the Android screen from left to right.

        Swiping left to right is not advised in every situation unless
        if you absolutely need to swipe the screen in android device.
        If there is no screen at all, it won't raise errors.
        """
        cmd = ["input", "swipe", "700", "300", "1500", "500"]
        self.adb_shell(cmd)
        return
