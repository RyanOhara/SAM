import pandas as pd
from nba_py.constants import TEAMS
from roster import get_all_rosters
import os.path, time
from datetime import datetime
from bball_ref_scrape import scrape_stats, scrape_team_stats
from injury_updates import injury_update

DATE = datetime.today().strftime('%m/%d/%Y')
BASE = pd.read_csv("1718_sam_base_projections.csv", dtype=str)
BASE['Playing'] = 1

def update_player_stats():
    stats_date = datetime.strptime(time.ctime(os.path.getmtime('stats_update.csv')), "%a %b %d %H:%M:%S %Y")

    if(DATE!=stats_date.strftime('%m/%d/%Y')):
        scrape_stats()
        STATS = pd.read_csv('stats_update.csv', dtype=str)
    else:
        STATS = pd.read_csv('stats_update.csv', dtype=str)

    player_updates = pd.read_csv("player_updates.csv", dtype=str)

    for index, row in player_updates.iterrows():
        player = row['Player']
        #print(player)
        stats = STATS.loc[STATS['Player'] == player]
        #print(stats)
        base = BASE.loc[BASE['Player'] == player]
        #print(base)

        if not stats.empty and not base.empty:
            mins = float(stats['MP'])
            games = float(stats['G'])
            mpg = mins/games
            obpm = float(stats['OBPM'])
            dbpm = float(stats['DBPM'])
            min_weight = mins/250
            if(min_weight >= 1):
                pm_weight = min_weight
            else:
                pm_weight = games/82

            base_mpg = float(base['MPG'])
            base_opm = float(base['OPM'])
            base_dpm = float(base['DPM'])
            base_weight = 1
            #print(base_mpg)
            #print(base_opm)
            #print(base_dpm)

            up_mpg = (base_mpg * base_weight + mpg * min_weight)/(base_weight + min_weight)
            #print(up_mpg)
            up_opm = (base_opm * base_weight + obpm * pm_weight) / (base_weight + pm_weight)
            #print(up_opm)
            up_dpm = (base_dpm * base_weight + dbpm * pm_weight) / (base_weight + pm_weight)
            #print(up_dpm)

            player_updates.loc[player_updates['Player'].str.contains(player) == True, 'MPG'] = up_mpg
            player_updates.loc[player_updates['Player'].str.contains(player) == True, 'OPM'] = up_opm
            player_updates.loc[player_updates['Player'].str.contains(player) == True, 'DPM'] = up_dpm

    player_updates.to_csv("player_updates.csv", index=False)

def update_rosters():
    roster_date = datetime.strptime(time.ctime(os.path.getmtime('current_roster.csv')), "%a %b %d %H:%M:%S %Y")

    if (DATE != roster_date.strftime('%m/%d/%Y')):
        get_all_rosters()
        ROSTER = pd.read_csv("current_roster.csv", dtype=str)
    else:
        ROSTER = pd.read_csv("current_roster.csv", dtype=str)

    player_updates = pd.read_csv("player_updates.csv", dtype=str)

    for index, row in player_updates.iterrows():
        player = row['Player']#.replace("'", "").replace(' Jr.', '').replace(' III', '').replace('.', '').replace(' II', '')
        roster_row = ROSTER.loc[ROSTER['Player'].str.contains(player) == True]
        team = str(roster_row['Team'].values).replace("'",'').replace("[","").replace("]","")
        #print(player)
        #print(team)

        player_updates.loc[player_updates['Player'].str.contains(player) == True, 'Team'] = team


    player_updates.to_csv("player_updates.csv", index=False)


def update_mins():
    injury_update()
    injuries = pd.read_csv('injury_updates.csv', dtype=str)

    for index, row in injuries.iterrows():
        #print(row['Player'] +", " + row['Expected Return'])
        player = row['Player'].replace("'", "").replace(' Jr.', '').replace(' III', '').replace('.', '').replace(' II', '')
        #print(player)
        status = row['Expected Return']

        if 'out' in status or 'Out' in status:
            BASE.loc[BASE['Player'].replace("'", "").replace(' Jr.', '').replace('.', '').replace(' III', '').replace(' II', '').str.contains(player.replace("'", "").replace(' Jr.', '').replace('.', '').replace(' III', '').replace(' II', '')) == True, 'Playing'] = 0

    BASE.to_csv("player_updates.csv", index=False)

def update_team_stats():
    stats_date = datetime.strptime(time.ctime(os.path.getmtime('team_stats_update.csv')), "%a %b %d %H:%M:%S %Y")

    if (DATE != stats_date.strftime('%m/%d/%Y')):
        scrape_team_stats()
        updates = pd.read_csv('team_stats_update.csv', dtype=str)
    else:
        updates = pd.read_csv('team_stats_update.csv', dtype=str)

    base = pd.read_csv('base_pace_hca.csv', dtype=str)
    avg_rph = base.loc[base['Team'] == "Average"]
    avg_pace = float(avg_rph.iloc[0]['Pace'])
    avg_ortg = float(avg_rph.iloc[0]['Ortg'])
    avg_drtg = float(avg_rph.iloc[0]['Drtg'])

    up_rph = updates.loc[updates['Team'] == "League Average"]
    pace = float(up_rph.iloc[0]['Pace'])
    ortg = float(up_rph.iloc[0]['ORtg'])
    drtg = float(up_rph.iloc[0]['DRtg'])
    up_weight = (float(up_rph.iloc[0]['PW']) + float(up_rph.iloc[0]['PL']))
    avg_weight = 82 - up_weight

    up_pace = (avg_pace * avg_weight + pace * up_weight)/82
    up_ortg = (avg_ortg * avg_weight + ortg * up_weight) / 82
    up_drtg = (avg_drtg * avg_weight + drtg * up_weight) / 82

    base.loc[base['Team'] == "Average", 'Pace'] = up_pace
    base.loc[base['Team'] == "Average", 'Ortg'] = up_ortg
    base.loc[base['Team'] == "Average", 'Drtg'] = up_drtg

    base.to_csv("pace_hca.csv", index=False)

if __name__ == "__main__":
    update_mins()
    update_player_stats()
    update_rosters()
    update_team_stats()
