from roster import *
from games import *
from datetime import datetime
from nba_py.constants import TEAMS
import pandas as pd

test_date = datetime(2017, 10, 17, 0, 0, 0).strftime('%m/%d/%Y')
BASE = pd.read_csv("1718_sam_base_projections.csv", dtype=str)
BASE['Playing'] = 1
BASE['Possessions'] = 0
BASE_PM = 106.8

def find_abrv(d, key):
    abrv = ''
    for k, v in d.items():
        if v['name'] in key:
            abrv = k
    return abrv

def project_all():
    games = get_all_games(test_date)

    for index, row in games.iterrows():
        project_game(row['Visitor'], row['Home'])

def project_game(away, home):

    home_abrv = find_abrv(TEAMS, home).lower()
    away_abrv = find_abrv(TEAMS, away).lower()
    print(away_abrv + ' @ ' + home_abrv)

    home_base = BASE.loc[BASE['Team'] == home_abrv]
    away_base = BASE.loc[BASE['Team'] == away_abrv]

    #find teams total projected mins / 5
    home_mins = 0
    for index, row in home_base.iterrows():
        home_mins += float(row['MPG'])*float(row['Playing'])
    home_mins = home_mins/5

    away_mins = 0
    for index, row in away_base.iterrows():
        away_mins += float(row['MPG']) * float(row['Playing'])
    away_mins = away_mins / 5

    # get % of possessions and game +/-'s
    home_opm = BASE_PM
    home_dpm = BASE_PM
    for index, row in home_base.iterrows():
        poss = (float(row['MPG'])/home_mins) * float(row['Playing'])
        home_base.loc[index, 'Possessions'] = poss
        home_opm += poss*float(row['OPM'])
        home_dpm -= poss * float(row['DPM'])
    print(home_opm)
    print(home_dpm)

    away_opm = BASE_PM
    away_dpm = BASE_PM
    for index, row in away_base.iterrows():
        poss = (float(row['MPG'])/away_mins) * float(row['Playing'])
        away_base.loc[index, 'Possessions'] = poss
        away_opm += poss * float(row['OPM'])
        away_dpm -= poss * float(row['DPM'])
    print (away_opm)
    print(away_dpm)


if __name__ == "__main__":
    project_all()





