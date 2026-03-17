
import cv2
import numpy as np
import logging

# Set up logging
logging.basicConfig(filename='detector.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def detect_image(image):
    try:
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create a list to store the detection results
        detection_results = []
        
        # Iterate over the contours
        for contour in contours:
            # Calculate the area of the contour
            area = cv2.contourArea(contour)
            
            # Check if the area is greater than 100
            if area > 100:
                # Calculate the x, y, w, h of the bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Draw a rectangle around the contour
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Append the detection result to the list
                detection_results.append(f'Object detected at ({x}, {y}) with width {w} and height {h}')
        return detection_results
    except Exception as e:
        logging.error(f'Error in detector.py: {e}')
        raise Exception('Error detecting image')
