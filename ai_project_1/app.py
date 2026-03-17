
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import processor

st.title('AI Image Analysis Tool')
st.subheader('Upload an image file')
uploaded_file = st.file_uploader('Choose a file')

if uploaded_file is not None:
    file_details = {
        'filename': uploaded_file.name,
        'filetype': uploaded_file.type,
        'filesize': uploaded_file.size
    }
    st.write(file_details)

    try:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        ela_result = processor.error_level_analysis(uploaded_file)
        st.write('Error Level Analysis Result:')
        st.write(ela_result)
    except Exception as e:
        st.error('Error occurred while processing the image')
        st.write(str(e))
