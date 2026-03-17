
import streamlit as st
import pandas as pd
from db import get_trash_hotspots

def main():
    st.title('Madurai Clean AI')
    trash_hotspots = get_trash_hotspots()
    st.write(trash_hotspots)

if __name__ == '__main__':
    main()
