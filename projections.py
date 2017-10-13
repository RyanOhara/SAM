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
REST = pd.read_csv("nba_rest.csv")
PACE_HCA = pd.read_csv("pace_hca.csv")

def find_abrv(d, key):
    abrv = ''
    for k, v in d.items():
        if v['name'] in key:
            abrv = k
    return abrv

def project_all():
    games = get_all_games(test_date)

    for index, row in games.iterrows():
        project_game(row)

def project_game(game):
    home = game['Home']
    away = game['Visitor']
    home_rest = game['Home Rest']
    away_rest = game['Visitor Rest']

    home_abrv = find_abrv(TEAMS, home).lower()
    away_abrv = find_abrv(TEAMS, away).lower()
    #print(away + ' @ ' + home)

    home_base = BASE.loc[BASE['Team'] == home_abrv]
    away_base = BASE.loc[BASE['Team'] == away_abrv]
    #print(away_base)


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
        home_base.set_value(index, 'Possessions', poss)
        home_opm += poss * float(row['OPM'])
        home_dpm -= poss * float(row['DPM'])
    #print(home_opm)
    #print(home_dpm)

    away_opm = BASE_PM
    away_dpm = BASE_PM
    for index, row in away_base.iterrows():
        poss = (float(row['MPG'])/away_mins) * float(row['Playing'])
        away_base.set_value(index, 'Possessions', poss)
        away_opm += poss * float(row['OPM'])
        away_dpm -= poss * float(row['DPM'])
    #print (away_opm)
    #print(away_dpm)

    home_rph = PACE_HCA.loc[PACE_HCA['Team'] == home]
    home_pace = home_rph.iloc[0]['Pace']
    home_ohca = home_rph.iloc[0]['HCA Off']
    home_dhca = home_rph.iloc[0]['HCA Deff']
    away_rph = PACE_HCA.loc[PACE_HCA['Team'] == away]
    away_pace = away_rph.iloc[0]['Pace']
    away_ohca = away_rph.iloc[0]['HCA Off']
    away_dhca = away_rph.iloc[0]['HCA Deff']
    avg_rph = PACE_HCA.loc[PACE_HCA['Team'] == "Average"]
    avg_pace = avg_rph.iloc[0]['Pace']
    avg_ohca = avg_rph.iloc[0]['HCA Off']
    avg_dhca = avg_rph.iloc[0]['HCA Deff']
    avg_ortg = avg_rph.iloc[0]['Ortg']
    avg_drtg = avg_rph.iloc[0]['Drtg']

    home_rest_vals = REST.loc[REST['Rest'] == home_rest]
    home_rest_ortg = home_rest_vals.iloc[0]['Ortg']
    home_rest_drtg = home_rest_vals.iloc[0]['Drtg']
    home_rest_pace = home_rest_vals.iloc[0]['Pace']

    away_rest_vals = REST.loc[REST['Rest'] == away_rest]
    away_rest_ortg = away_rest_vals.iloc[0]['Ortg']
    away_rest_drtg = away_rest_vals.iloc[0]['Drtg']
    away_rest_pace = away_rest_vals.iloc[0]['Pace']

    home_ortg = home_opm * home_ohca * avg_ohca + home_rest_ortg
    home_drtg = home_dpm * home_dhca * avg_dhca +home_rest_drtg
    home_pace = home_pace + home_rest_pace

    away_ortg = away_opm + away_rest_ortg
    away_drtg = away_dpm + away_rest_drtg
    away_pace = away_pace + away_rest_pace

    game_pace = (home_pace / avg_pace) * (away_pace / avg_pace) * avg_pace
    home_score = (home_ortg / avg_ortg) * (away_drtg / avg_drtg) * avg_ortg * (game_pace/100)
    away_score = (away_ortg / avg_ortg) * (home_drtg / avg_drtg) * avg_ortg * (game_pace / 100)
    total = home_score + away_score

    projection = pd.DataFrame(data=[[home, home_score, away, away_score, total]], columns=['Home', 'Home Score', 'Away', 'Away Score', 'Total'])

    print(projection)


if __name__ == "__main__":
    project_all()





