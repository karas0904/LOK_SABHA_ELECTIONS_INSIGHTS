import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def scrape_eci_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: Status code {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='table')

    if not table:
        raise Exception("Could not find the results table on the page")

    data = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) == 4:
            party = cols[0].text.strip()
            won = int(cols[1].text.strip())
            leading = int(cols[2].text.strip())
            total = int(cols[3].text.strip())
            party_link = cols[1].find('a')['href']
            data.append({
                'Party': party,
                'Won': won,
                'Leading': leading,
                'Total': total,
                'Link': party_link
            })

    return pd.DataFrame(data)
