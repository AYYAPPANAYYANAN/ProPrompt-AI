
import streamlit as st
import cv2
import numpy as np
from processor import process_image
from detector import detect_image
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for Cyber theme
st.markdown(
    """
    <style>
    /* Remove the footer */
    footer {visibility: hidden;}
    /* Remove the main menu */
    .main-menu {visibility: hidden;}
    /* Set the background color */
    .block-container {background-color: #2f2f2f;}
    /* Set the text color */
    .css-1kyx76e {color: #ffffff;}
    /* Set the button color */
    .css-1cpxqw2 {background-color: #4CAF50;}
    </style>
    "",
    unsafe_allow_html=True
)

# Set up the Streamlit UI
st.title('AI Image Detector')
st.subheader('Upload an image to detect objects')

# Create a file uploader
uploaded_image = st.file_uploader('Choose an image', type=['jpg', 'png', 'jpeg'])

if uploaded_image is not None:
    try:
        # Process the image
        processed_image = process_image(uploaded_image)
        
        # Detect objects in the image
        detection_result = detect_image(processed_image)
        
        # Display the detection result
        st.write(detection_result)
        
        # Display the processed image
        st.image(processed_image)
        
        # Log the successful detection
        logging.info('Image detection successful')
    except Exception as e:
        # Log the error
        logging.error(f'Error detecting image: {e}')
        st.error('Error detecting image')
