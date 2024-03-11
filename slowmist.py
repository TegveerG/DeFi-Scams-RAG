import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import time

def get_last_page_number():
    base_url = "https://hacked.slowmist.io"

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        records = soup.find('ul', class_='pagination')

        if records:
            pages = records.find_all('li')
            for page in pages:
                last_page_tag = page.find('a')
                if last_page_tag and 'Page' in last_page_tag.text:
                    match = re.search(r'Page \d+ of (\d+)', last_page_tag.text)
                    if match:
                        last_page_number = int(match.group(1))
                        return last_page_number

    except requests.RequestException as e:
        print(f"Error during request: {e}")
    except IndexError as e:
        print(f"Error accessing list index: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None

def scrape_data():
    last_page_number = get_last_page_number()

    if last_page_number is None:
        print("Failed to get the last page number.")
        return None

    base_url = 'https://hacked.slowmist.io/?c=&page='
    num_pages = last_page_number

    time_list = []
    hacked_target_list = []
    description_list = []
    funds_lost_list = []
    attack_method_list = []
    source_list = []

    for page in range(1, num_pages+1):
        url = base_url + str(page)
        time.sleep(0.1)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        records = soup.find('div', class_='case-content')

        if records:
            attacks = records.find_all('li')
            for attack in attacks:
                attack_time = attack.find('span', class_='time').text.strip()
                hacked_target = attack.find('h3').text.strip().replace("Hacked target: ", "")
                description = attack.find('p').text.strip().replace("Description of the event: ", "")
                funds_lost = re.sub(r'[^\d-]+', '', attack.find('em').find_next('span').text.strip())
                attack_method = attack.find('em').find_next('span').find_next('span').text.strip().replace("Attack method: ", "")
                source = attack.find('a', text='View Reference Sources')
                source = source['href'] if source else ''

                time_list.append(attack_time)
                hacked_target_list.append(hacked_target)
                description_list.append(description)
                funds_lost_list.append(funds_lost)
                attack_method_list.append(attack_method)
                source_list.append(source)

    data = {
        'Date': time_list,
        'Hacked_Target': hacked_target_list,
        'Description': description_list,
        'Funds_Lost': funds_lost_list,
        'Attack_Method': attack_method_list,
        'Source': source_list
    }

    df = pd.DataFrame(data)
    return df

def main():
    df = scrape_data()
    if df is not None:
        os.makedirs('./data', exist_ok=True)
        df.to_csv('./data/slowmist.csv', index=False)

if __name__ == "__main__":
    main()
