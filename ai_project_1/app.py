
import streamlit as st
import streamlit.components.v1 as components
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
    .block-container {background-color: #2f4f7f;}
    /* Set the text color */
    .css-1kyx76e {color: #ffffff;}
    /* Set the button color */
    .css-1ka88d4 {background-color: #4CAF50;}
    /* Set the button hover color */
    .css-1ka88d4:hover {background-color: #3e8e41;}
    </style>
    "",
    unsafe_allow_html=True
)

# Create a Streamlit app
def main():
    try:
        st.title('AI Image Detector')
        st.subheader('Upload an image to detect objects')
        image_file = st.file_uploader('Upload an image', type=['jpg', 'png', 'jpeg'])
        if image_file is not None:
            image = process_image(image_file)
            detection_result = detect_image(image)
            st.write(detection_result)
    except Exception as e:
        logging.error(f'Error in app.py: {e}')
        st.error('An error occurred. Please try again.')

if __name__ == '__main__':
    main()
