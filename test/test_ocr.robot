** Settings **

Library  MockUtil.TesseractMock
Library  parrot.OCRLib
Test Setup  Setup
Test Teardown  Teardown

** Test Cases **

Test OCR Verify Image Contains Text with Command Success
       Set Image Data  Hello World
       Verify Image Contains Text  sample.jpg  Hello world

Test OCR Verify Image Contains Text with Command Failure
       Set Image Data  Hello World
       Run keyword And Expect Error  *  Verify Image Contains Text  sample.jpg  Have a good day
