import streamlit as st
import fitz  # PyMuPDF
import docx
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Extract text from Word
def extract_text_from_docx(file):
    doc = docx.Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

# Chunk text
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# Create FAISS index
def create_faiss_index(chunks):
    embeddings = model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index, chunks

# Streamlit UI
st.title("📄 Document Semantic Search Chatbot")
st.write("Upload a PDF or Word document and ask questions about its content.")

uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx"])

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file format.")
        st.stop()

    st.success("Document uploaded and text extracted successfully.")

    chunks = chunk_text(text)
    index, chunk_texts = create_faiss_index(chunks)

    query = st.text_input("Enter your question or search query")

    if query:
        query_embedding = model.encode([query])
        D, I = index.search(np.array(query_embedding), k=5)
        st.subheader("🔍 Top Relevant Results")
        for i in I[0]:
            st.write(chunk_texts[i])
