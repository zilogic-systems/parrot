"""
A library providing keywords for OCR(Optical Character Recognition).
"""
from PIL import Image
import pytesseract
import numpy as np
from pytesseract import Output
from robot.api.deco import keyword
import argparse

#
# FIXME: Add following keywords
#
# Get Coordinate of Text  <filename>  <text>
#

@keyword("Verify Image Contains Text")
def verify_image_contains_text(file_name: str, expected_text: str) -> bool:
    """Verifies image contains the expected text.
    
    Reads and return text from the image is specified by
    ``file_name`` and verifies the text with ``expected_text``.
    
    *Example*

    | Verify Image Contains Text | /home/user/Downloads/picture.png | Free as a bird |
    
    """
    actual_text = image_to_text(file_name)
    if expected_text.lower() not in actual_text.lower():
        raise Exception(f"Expected text {expected_text} not present in image")

@keyword("Get Text From Image")
def image_to_text(file_name: str) -> list:
    """Reads all the text from the image.

    Reads and return text from the image is specified by
    ``file_name``.

    NOTE : Image should be clear and without noise.

    *Example*

    | Get Text From Image | /home/user/Downloads/picture.png |
    """
    img = np.array(Image.open(file_name))
    data = pytesseract.image_to_data(img, output_type=Output.DICT)
    text_value = data['text']
    final_value = ' '.join(text_value)
    return final_value

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filepath', type = str, required = True, help = "Image Filepath")
    parser.add_argument('-e','--expected-text', type = str, help = 'Expected text')
    args = parser.parse_args()
    file_path = args.filepath
    expected_text = args.expected_text
    if file_path and expected_text:
        if not verify_image_contains_text(file_path, expected_text):
            print(f"Expected text {expected_text} present in image")
    else:
        text = image_to_text(file_path)
        print("Image Contains : ",text)
