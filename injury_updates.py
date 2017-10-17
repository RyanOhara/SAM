from urllib.request import urlopen
import pandas as pd
from bs4 import BeautifulSoup

def injury_update():
    feed_url = 'https://www.cbssports.com/nba/injuries/daily'

    html = urlopen(feed_url)
    soup = BeautifulSoup(html, 'lxml')

    table = soup.find('table', {'class':'data'})
    #print(table.prettify())

    injury_df = pd.read_html(table.prettify())[0][1:]
    columns = injury_df.iloc[0]
    injury_df = injury_df[1:]
    injury_df.columns = columns
    #print(injury_df)

    injury_df.to_csv('injury_updates.csv', index=False)

if __name__ == "__main__":
    injury_update()

