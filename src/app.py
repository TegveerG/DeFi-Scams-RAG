### DeFi Scams RAG Application
from dotenv import load_dotenv,find_dotenv
import os
import streamlit as st
from langchain.llms import OpenAI
from langchain.vectorstores import Pinecone
import pinecone


pinecone.init(
    api_key=os.getenv('PINECONE_API_KEY'),
    environment=os.getenv('PINECONE_ENV')
)

load_dotenv(find_dotenv())
  # load all the environment variables
