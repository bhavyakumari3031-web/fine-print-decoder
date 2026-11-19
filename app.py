import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
MODEL = "openai/gpt-oss-120b" # change this if you get a model error

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT = """You are a financial document checker for Indian students and families.
Find the hidden charges and risky clauses in the document below.
For each one:
- Quote the exact line
- Explain in simple Hinglish why it is risky
Finish with an overall risk rating: Low, Medium or High, with a one-line reason.

Document:
"""

st.set_page_config(page_title="Fine-Print Decoder", page_icon="🔍")
st.title("🔍 Fine-Print Decoder")
st.write("Upload or paste a loan, insurance or credit card document. AI finds the hidden traps.")

uploaded = st.file_uploader("Upload a .txt file", type=["txt"])
text = st.text_area("...or paste the document here", height=200)
if uploaded:
    text = uploaded.read().decode("utf-8")

if st.button("Analyse"):
    if not text.strip():
        st.warning("Please upload or paste a document first.")
    else:
        with st.spinner("Reading the fine print..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": PROMPT + text}],
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Something went wrong: {e}")