from urllib.request import urlopen
import pandas as pd
from bs4 import BeautifulSoup

def injury_update():
    feed_url = 'https://www.cbssports.com/nba/injuries/daily'

    html = urlopen(feed_url)
    soup = BeautifulSoup(html, 'lxml')

    #print(soup.prettify())

    tables = soup.findAll('table', {'class':'TableBase-table'})
    #print(table.prettify())
    all_injuries = pd.DataFrame()
    for table in tables:
        injury_df = pd.read_html(table.prettify())[0]#[1:]

        columns = injury_df.columns.str.strip()

        #injury_df = injury_df[1:]
        injury_df.columns = columns
        name = injury_df['Player'].str.split(' ', 2).str
        injury_df['Player'] = name[-1].str.strip()
        #print(injury_df.head())
        all_injuries = all_injuries.append(injury_df, ignore_index=True)

    all_injuries.to_csv('injury_updates.csv', index=False)

if __name__ == "__main__":
    injury_update()

