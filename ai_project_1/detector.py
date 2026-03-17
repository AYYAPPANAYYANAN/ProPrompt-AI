
import cv2
import numpy as np
import logging

# Set up logging
logging.basicConfig(filename='detector.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def detect_image(image):
    try:
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create a list to store the detection results
        detection_results = []
        
        # Iterate over the contours
        for contour in contours:
            # Calculate the area of the contour
            area = cv2.contourArea(contour)
            
            # Check if the area is greater than 100
            if area > 100:
                # Draw a bounding rectangle around the contour
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Append the detection result to the list
                detection_results.append(f'Object detected at ({x}, {y}) with width {w} and height {h}')
        
        # Log the successful detection
        logging.info('Object detection successful')
        return detection_results
    except Exception as e:
        # Log the error
        logging.error(f'Error detecting objects: {e}')
        raise Exception('Error detecting objects')
