import streamlit as st
import openai
from PyPDF2 import PdfReader
from docx import Document

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # <-- Put your real key here
openai.api_key = OPENAI_API_KEY

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_txt(file):
    return file.read().decode("utf-8")

def extract_text(files):
    full_text = ""
    for file in files:
        if file.name.endswith(".pdf"):
            full_text += extract_text_from_pdf(file)
        elif file.name.endswith(".docx"):
            full_text += extract_text_from_docx(file)
        elif file.name.endswith(".txt"):
            full_text += extract_text_from_txt(file)
        else:
            full_text += "Unsupported file type: " + file.name
    return full_text

def ask_question(context, question):
    context = context[:4000]  # Limit for token safety
    messages = [
        {"role": "system", "content": "You are a helpful assistant who answers questions based on the context provided."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=512,
        temperature=0.2
    )
    return response.choices[0].message["content"]

st.set_page_config(page_title="Document Chatbot", layout="centered")
st.title("📄 Chat with Your Documents")

uploaded_files = st.file_uploader("Upload your documents (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("Processing documents..."):
        context_text = extract_text(uploaded_files)
    st.success("Documents processed! You can now ask questions.")

    with st.form("question_form"):
        question = st.text_input("Ask a question about your documents:")
        submit = st.form_submit_button("Ask")
        if submit and question:
            with st.spinner("Thinking..."):
                answer = ask_question(context_text, question)
            st.markdown(f"**Answer:** {answer}")
else:
    st.info("Please upload at least one document to begin.")

st.markdown("---")
st.markdown("Made with ❤️ using [Streamlit](https://streamlit.io/) and [OpenAI](https://openai.com/)")
