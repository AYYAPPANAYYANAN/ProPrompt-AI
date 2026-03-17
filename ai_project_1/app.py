
import streamlit as st
from ai_engine import TextAnalyzer

def main():
    st.title('AI Text Analyzer')
    text = st.text_area('Enter text to analyze', height=200)
    if st.button('Analyze'):
        analyzer = TextAnalyzer()
        summary, sentiment = analyzer.analyze_text(text)
        st.write('Summary:', summary)
        st.write('Sentiment:', sentiment)

if __name__ == '__main__':
    main()
