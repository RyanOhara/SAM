from urllib.request import urlopen, HTTPError, URLError
import requests
import pandas as pd

#base = pd.read_csv("1718_sam_base_projections.csv", dtype=str)
base = pd.read_csv("current_roster.csv", dtype=str)
carmelo_page = "https://projects.fivethirtyeight.com/carmelo/"

for index, row in base.iterrows():
    player = row['Player']
    p = player.replace(" ", "-")
    p = p.replace("'", "")
    p = p.replace(".", "")
    player_page = carmelo_page + p.lower() + '.json'

    try:
        url = urlopen(player_page)

        r = requests.get(player_page)
        projs = r.json()

        opm = float(projs['player_stats']['opm_2018'])
        dpm = float(projs['player_stats']['dpm_2018'])

        base.loc[index, 'OPM'] = opm
        base.loc[index, 'DPM'] = dpm

        print('Player: ' + player + ' OPM: ' + str(opm) + ' DPM: ' + str(dpm))

    except HTTPError as err:
        if err.code == 404:
            print ("Page not found for player " + player)
        else:
            print ("Something happened on player " + player + "! Error code", err.code)
    except URLError as err:
        print ("Some url error happened on player " + player + "! Error code:", err.reason)


base.to_csv('roster_projections.csv', index=False)