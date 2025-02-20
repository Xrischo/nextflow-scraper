import argparse
from datetime import datetime
from dateutil import parser as dateparser
import yaml
import requests
from bs4 import BeautifulSoup
import sqlite3

parser = argparse.ArgumentParser(description="Scrape data from sources and store it in a SQLite database.")
parser.add_argument("--config", required=True, help="Path to the YAML configuration file")
parser.add_argument('--overwrite', action='store_true', help='Overwrite existing data in the database')
args = parser.parse_args()

config_file = args.config
overwrite = args.overwrite

# load the yaml config file
with open(config_file, 'r') as file:
    config = yaml.safe_load(file)

# db connection
conn = sqlite3.connect('scraper_data.db')
cursor = conn.cursor()

# headers needed for some websites (like yahoo finance)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# for each source, get the data and store it in the db according to the selectors
for source in config['sources']:
    table_name = source['name']
    url = source['url']
    selectors = source['selectors']
    label = source.get('label', url)

    # send request and parse
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    data_matrix = [] 
    selector_names = list(selectors.keys()) 

    # assigns vertically in a 2d matrix, so column-first
    for column_name, selector in selectors.items():
        elements = soup.select(selector)

        column_data = [] 

        for element in elements:
            # whatever can be parsed to float, parse it
            try:
                value = float(element.get_text(strip=True).replace(',', ''))
            except ValueError:
                # try parsing as date instead (YYYY-MM-DD format)
                try:
                    value = dateparser.parse(element.get_text(strip=True)).date()
                    # Convert to YYYY-MM-DD format
                    value = value.strftime('%Y-%m-%d')
                except ValueError:
                    # leave it as raw text if all fails
                    value = element.get_text(strip=True)
                    print(value)

            column_data.append(value)

        while len(data_matrix) < len(column_data):
            data_matrix.append([None] * len(selectors))

        for row_idx, val in enumerate(column_data):
            data_matrix[row_idx][selector_names.index(column_name)] = val

    # create table
    column_definitions = [f'"{col}" TEXT' for col in selector_names]
    if overwrite:
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}" (
                        source TEXT,
                        label TEXT,
                        {', '.join(column_definitions)},
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    for row in data_matrix:
        values = row

        cursor.execute(f'''INSERT INTO "{table_name}" (source, label, {', '.join(f'"{col}"' for col in selector_names)}) 
                           VALUES (?, ?, {', '.join(['?'] * len(selector_names))})''',
                       (url, label, *values))

        print(f"Inserted row into {table_name}: {values}")

conn.commit()
conn.close()
print("Scraping completed. Data saved to scraper_data.db.")
