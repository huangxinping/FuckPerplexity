import streamlit as st
from app import main

st.sidebar.title('FuckPerplexity')

api_key = st.sidebar.text_input('OpenAI API Key:', value='')

question = st.text_input("有何指教？")
if st.sidebar.button('开始请教'):
    st.toast(question, icon='😍')
    answer, convs = main(question, api_key)
    answer = answer.replace("citation:", "")
    result = f"""
{answer}  

### 参考文献：
"""
    for index, conv in enumerate(convs):
        result += f'[{index+1}] [{conv["title"]}]({conv["url"]})    \n'
    
    st.markdown(result)
    
    st.balloons()
    