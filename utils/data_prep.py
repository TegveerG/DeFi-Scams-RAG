import pandas as pd
import json
from tqdm.auto import tqdm
from utils.openai_logic import create_embeddings
import os, sys

def preprocess_and_concat():
    # Read data
    print("Start: Reading data")
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

    # Create an id column
    df['id'] = [i for i in range(1, len(df) + 1)]

    # Output the concatenated dataframe
    df.to_csv('./data/RAG_scams.csv', index=False)
    print("Done: Data read, concatenated, and saved to CSV")

    return df

def clean_data_pinecone_schema(df):
    # Ensure necessary columns are present
    required_columns = {'id', 'Document','Hacked_Target','Funds_Lost','Attack_Method','Source'}
    if not required_columns.issubset(df.columns):
        missing_columns = required_columns - set(df.columns)
        return f"Error: CSV file is missing required columns: {missing_columns}"

    if df.empty:
        return "Error: No valid data found in the CSV file after filtering empty content."

    # Proceed with the function's main logic
    df['id'] = df['id'].astype(str)
    df['metadata'] = df.apply(lambda row: json.dumps({'source': row['Source'],
                            'text': row['Document'], 'chain': row['Hacked_Target'],
                            'attack_method': row['Attack_Method'],
                            'funds_lost_USD': row['Funds_Lost']}), axis=1)
    df = df[['id', 'metadata']]
    # print(df.head())
    print("Done: Dataset retrieved")
    return df


# Function to generate embeddings and add to DataFrame
def generate_embeddings_and_add_to_df(df, model_emb):
    print("Start: Generating embeddings and adding to DataFrame")
    # Check if the DataFrame and the 'metadata' column exist
    if df is None or 'metadata' not in df.columns:
        print("Error: DataFrame is None or missing 'metadata' column.")
        return None


    df['values'] = None

    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        try:
            content = row['metadata']
            meta = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for row {index}: {e}")
            continue  # Skip to the next iteration

        text = meta.get('text', '')
        if not text:
            print(f"Warning: Missing 'text' in metadata for row {index}. Skipping.")
            continue

        try:
            response = create_embeddings(text, model_emb)
            embedding = response   # .data[0].embedding -- Embedding Error? this may be it  # Each in bedding format may be different
            df.at[index, 'values'] = embedding
        except Exception as e:
            print(f"Error generating embedding for row {index}: {e}")

    print("Done: Generating embeddings and adding to DataFrame")
    return df