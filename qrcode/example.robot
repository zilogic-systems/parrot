*** Settings ***

Library                 parrot.QRCode

*** Test Cases ***

Verify QR Code
    QR Code Verify Image Contains  sample.png  https://zilogic.com
