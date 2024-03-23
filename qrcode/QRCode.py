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
Keyword Library provides API for QR Code related tasks.

Author: code@zilogic.com

Requirements: robotframework, pyzbar, pillow
"""

import os.path
import argparse

from pyzbar import pyzbar
from PIL import Image
from robot.api.deco import keyword
from robot.api import logger


@keyword("QR Code Scan Image")
def read_qr_code(image_path: str)-> str:
    """Reads the QR Code Image.

    Decodes and returns the QR code present in the image specified by
    ``image_path``.

    NOTE: If more than one QR code is present returns only one of the decoded codes.
    """
    result = ""
    # Load the image containing the QR code'
    image_path = os.path.join(image_path)
    img = Image.open(image_path)

    # Find and decode any QR codes in the image
    decoded_qr_codes = pyzbar.decode(img)

    # Return the decoded value of the first QR code found (if any)
    if len(decoded_qr_codes) > 0:
        logger.write("QR Code Detected")
        result = decoded_qr_codes[0].data.decode('utf-8')
    else:
        logger.write("QR Code not Detected")
    return result


@keyword("QR Code Verify Image Contains")
def verify_qr_code_text(image_path: str, expected_text: str)-> bool:
    """Verifies the text in the QR Image.

    Decodes the text in the QR image specified by ``image_path``
    and verifies the decoded text with ``expected_text``.

    *Example*

    | Verify Image Contains QRCode | /home/user/Pictures/frame.png | Zilogic Systems |
    """
    image_path = os.path.join(image_path)
    img = Image.open(image_path)

    # Find and decode any QR codes in the image
    decoded_qr_codes = pyzbar.decode(img)

    found = False
    for code in decoded_qr_codes:
        decoded_text = code.data.decode("utf-8")
        logger.write(f"Detected QRCode with text '{decoded_text}'")
        if decoded_text == expected_text:
            found = True

    if not found:
        raise Exception(f"Expected text {expected_text} not present in QR image")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filepath',type = str, required = True, help = "Image Filepath")
    parser.add_argument('-e','--expected-text',type = str, help = "Expected Text")
    args = parser.parse_args()
    filepath = args.filepath
    expected_text = args.expected_text
    if filepath and expected_text:
        result = verify_qr_code_text(filepath, expected_text)
        if result :
            print(f"Verified Text : {expected_text}")
    else:
        text_in_image = read_qr_code(filepath)
        print(f"The text in the image : {text_in_image}")
