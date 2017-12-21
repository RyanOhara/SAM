from games import *
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup
from stat_updates import *
from datetime import datetime, timedelta

DATE = datetime.today().strftime('%m/%d/%Y')

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
                if 'row-group' not in tr['class'] and nba == 1:
                    date = tr.find('span', {'id': 'period1'}).text
                    if month + '/' + day in date or ':' in date or '\n' == date:
                        tmv = tr.find('span', {'id': 'tmv'}).text.split('-')[0]
                        tmh = tr.find('span', {'id': 'tmh'}).text.split('-')[0]
                        all_odds = tr.find_all('td', {'class': 'sportsbook'})
                        consensus = all_odds[-1].find_all('span')
                        if (len(consensus) > 1):
                            top = str(consensus[0].text).strip()
                            away_line = None
                            home_line = None
                            total = None
                            if top[0] != '-' and top.count("-") == 1:
                                top = top.split("-")[0].replace('o', '').replace('u', '')
                            else:
                                top = "-".join(top.split("-", 2)[:2]).replace('o', '').replace('u', '')

                            bottom = str(consensus[1].text).strip()
                            if bottom[0] != '-' and bottom.count("-") == 1:
                                bottom = bottom.split("-")[0].replace('o', '').replace('u', '')
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

                            if away_line is not None or home_line is not None or total is not None:
                                game = pd.DataFrame(data=[[tmv, away_line, tmh, home_line, total]], columns=columns)
                                #print(game)
                                odds_df = odds_df.append(game, ignore_index=True)
                                #print(tmv + ' ' + str(away_line) + ' @ ' + tmh + ' ' + str(home_line) + ' total: ' + str(total))
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
    projections = pd.DataFrame(columns=['Date', 'Home', 'Home Score', 'Away', 'Away Score', 'Proj. Home Spread', 'Proj. Away Spread', 'Proj. Total', 'Home Spread', 'Away Spread', 'Total', 'Home Spread Diff', 'Away Spread Diff', 'Total Diff', 'Spread Bet', 'Total Bet'])

    for index, row in games.iterrows():
        if not spreads.empty:
            lines = spreads.loc[spreads['Home'] == row['Home']]
        else:
            lines = pd.DataFrame(data=[[row['Visitor'], 0, row['Home'], 0, 0]], columns=['Away', 'Away Spread', 'Home', 'Home Spread', 'Total'])

        if not lines.empty:
            proj = project_game(row, lines)
            projections = projections.append(proj, ignore_index=True)

    return projections

def project_game(game, line):
    UPDATES = pd.read_csv("player_updates.csv", dtype=str)
    UPDATES['Possessions'] = 0
    REST = pd.read_csv("nba_rest.csv")
    PACE_HCA = pd.read_csv("pace_hca.csv")

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

    avg_rph = PACE_HCA.loc[PACE_HCA['Team'] == "League Average"]
    avg_pace = avg_rph.iloc[0]['Pace']
    avg_ohca = avg_rph.iloc[0]['HCA Off']
    avg_dhca = avg_rph.iloc[0]['HCA Deff']
    avg_ortg = avg_rph.iloc[0]['Ortg']
    avg_drtg = avg_rph.iloc[0]['Drtg']

    # get % of possessions and game +/-'s
    home_opm = avg_ortg
    home_dpm = avg_drtg
    for index, row in home_base.iterrows():
        poss = (float(row['MPG'])/home_mins) * float(row['Playing'])
        home_base

        home_opm += poss * float(row['OPM'])
        home_dpm -= poss * float(row['DPM'])
    #print(home_opm)
    #print(home_dpm)

    away_opm = avg_ortg
    away_dpm = avg_drtg
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

    home_rest_vals = REST.loc[REST['Rest'] == home_rest]
    home_rest_ortg = home_rest_vals.iloc[0]['Ortg']
    home_rest_drtg = home_rest_vals.iloc[0]['Drtg']
    home_rest_pace = home_rest_vals.iloc[0]['Pace']

    away_rest_vals = REST.loc[REST['Rest'] == away_rest]
    away_rest_ortg = away_rest_vals.iloc[0]['Ortg']
    away_rest_drtg = away_rest_vals.iloc[0]['Drtg']
    away_rest_pace = away_rest_vals.iloc[0]['Pace']

    home_ortg = home_opm * home_ohca * avg_ohca + home_rest_ortg
    home_drtg = home_dpm * home_dhca * avg_dhca + home_rest_drtg
    home_pace = home_pace + home_rest_pace

    away_ortg = away_opm + away_rest_ortg
    away_drtg = away_dpm + away_rest_drtg
    away_pace = away_pace + away_rest_pace

    game_pace = (home_pace / avg_pace) * (away_pace / avg_pace) * avg_pace
    home_score = (home_ortg / avg_ortg) * (away_drtg / avg_drtg) * avg_ortg * (game_pace / 100)
    away_score = (away_ortg / avg_ortg) * (home_drtg / avg_drtg) * avg_ortg * (game_pace / 100)
    home_spread = away_score - home_score
    away_spread = home_score - away_score
    total = home_score + away_score

    home_spread_diff = float(line['Home Spread']) - home_spread
    away_spread_diff = float(line['Away Spread']) - away_spread
    total_diff = total - float(line['Total'])

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
        total_bet = 'No Bet'

    projection = pd.DataFrame(data=[[str(DATE), home, home_score, away, away_score, home_spread, away_spread, total, float(line['Home Spread']), float(line['Away Spread']), float(line['Total']), home_spread_diff, away_spread_diff, total_diff, spread_bet, total_bet]], columns=['Date', 'Home', 'Home Score', 'Away', 'Away Score', 'Proj. Home Spread', 'Proj. Away Spread', 'Proj. Total', 'Home Spread', 'Away Spread', 'Total', 'Home Spread Diff', 'Away Spread Diff', 'Total Diff', 'Spread Bet', 'Total Bet'])

    #print(projection)
    return projection

def update_results():
    today = pd.read_csv('todays_projections.csv')
    today['Act. Home Score'] = 0
    today['Act. Away Score'] = 0
    today['Act. Home Diff'] = 0
    today['Act. Away Diff'] = 0
    today['Act. Total'] = 0
    today['Spread Result'] = ''
    today['Total Result'] = ''
    #print(today)


    url = "https://www.basketball-reference.com/leagues/NBA_2018_games-"
    yesterday = datetime.now() - timedelta(days=1)
    month = yesterday.strftime("%B")
    url = url + month.lower() +'.html'

    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')

    table = soup.find('table', {'id': 'schedule'})

    scores_df = pd.read_html(table.prettify())[0]
    #print(today['Date'][0])
    scores_df['Date'] = pd.to_datetime(scores_df['Date'])
    #print(scores_df['Date'].dt.strftime('%m/%d/%Y'))
    scores = scores_df[scores_df['Date'].dt.strftime('%m/%d/%Y') == today['Date'][0]]
    #print(scores)
    for index, row in today.iterrows():
        score = scores[scores['Home/Neutral'] == row['Home']]
        home = score['Home/Neutral'].item()
        away = score['Visitor/Neutral'].item()
        home_score = float(score['PTS.1'])
        away_score = float(score['PTS'])
        home_diff = home_score - away_score
        away_diff = away_score - home_score
        act_total = away_score + home_score
        total = row['Total']
        home_spread = row['Home Spread']
        away_spread = row['Away Spread']
        total_bet = row['Total Bet']
        spread_bet = row['Spread Bet']
        today.loc[index, 'Act. Home Score'] = home_score
        today.loc[index, 'Act. Away Score'] = away_score
        today.loc[index, 'Act. Home Diff'] = home_diff
        today.loc[index, 'Act. Away Diff'] = away_diff
        today.loc[index, 'Act. Total'] = act_total

        if spread_bet == home:
            if (-1*home_diff > home_spread):
                today.loc[index, 'Spread Result'] = 'Loss'
            elif (-1*home_diff < home_spread):
                today.loc[index, 'Spread Result'] = 'Win'
            else:
                today.loc[index, 'Spread Result'] = 'Push'
        elif spread_bet == away:
            if (-1*away_diff > away_spread):
                today.loc[index, 'Spread Result'] = 'Loss'
            elif (-1*away_diff < away_spread):
                today.loc[index, 'Spread Result'] = 'Win'
            else:
                today.loc[index, 'Spread Result'] = 'Push'
        else:
            today.loc[index, 'Spread Result'] = 'No Bet'

        if act_total > total:
            if total_bet == 'Over':
                today.loc[index, 'Total Result'] = 'Win'
            elif total_bet == 'Under':
                today.loc[index, 'Total Result'] = 'Loss'
            else:
                today.loc[index, 'Total Result'] = 'No Bet'
        elif act_total < total:
            if total_bet == 'Over':
                today.loc[index, 'Total Result'] = 'Loss'
            elif total_bet == 'Under':
                today.loc[index, 'Total Result'] = 'Win'
            else:
                today.loc[index, 'Total Result'] = 'No Bet'
        else:
            today.loc[index, 'Total Result'] = 'Push'

        #print(row)

    print(today)
    today.to_csv('all_projections.csv', mode='a', index=False, header=False)

def parse_results():
    results = pd.read_csv('all_projections.csv')

    spread_win0 = 0
    spread_win2 = 0
    spread_win4 = 0
    spread_win6 = 0
    spread_loss0 = 0
    spread_loss2 = 0
    spread_loss4 = 0
    spread_loss6 = 0
    spread_push0 = 0
    spread_push2 = 0
    spread_push4 = 0
    spread_push6 = 0

    total_win0 = 0
    total_win2 = 0
    total_win4 = 0
    total_win6 = 0
    total_loss0 = 0
    total_loss2 = 0
    total_loss4 = 0
    total_loss6 = 0
    total_push0 = 0
    total_push2 = 0
    total_push4 = 0
    total_push6 = 0

    for index, row in results.iterrows():
        spread_diff = float(row['Home Spread Diff'])
        total_diff = float(row['Total Diff'])
        spread_result = row['Spread Result']
        total_result = row['Total Result']

        if abs(spread_diff) >= 6 and spread_result == 'Win':
            spread_win6 += 1
        elif abs(spread_diff) >= 6 and spread_result == 'Loss':
            spread_loss6 += 1
        elif abs(spread_diff) >= 6 and spread_result == 'Push':
            spread_push6 += 1
        elif abs(spread_diff) >= 4 and spread_result == 'Win':
            spread_win4 += 1
        elif abs(spread_diff) >= 4 and spread_result == 'Loss':
            spread_loss4 += 1
        elif abs(spread_diff) >= 4 and spread_result == 'Push':
            spread_push4 += 1
        elif abs(spread_diff) >= 2 and spread_result == 'Win':
            spread_win2 += 1
        elif abs(spread_diff) >= 2 and spread_result == 'Loss':
            spread_loss2 += 1
        elif abs(spread_diff) >= 2 and spread_result == 'Push':
            spread_push2 += 1
        elif abs(spread_diff) >= 0 and spread_result == 'Win':
            spread_win0 += 1
        elif abs(spread_diff) >= 0 and spread_result == 'Loss':
            spread_loss0 += 1
        elif abs(spread_diff) >= 0 and spread_result == 'Push':
            spread_push0 += 1

        if abs(total_diff) >= 6 and total_result == 'Win':
            total_win6 += 1
        elif abs(total_diff) >= 6 and total_result == 'Loss':
            total_loss6 += 1
        elif abs(total_diff) >= 6 and total_result == 'Push':
            total_push6 += 1
        elif abs(total_diff) >= 4 and total_result == 'Win':
            total_win4 += 1
        elif abs(total_diff) >= 4 and total_result == 'Loss':
            total_loss4 += 1
        elif abs(total_diff) >= 4 and total_result == 'Push':
            total_push4 += 1
        elif abs(total_diff) >= 2 and total_result == 'Win':
            total_win2 += 1
        elif abs(total_diff) >= 2 and total_result == 'Loss':
            total_loss2 += 1
        elif abs(total_diff) >= 2 and total_result == 'Push':
            total_push2 += 1
        elif abs(total_diff) >= 0 and total_result == 'Win':
            total_win0 += 1
        elif abs(total_diff) >= 0 and total_result == 'Loss':
            total_loss0 += 1
        elif abs(total_diff) >= 0 and total_result == 'Push':
            total_push0 += 1

    print("Spread 6+: " + str(spread_win6) + '-' + str(spread_loss6) + '-' + str(spread_push6) + ' ' + str(spread_win6/(spread_loss6 + spread_win6)*100) + '%')
    print("Spread 4-6: " + str(spread_win4) + '-' + str(spread_loss4) + '-' + str(spread_push4) + ' ' + str(spread_win4/(spread_loss4 + spread_win4)*100) + '%')
    print("Spread 2-4: " + str(spread_win2) + '-' + str(spread_loss2) + '-' + str(spread_push2) + ' ' + str(spread_win2/(spread_loss2 + spread_win2)*100) + '%')
    print("Spread 0-2: " + str(spread_win0) + '-' + str(spread_loss0) + '-' + str(spread_push0) + ' ' + str(spread_win0/(spread_loss0 + spread_win0)*100) + '%')
    print("Spread all: " + str(spread_win0 + spread_win2 + spread_win4 + spread_win6) + '-'
          + str(spread_loss0 + spread_loss2 + spread_loss4 + spread_loss6) + '-'
          + str(spread_push0 + spread_push2 + spread_push4 + spread_push6) + ' ' + str((spread_win0 + spread_win2 + spread_win4 + spread_win6)/((spread_loss0 + spread_loss2 + spread_loss4 + spread_loss6) + (spread_win0 + spread_win2 + spread_win4 + spread_win6))*100) + '%')

    print('\n')
    print("Total 6+: " + str(total_win6) + '-' + str(total_loss6) + '-' + str(total_push6) + ' ' + str(total_win6/(total_loss6 + total_win6)*100) + '%')
    print("Total 4-6: " + str(total_win4) + '-' + str(total_loss4) + '-' + str(total_push4) + ' ' + str(total_win4/(total_loss4 + total_win4)*100) + '%')
    print("Total 2-4: " + str(total_win2) + '-' + str(total_loss2) + '-' + str(total_push2) + ' ' + str(total_win2/(total_loss2 + total_win2)*100) + '%')
    print("Total 0-2: " + str(total_win0) + '-' + str(total_loss0) + '-' + str(total_push0) + ' ' + str(total_win0/(total_loss0 + total_win0)*100) + '%')
    print("Total all: " + str(total_win0 + total_win2 + total_win4 + total_win6) + '-'
          + str(total_loss0 + total_loss2 + total_loss4 + total_loss6) + '-'
          + str(total_push0 + total_push2 + total_push4 + total_push6)  + ' ' + str((total_win0 + total_win2 + total_win4 + total_win6)/((total_loss0 + total_loss2 + total_loss4 + total_loss6) + (total_win0 + total_win2 + total_win4 + total_win6))*100) + '%')

    print('\n')
    print("Combined 6+: " + str(total_win6 + spread_win6) + '-' + str(total_loss6 + spread_loss6) + '-' + str(total_push6 + spread_push6) + ' ' + str((total_win6 + spread_win6)/(total_loss6 + spread_loss6 + total_win6 + spread_win6)*100) + '%')
    print("Combined 4-6: " + str(total_win4 + spread_win4) + '-' + str(total_loss4 + spread_loss4) + '-' + str(total_push4 + spread_push4) + ' ' + str((total_win4 + spread_win4)/(total_loss4 + spread_loss4 + total_win4 + spread_win4)*100) + '%')
    print("Combined 2-4: " + str(total_win2 + spread_win2) + '-' + str(total_loss2 + spread_loss2) + '-' + str(total_push2 + spread_push2) + ' ' + str((total_win2 + spread_win2)/(total_loss2 + spread_loss2 + total_win2 + spread_win2)*100) + '%')
    print("Combined 0-2: " + str(total_win0 + spread_win0) + '-' + str(total_loss0 + spread_loss0) + '-' + str(total_push0 + spread_push0) + ' ' + str((total_win0 + spread_win0)/(total_loss0 + spread_loss0 + total_win0 + spread_win0)*100) + '%')
    print("Combined all: " + str(total_win0 + total_win2 + total_win4 + total_win6 + spread_win0 + spread_win2 + spread_win4 + spread_win6) + '-'
          + str(total_loss0 + total_loss2 + total_loss4 + total_loss6 + spread_loss0 + spread_loss2 + spread_loss4 + spread_loss6) + '-'
          + str(total_push0 + total_push2 + total_push4 + total_push6 + spread_push0 + spread_push2 + spread_push4 + spread_push6)  + ' '
          + str((total_win0 + total_win2 + total_win4 + total_win6 + spread_win0 + spread_win2 + spread_win4 + spread_win6)/((total_loss0 + total_loss2 + total_loss4 + total_loss6 + spread_loss0 + spread_loss2 + spread_loss4 + spread_loss6) + (total_win0 + total_win2 + total_win4 + total_win6 + spread_win0 + spread_win2 + spread_win4 + spread_win6))*100) + '%')
    print('\n')


if __name__ == "__main__":
    today_proj = pd.read_csv('todays_projections.csv')

    if not today_proj.empty:
        prev = today_proj['Date'][0]
        if (DATE != prev):
            update_results()

    parse_results()
    update_injuries()
    update_player_stats()
    update_rosters()
    update_team_stats()
    projections = project_all(DATE)
    print(projections)
    projections.to_csv('todays_projections.csv', index=False)





