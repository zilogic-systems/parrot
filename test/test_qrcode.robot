** Settings **

Library  MockUtil.PyzbarMock
Library  parrot.QRCode
Test Setup  Setup
Test Teardown  Teardown

** Test Cases **

Test QRCode Verify Image Contains Text with Command Success
    Set Qrcode Data  Hello World
    QR Code Verify Image Contains  sample.png  Hello World

Test QRCode Verify Image Contains Text with Command Failure
    Set Qrcode Data  Hello World
    Run Keyword And Expect Error  *  QR Code Verify Image Contains  sample.png  Hello All
