
import cv2
import numpy as np
from PIL import Image

def read_image(image_path):
    try:
        image = cv2.imread(image_path)
        return image
    except Exception as e:
        raise Exception('Error occurred while reading the image: ' + str(e))

def extract_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        return exif_data
    except Exception as e:
        raise Exception('Error occurred while extracting EXIF data: ' + str(e))

def error_level_analysis(image_path):
    try:
        original_image = read_image(image_path)
        temp_image_path = 'temp.jpg'
        cv2.imwrite(temp_image_path, original_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        temp_image = read_image(temp_image_path)

        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        temp_image = cv2.cvtColor(temp_image, cv2.COLOR_BGR2RGB)

        difference = cv2.absdiff(original_image, temp_image)
        difference = np.sum(difference, axis=2)

        max_diff = np.max(difference)
        avg_diff = np.mean(difference)

        return {
            'max_diff': max_diff,
            'avg_diff': avg_diff,
            'tampering_detected': max_diff > 50
        }
    except Exception as e:
        raise Exception('Error occurred while performing Error Level Analysis: ' + str(e))
