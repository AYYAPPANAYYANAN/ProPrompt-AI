
import cv2
import numpy as np
import logging

# Set up logging
logging.basicConfig(filename='processor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_image(image):
    try:
        # Read the image
        image_array = np.frombuffer(image.read(), np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Resize the image
        resized_image = cv2.resize(image, (256, 256))
        
        # Apply noise reduction
        blurred_image = cv2.GaussianBlur(resized_image, (5, 5), 0)
        
        # Log the successful image processing
        logging.info('Image processing successful')
        return blurred_image
    except Exception as e:
        # Log the error
        logging.error(f'Error processing image: {e}')
        raise Exception('Error processing image')
