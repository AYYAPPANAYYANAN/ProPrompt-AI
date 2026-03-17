
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS

def extract_exif_data(image):
    image = Image.open(image)
    exif_data = image._getexif()
    if exif_data is not None:
        exif_data_dict = {TAGS[k]: v for k, v in exif_data.items() if k in TAGS}
        return exif_data_dict
    else:
        return None

def error_level_analysis(image):
    try:
        # Save the image at 90% quality
        cv2.imwrite('temp.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        # Read the saved image
        saved_image = cv2.imread('temp.jpg')
        # Calculate the absolute difference in pixel arrays
        difference = cv2.absdiff(image, saved_image)
        # Calculate the mean of the absolute difference
        mean_diff = np.mean(difference)
        return mean_diff
    except Exception as e:
        return 'Error occurred: ' + str(e)
