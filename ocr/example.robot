*** Settings ***

Library    parrot.OCRLib

*** Test Cases ***

Simple OCR Test
	Verify Image Contains Text    sample.jpg    keep it simple
