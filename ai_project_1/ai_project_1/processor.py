
import cv2
import numpy as np
from PIL import Image
import io

def process_image(image_file):
    image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
    exif_data = image_file

    # Read EXIF data
    try:
        image_pil = Image.open(io.BytesIO(exif_data.read()))
        exif_info = image_pil._getexif()
        if exif_info:
            for tag, value in exif_info.items():
                print(f'DECODED TAG: {tag} - VALUE: {value}')
    except Exception as e:
        print(f'Error reading EXIF data: {str(e)}')

    # Perform Error Level Analysis (ELA)
    temp_file = 'temp.jpg'
    cv2.imwrite(temp_file, image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    recompressed_image = cv2.imread(temp_file)

    # Calculate absolute difference in pixel arrays
    difference = cv2.absdiff(image, recompressed_image)
    gray_diff = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray_diff], [0], None, [256], [0, 256])

    # Calculate ELA metrics
    ela_mean = np.mean(hist)
    ela_std = np.std(hist)
    ela_max = np.max(hist)

    # Detect tampering based on ELA metrics
    if ela_mean > 20 and ela_std > 10 and ela_max > 50:
        return 'Image may be tampered with.'
    else:
        return 'Image appears to be authentic.'
