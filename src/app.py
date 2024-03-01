### DeFi Scams RAG Streamlit Application
from dotenv import load_dotenv
import os
import streamlit as st
from langchain.document_loaders import DataFrameLoader
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser
import numpy as np
import pandas as pd

def preprocess_and_concat():
    # Read data
    slowmist_df = pd.read_csv('./data/slowmist.csv')
    defiyield_df = pd.read_csv('./data/defiyield.csv')

    # Convert the date columns to datetime
    slowmist_df['Date'] = pd.to_datetime(slowmist_df['Date'])
    defiyield_df['date'] = pd.to_datetime(defiyield_df['date'])

    # Format the date columns
    slowmist_df['Date'] = slowmist_df['Date'].dt.strftime('%B %d, %Y')
    defiyield_df['date'] = defiyield_df['date'].dt.strftime('%B %d, %Y')

    # Concatenate Date and Description columns
    slowmist_df['Document'] = slowmist_df['Date'] + ' - ' + slowmist_df['Description']
    defiyield_df['Document'] = defiyield_df['date'] + ' - ' + defiyield_df['description']

    # Drop NaN values
    slowmist_df.dropna(inplace=True)
    defiyield_df.dropna(inplace=True)

    # Keep relevant columns
    slowmist_df = slowmist_df[['Document', 'Hacked_Target', 'Funds_Lost', 'Attack_Method', 'Source']]
    defiyield_df = defiyield_df[['Document', 'project_name', 'funds_lost', 'scam_type', 'proof_link']]

    # Rename columns
    defiyield_df.rename(columns={'project_name': 'Hacked_Target', 'funds_lost': 'Funds_Lost', 'scam_type': 'Attack_Method', 'proof_link': 'Source'}, inplace=True)

    # Concatenate the two dataframes
    df = pd.concat([slowmist_df, defiyield_df], ignore_index=True)

    # Output the dataframe
    df.to_csv('./data/RAG_scams.csv', index=False)

def main():
  # Load the environment variables
  load_dotenv()

  # Call the function
  preprocess_and_concat()

  # Read the concatenated data
  df = pd.read_csv('./data/RAG_scams.csv')

  # Init langchain components
  DOCUMENT = 'Document'
  df_loader = DataFrameLoader(df, page_content_column=DOCUMENT)

  df_document = df_loader.load()

  text_splitter = CharacterTextSplitter(chunk_size=250, chunk_overlap=10)
  texts = text_splitter.split_documents(df_document)

  embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

  # Create the Chroma index
  chromadb_index = Chroma.from_documents(
    texts, embedding_function, persist_directory='./input'
  )

  retriever = chromadb_index.as_retriever()

  model_id = "databricks/dolly-v2-3b"
  task="text-generation"

  hf_llm = HuggingFacePipeline.from_model_id(
    model_id=model_id,
    task=task,
    model_kwargs={
        "max_length": 1024
    },
    pipeline_kwargs={
        "repetition_penalty": 1.1
    }
  )

  document_qa = RetrievalQA.from_chain_type(
    llm=hf_llm, chain_type="stuff", retriever=retriever
  )


  st.title("SlowMist and DEFIYIELD Crypto Scams RAG Application")

  st.write("This is a Streamlit app that uses the SlowMist and DEFIYIELD APIs to display the latest crypto scams.")

  user_question = st.text_input("Ask a question:")
  if user_question:
    response = document_qa.invoke(user_question)

    # Display the response
    st.write("Answer:")
    st.write(response)

if __name__ == "__main__":
    main()