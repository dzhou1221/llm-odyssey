from dotenv import load_dotenv
import os

from pypdf import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
import streamlit as st

load_dotenv()
st.title("Q&A Chatbot")
st.write("Upload a PDF file and ask questions")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# load the pdf file and extrac the text
if uploaded_file:
  doc_reader = PdfReader(uploaded_file)
  
  raw_text = ""
  for i, page in enumerate(doc_reader.pages):
    text = page.extract_text()
    if text:
      raw_text += text
      
  # st.text(raw_text)
  
  # split the text into chunks
  text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
  )
  texts = text_splitter.split_text(raw_text)
  
  # download embeddings
  embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
  # create the document search
  docsearch = FAISS.from_texts(texts, embeddings)
  
  qa = ConversationalRetrievalChain.from_llm(
    llm=OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")),
    retriever=docsearch.as_retriever(),
    return_source_documents=True,
  )
  
  # initialize chat history list
  chat_history = []
  
  # get the user's query
  query = st.text_input("Ask a question about the uploaded document:")
  
  generate_button = st.button("Gnerate Answer")
  
  if generate_button and query:
    with st.spinner("Generating answer ...."):
      result = qa({
        "question": query,
        "chat_history": chat_history
      })

      answer = result['answer']
      source_documents = result['source_documents']
      
      # combine the answer and source_documents into a single response
      response = {
        "answer": answer,
        "source_documents": source_documents
      }
      st.wrtie("response", response)