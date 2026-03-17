
import streamlit as st
from PIL import Image
import cv2
import numpy as np
from processor import process_image

st.title('AI Image Analysis Tool')
st.markdown('<style>body{background-color: #f0f0f0;}</style>', unsafe_allow_html=True)

uploaded_file = st.file_uploader('Choose an image file', type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    try:
        result = process_image(uploaded_file)
        st.write(result)
    except Exception as e:
        st.error(str(e))
