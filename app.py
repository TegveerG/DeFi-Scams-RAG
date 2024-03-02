### DeFi Scams RAG Streamlit Application
import os
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import gradio as gr
from utils.pinecone_logic import (
  delete_pinecone_index,
  get_pinecone_index,
  upsert_data
)
from utils.data_prep import (
  preprocess_and_concat,
  clean_data_pinecone_schema,
  generate_embeddings_and_add_to_df
)
from utils.openai_logic import (
  get_embeddings,
  create_prompt,
  add_prompt_messages,
  get_chat_completion_messages,
  create_system_prompt
)
import sys

# load environment variables
load_dotenv(find_dotenv())

# Function to extract information
def extract_info(data):
    extracted_info = []
    for match in data['matches']:
        source = match['metadata']['source']
        chain = match['metadata']['chain']
        attack = match['metadata']['attack_method']
        funds = match['metadata']['funds_lost_USD']
        extracted_info.append((source, chain, attack, funds))
    return extracted_info

def main(query):

  print("Start: Main function")

  model_for_openai_embedding="text-embedding-3-small"
  model_for_openai_chat="gpt-3.5-turbo-0125"
  index_name = "defi-scams-rag" # new index for new run of the data
  # query = "This is where I put a question if I'm Testing?"

  ######## delete_pinecone_index(index_name)  # uncomment to delete index
  index, index_created = get_pinecone_index(index_name)

  if index_created:
    df = preprocess_and_concat()
    df = clean_data_pinecone_schema(df)
    df = generate_embeddings_and_add_to_df(df, model_for_openai_embedding)
    upsert_data(index, df)

  embed = get_embeddings(query, model_for_openai_embedding)
  res = index.query(vector=embed.data[0].embedding, top_k=3, include_metadata=True)

  # create system prompt and user prompt for openai chat completion
  messages = []
  system_prompt = create_system_prompt()
  prompt = create_prompt(query, res)
  messages = add_prompt_messages("system", system_prompt , messages)
  messages = add_prompt_messages("user", prompt , messages)
  response = get_chat_completion_messages(messages, model_for_openai_chat)
  print('-' * 80)
  extracted_info = extract_info(res)
  validated_info = []
  for info in extracted_info:
      source, chain, attack, funds = info
      validated_info.append(f"Source: {source}   Chain: {chain}   Attack: {attack}   Funds Lost: {funds}")

  validated_info_str = "\n".join(validated_info)
  final_output = response + "\n\n" + validated_info_str
  print(final_output)
  print('-' * 80)
  return final_output

# if __name__ == "__main__":
#     main()

#create Gradio interface for the chatbot
gr.close_all()
demo = gr.Interface(fn=main,
                    inputs=[gr.Textbox(label="Hello, my name is Teg, your crypto scams specialist, how may I help?", lines=1,placeholder=""),],
                    outputs=[gr.Textbox(label="response", lines=30)],
                    title="DeFi Scams RAG Chatbot",
                    description="A question and answering chatbot with knowledge from Slowmist's Hacked Database and DEFIYIELD's REKT Database. Ask me anything about crypto scams!",
                    allow_flagging="never")
demo.launch(server_name="localhost", server_port=8888)