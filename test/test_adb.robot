** Settings **

Library    MockUtil.SubprocessMock
Library    parrot.ADBController

Test Setup    Setup
Test Teardown    Teardown

** Test Cases **
Test ADB Start Server Success
    Set ADB Response    0
    ADB Start Server
    Verify ADB Command    ['adb', 'start-server', '-p', '5037']

Test ADB Start Server Failure
    Set ADB Response    1
    Run Keyword And Expect Error    *    ADB Start Server

Test ADB Stop Server Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Stop Server
    Verify ADB Command    ['adb', 'kill-server', '-p', '5037']

Test ADB Stop Server Failure
    Set ADB Response    1
    Run Keyword And Expect Error    *    ADB Stop Server

Test ADB Device Connection Success
    ADB IP Connect    10.42.0.206
    Set ADB Response    0
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'wait-for-device']

Test ADB Shell Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'wait-for-device']

Test Take ScreenShot Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Take Screenshot    image.png
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'exec-out', 'screencap', '-p']

Test ADB Disconnect All Success
    Set ADB Response    0
    ADB IP Connect  10.42.0.206
    ADB Disconnect All
    Verify ADB Command    ['adb', 'disconnect']

Test ADB Lock Screen Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Lock Screen
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '223']

Test ADB Wake Screen Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Wake Screen
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '224']

Test ADB Install APK Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Install APK    camserver.apk
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'install', 'camserver.apk']

Test ADB Uninstall APK Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Uninstall Package    com.rapido.passenger
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'uninstall', 'com.rapido.passenger']

Test ADB Play MP3 File Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Play MP3 File    song.mp3
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', 'file://song.mp3', '-t', 'audio/mp3']

Test ADB Play Pause Music File Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Play Pause Music File
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '85']

Test ADB Mute Volume Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Mute Volume
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '164']

Test ADB Increase Volume Success
    Set ADB Response    0
    ADB IP Connect  10.42.0.206
    ADB Increase Volume
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '24']

Test ADB Reduce Volume Success
    Set ADB Response    0
    ADB IP Connect  10.42.0.206
    ADB Reduce Volume
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '25']

Test ADB Close Current Application Success
    Set ADB Response    0    Proc#0:fgT/A/TOPLCMNt:028240:com.android.vending/u0a161(top-activity)
    ADB IP Connect    10.42.0.206
    ADB Close Current Application
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'dumpsys', 'activity', '|', 'grep', 'top-activity']

Test ADB Copy To Android Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Copy To Android    image.png    storage/emulated/0/Download
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'push', 'image.png', 'storage/emulated/0/Download']

Test ADB Copy To PC Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Copy To PC    storage/emulated/0/Download    image.png
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'pull', 'storage/emulated/0/Download', 'image.png']

Test ADB Open An Application Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Open An Application    app.camserver.com
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'monkey', '-p', 'app.camserver.com', '-v', '20']

Test ADB Send Tab Key Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Send Tab Key
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '61']

Test ADB Send Enter Key Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Send Enter Key
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '66']

Test ADB Chrome Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Chrome    song.mp3
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'am', 'start', '-n', 'com.android.chrome/com.google.android.apps.chrome.Main', '-d', 'file://song.mp3']

Test ADB Get Current Application Package Name Success
    Set ADB Response    0    Proc#0:fgT/A/TOPLCMNt:028240:com.android.vending/u0a161(top-activity)
    ADB IP Connect    10.42.0.206
    ADB Get Current Application Package Name
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'dumpsys', 'activity', '|', 'grep', 'top-activity']

Test ADB Media Play Key Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Media Play Key
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '126']

Test ADB Scroll Down Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Scroll Down
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', "input", "swipe", "500", "1000", "300", "300"]

Test ADB Scroll Up Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Scroll Up
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', "input", "swipe", "300", "700", "500", "1500"]

Test ADB Pull XML Screen Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Pull XML Screen    /home/user/
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', "uiautomator", "dump", "/sdcard/view.xml"]

Test ADB Send Message Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Send Message    Hello    9988776655
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', "service", "call", "isms", "5", "i32", "0", "s16", "com.android.mms.service", "s16", "null", "s16", "9988776655", "s16", "null", "s16", "Hello"]

Test ADB Home Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Home
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', 'input', 'keyevent', '3']

Test ADB Swipe Right To Left Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Swipe Right To Left
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', "input", "swipe", "1000", "500", "300", "300"]

Test ADB Swipe Left To Right Success
    Set ADB Response    0
    ADB IP Connect    10.42.0.206
    ADB Swipe Left To Right
    Verify ADB Command    ['adb', '-s', '10.42.0.206', 'shell', "input", "swipe", "700", "300", "1500", "500"]

