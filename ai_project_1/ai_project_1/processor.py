
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS

def extract_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    if exif_data is not None:
        return {TAGS[k]: v for k, v in exif_data.items() if k in TAGS}
    else:
        return {}

def error_level_analysis(image_path):
    original_image = cv2.imread(image_path)
    height, width, _ = original_image.shape

    # Resave the image at 90% quality
    cv2.imwrite('temp.jpg', original_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    resaved_image = cv2.imread('temp.jpg')

    # Calculate the absolute difference in pixel arrays
    difference = cv2.absdiff(original_image, resaved_image)

    # Convert the difference to grayscale
    gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

    # Apply threshold to segment out the differences
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Return the thresholded image
    return thresh