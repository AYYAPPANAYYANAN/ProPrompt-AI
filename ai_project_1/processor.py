
import cv2
import numpy as np
import logging

# Set up logging
logging.basicConfig(filename='processor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_image(image_file):
    try:
        # Read the image
        image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
        
        # Resize the image
        image = cv2.resize(image, (512, 512))
        
        # Apply noise reduction
        image = cv2.GaussianBlur(image, (5, 5), 0)
        
        return image
    except Exception as e:
        logging.error(f'Error in processor.py: {e}')
        raise Exception('Error processing image')
