# Retrieval Augmented Generation Engine using LangChain, Streamlit, & Pinecone

[Access application on Streamlit Cloud Platform](https://)

![Demo](misc/demo.gif)

## Overview

The Retrieval Augmented Engine (RAG) is a powerful tool for document retrieval, summarization, and interactive question-answering. This project utilizes LangChain, Streamlit, and Pinecone to provide a seamless web application for chatting with a chatbot about DeFi (Decentralized Finance) scams.

Two open-source databases, including [DEFIYIELD](https://de.fi/rekt-database) and [SlowMist](https://hacked.slowmist.io/), are used to train the chatbot. Specifically, one of the scraped fields that describes the summary of an attack is used to generate vector embeddings for the documents. The vector embeddings are then stored in Pinecone, a vector database, for efficient retrieval and question-answering tasks.

The project's front-end is built using Streamlit, a popular Python library for building web applications.

## Features

- **Streamlit Web App**: The project is built using Streamlit, providing an intuitive and interactive web interface for users.
- **Input Fields**: Users can input essential credentials like OpenAI API key and Pinecone API key through dedicated input fields.
- **Text Splitting**: The uploaded PDFs are split into smaller text chunks, ensuring compatibility with models with token limits.
- **Vector Embeddings**: The text chunks are converted into vector embeddings, making it easier to perform retrieval and question-answering tasks.
- **Flexible Vector Storage**: You can choose to store vector embeddings either in Pinecone or a local vector store, providing flexibility and control.
- **Interactive Conversations**: Users can engage in interactive conversations with the documents, asking questions and receiving answers. The chat history is preserved for reference.

## Prerequisites

Before running the project, make sure you have the following prerequisites:

- Python 3.7+
- LangChain
- Streamlit
- Pinecone
- An OpenAI API key

## Usage

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/TegveerG/DeFi-Scams-RAG.git

   cd DeFi-Scams-RAG
   ```

2. Install the required dependencies by running:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:

   ```bash
   streamlit run src/app.py
   ```

4. Access the app by opening a web browser and navigating to the provided URL.

5. Input your OpenAI API key, Pinecone API key, Pinecone environment, and Pinecone index name in the respective fields. You can provide them either in the sidebar of the application or place them in the **secrets.toml** file in the [.streamlit directory](src/.streamlit)

6. Ask the chatbot about DeFi scams.

7. Click the "Submit Query" button to process the documents and generate vector embeddings.

8. Engage in interactive conversations with the text by typing your questions in the chat input box.

## Contributors

[Tegveer Ghura](https://github.com/TegveerG)

## Contact

If you have any questions, suggestions, or would like to discuss this project further, feel free to get in touch with me:

- [Email](mailto:tegu99@gmail.com)
- [LinkedIn](https://www.linkedin.com/in/tegveerg/)

I'm open to collaboration and would be happy to connect!
