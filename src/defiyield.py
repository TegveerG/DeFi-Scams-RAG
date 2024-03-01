### This script is not compatible with the current version of the API. It is kept here for reference purposes only.
import requests
from bs4 import BeautifulSoup
import json
import re
import os
import pandas as pd
import json
import math

url = "https://api.s.defiyield.app/scam_database?sortField=fundsLost&sort=desc&sortDirection=desc&limit=4000&page=1"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

res_list = response.json()['items'] # items key is pertinent

with open('../data/REKT_unclean.json', 'w') as json_file:
    json.dump(res_list, json_file)

def process_json():
    open_REKTjson = open('../data/REKT_unclean.json')
    load_REKTjson = json.load(open_REKTjson)
    REKT_df = pd.DataFrame(load_REKTjson)
    # Removing spaces at beginning and at the end, if any, from column names
    REKT_df.columns = REKT_df.columns.str.strip()
    REKT_df.drop(columns={'id','technical_issue', 'proof_archive_link', 'logo_link', 'website_link', 'twitter_link', 'our_post_link', 'telegram_link', 'git_hub', 'git_hub_contract_link', 'discord', 'bug_bounty_program_link', 'bug_bounty_program_company', 'audit_code_conf', 'funds_recovered', 'funds_by_chains', 'scam_updates'}, inplace=True)
    #Converting the object data type variables to their respective datatype
    REKT_df['funds_lost'] = REKT_df['funds_lost'].astype('float64')
    REKT_df['funds_returned'] = REKT_df['funds_returned'].astype('float64')
    REKT_df['date'] = pd.to_datetime(REKT_df['date'])
    REKT_df['is_verified_source_code'] = REKT_df['is_verified_source_code'].astype('category')
    REKT_df['is_public_team'] = REKT_df['is_public_team'].astype('category')
    # create time based features for pickup_datetime
    REKT_df['month_of_attack'] = REKT_df.date.dt.month
    REKT_df['day_of_week_of_attack'] = REKT_df.date.dt.dayofweek
    REKT_df['day_of_year_of_attack'] = REKT_df.date.dt.dayofyear
    REKT_df['description'].fillna("", inplace=True)
    #REKT_df_clean = REKT_df.loc[(REKT_df['description'].notnull() & REKT_df['funds_lost']==20000000.0)]

    # An observation that has a high funds lost value but no description must be preserved. So, we convert all of description's missing value to empty string to avoid bs4 errors
    REKT_df['description'].fillna("", inplace=True)
    # running bs4 on description variable
    for index in range(REKT_df.shape[0]):
        soup = BeautifulSoup(REKT_df.iloc[index,1])
        REKT_df.iloc[index,1] = soup.get_text()
    REKT_df['description'] = REKT_df['description'].apply(lambda x: x.replace("Quick Summary", ""))
    # using for loop and jmespath to extract network name
    clean_network=[]

    for i in range(len(REKT_df)):
        clean_network.append(jmespath.search('[].networks.name', REKT_df.scamNetworks[i]))

    REKT_df['scamNetworks']=clean_network
    REKT_df['scam_type_clean']=[d.get('type') for d in REKT_df.scam_type]
    # Removing list brackets and single quotes from the scamNetworks column
    REKT_df['scamNetworks'] = REKT_df['scamNetworks'].str.replace(r'\[|\]|\'' , '', regex=True)

    # Imputing missing values as "Other"
    REKT_df['scamNetworks'].replace('', 'Other', inplace=True)

    # Splitting df by scamNetworks feature that has multiple categorical values for respective rows
    REKT_df['scamNetworks'] = REKT_df['scamNetworks'].str.split(', ')
    REKT_df = REKT_df.explode('scamNetworks').reset_index(drop=True)
    return REKT_df

def main():
    df = process_json()
    if df is not None:
        os.makedirs('../data', exist_ok=True)
        df.to_csv('../data/defiyield.csv', index=False)