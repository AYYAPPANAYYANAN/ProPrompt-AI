
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import processor

st.title('AI Image Analysis Tool')
st.subheader('Upload an image to analyze')
uploaded_file = st.file_uploader('Choose a file', type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    try:
        exif_data = processor.extract_exif_data(uploaded_file)
        ela_result = processor.error_level_analysis(img)
        st.write('EXIF Data:')
        st.write(exif_data)
        st.write('ELA Result:')
        st.write(ela_result)
    except Exception as e:
        st.error('Error occurred: ' + str(e))
