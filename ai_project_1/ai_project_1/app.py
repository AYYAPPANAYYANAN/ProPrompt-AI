
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import processor

st.title('AI Image Analysis Tool')
st.markdown('<style>body{background-color: #f0f0f0;}</style>', unsafe_allow_html=True)

uploaded_file = st.file_uploader('Choose an image file', type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    try:
        exif_data = processor.extract_exif_data(uploaded_file)
        st.write('EXIF Data:')
        for tag, value in exif_data.items():
            st.write(f'{tag}: {value}')

        ela_result = processor.error_level_analysis(uploaded_file)
        st.write('Error Level Analysis (ELA) Result:')
        st.image(ela_result, caption='ELA Image', use_column_width=True)

    except Exception as e:
        st.error(f'An error occurred: {e}')