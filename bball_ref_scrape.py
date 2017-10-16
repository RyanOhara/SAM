from urllib.request import urlopen
import pandas as pd
from bs4 import BeautifulSoup

def scrape_stats():
    bball_ref_url = "https://www.basketball-reference.com/leagues/NBA_2018_advanced.html"

    html = urlopen(bball_ref_url)
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find('table', id='advanced_stats')
    adv_df = pd.read_html(table.prettify())[0]
    adv_df = adv_df.drop('Unnamed: 19', axis=1)
    adv_df = adv_df.drop('Unnamed: 24', axis=1)
    adv_df = adv_df.drop('Rk', axis=1)
    #print(adv_df.head())

    adv_df.to_csv("stats_update.csv", index=False)

if __name__ == "__main__":
    scrape_stats()
