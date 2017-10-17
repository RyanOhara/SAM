from roster import *
from games import *
from datetime import datetime
from nba_py.constants import TEAMS
import pandas as pd
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup

DATE = datetime.today().strftime('%m/%d/%Y')
UPDATES = pd.read_csv("player_updates.csv", dtype=str)
#BASE = pd.read_csv("1718_sam_base_projections.csv", dtype=str)
#BASE['Playing'] = 1
UPDATES['Possessions'] = 0
BASE_PM = 106.8
REST = pd.read_csv("nba_rest.csv")
PACE_HCA = pd.read_csv("pace_hca.csv")

def find_abrv(d, key):
    abrv = ''
    for k, v in d.items():
        if v['name'] in key:
            abrv = k
    return abrv

def get_odds(date):
    day = date[3:5]
    month = date[0:2]
    columns = ['Away', 'Away Spread', 'Home', 'Home Spread', 'Total']
    odds_df = pd.DataFrame(columns=columns)

    try:
        si_page = urlopen("http://free.sportsinsights.com/free-odds/free-odds-frame.aspx?MaxColumns=100&LineOption=Combined&EventOption=undefined&SortBy=undefined&Previous=&Yesterday=&ShowPercents=&SportGroup=sg2")
        si_soup = BeautifulSoup(si_page, "html.parser")
        trs = si_soup.find_all('tr')
        nba = 0

        for tr in trs:
            try:
                if 'row-group' in tr['class']:
                    if "NBA" in tr.find('td', {'class': 'team'}).text:
                        nba = 1
                    else:
                        nba = 0
                if 'row-odd' in tr['class'] and nba == 1:
                    date = tr.find('span', {'id': 'period1'}).text
                    if month + '/' + day in date:
                        tmv = tr.find('span', {'id': 'tmv'}).text.split('-')[0]
                        tmh = tr.find('span', {'id': 'tmh'}).text.split('-')[0]
                        all_odds = tr.find_all('td', {'class': 'sportsbook'})
                        consensus = all_odds[-1].find_all('span')
                        if (len(consensus) > 1):
                            top = str(consensus[0].text).strip()
                            if top[0] != '-' and top.count("-") == 1:
                                top = top.split("-")[0].replace('o', '').replace('u', '')
                            # elif top.count("-") == 1:
                            #    top = top.split("-")[0].replace('o', '').replace('u', '')
                            else:
                                top = "-".join(top.split("-", 2)[:1]).replace('o', '').replace('u', '')

                            bottom = str(consensus[1].text).strip()
                            if bottom[0] != '-' and bottom.count("-") == 1:
                                bottom = bottom.split("-")[0].replace('o', '').replace('u', '')
                            # elif bottom.count("-") == 1:
                            #    bottom = bottom.split("-")[0].replace('o', '').replace('u', '')
                            else:
                                bottom = "-".join(bottom.split("-", 2)[:2]).replace('o', '').replace('u', '')

                            if (float(top) >= 100):
                                total = float(top)
                                away_line = -1 * float(bottom)
                                home_line = float(bottom)
                            elif (float(bottom) >= 100):
                                total = float(bottom)
                                away_line = float(top)
                                home_line = -1 * float(top)
                            game = pd.DataFrame(data=[[tmv, away_line, tmh, home_line, total]], columns=columns)
                            # print(game)
                            odds_df = odds_df.append(game, ignore_index=True)
                            # print(tmv + ' ' + str(away_line) + ' @ ' + tmh + ' ' + str(home_line) + ' total: ' + str(total))
            except KeyError:
                pass
    except HTTPError as err:
        if err.code == 404:
            print ("Page not found for spreads")
        elif err.code == 403:
            print ("Page for spreads blocked")
        else:
            print ("Something happened getting the spreads! Error code", err.code)

    #print(odds_df)
    return odds_df

def project_all(date):
    games = get_all_games(date)
    spreads = get_odds(date)
    projections = pd.DataFrame(columns=['Home', 'Home Score', 'Away', 'Away Score', 'Proj. Home Spread', 'Proj. Away Spread', 'Proj. Total', 'Home Spread', 'Away Spread', 'Total', 'Home Spread Diff', 'Away Spread Diff', 'Total Diff', 'Spread Bet', 'Total Bet'])

    for index, row in games.iterrows():
        if not spreads.empty:
            lines = spreads.loc[spreads['Home'] == row['Home']]
        else:
            lines = pd.DataFrame(data=[[row['Visitor'], 0, row['Home'], 0, 0]], columns=['Away', 'Away Spread', 'Home', 'Home Spread', 'Total'])
        proj = project_game(row, lines)
        proj = proj.set_index('Date')
        projections = projections.append(proj)

    return projections

def project_game(game, line):
    home = game['Home']
    away = game['Visitor']
    home_rest = game['Home Rest']
    away_rest = game['Visitor Rest']

    home_abrv = find_abrv(TEAMS, home).lower()
    away_abrv = find_abrv(TEAMS, away).lower()
    #print(away + ' @ ' + home)

    home_base = UPDATES.loc[UPDATES['Team'] == home_abrv]
    away_base = UPDATES.loc[UPDATES['Team'] == away_abrv]
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
    home_spread = away_score - home_score
    away_spread = home_score - away_score
    total = home_score + away_score

    home_spread_diff = float(line['Home Spread']) - home_spread
    away_spread_diff = float(line['Away Spread']) - away_spread
    total_diff = float(line['Total']) - total

    if home_spread_diff > 0:
        spread_bet = home
    elif away_spread_diff > 0:
        spread_bet =  away
    else:
        spread_bet = 'No Bet'

    if total_diff > 0:
        total_bet = 'Over'
    elif total_diff < 0:
        total_bet =  'Under'
    else:
        spread_bet = 'No Bet'

    projection = pd.DataFrame(data=[[str(DATE), home, home_score, away, away_score, home_spread, away_spread, total, float(line['Home Spread']), float(line['Away Spread']), float(line['Total']), home_spread_diff, away_spread_diff, total_diff, spread_bet, total_bet]], columns=['Date', 'Home', 'Home Score', 'Away', 'Away Score', 'Proj. Home Spread', 'Proj. Away Spread', 'Proj. Total', 'Home Spread', 'Away Spread', 'Total', 'Home Spread Diff', 'Away Spread Diff', 'Total Diff', 'Spread Bet', 'Total Bet'])

    #print(projection)
    return projection


if __name__ == "__main__":
    projections = project_all(DATE)
    print(projections)
    projections.to_csv('game_projections.csv')
    #get_odds(DATE)





