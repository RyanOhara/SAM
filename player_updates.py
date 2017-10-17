import pandas as pd
from nba_py.constants import TEAMS
from roster import get_all_rosters, get_team_roster
import os.path, time
from datetime import datetime
from bball_ref_scrape import scrape_stats
from injury_updates import injury_update

DATE = datetime.today().strftime('%m/%d/%Y')
BASE = pd.read_csv("1718_sam_base_projections.csv", dtype=str)
BASE['Playing'] = 1

def update_pm():
    stats_date = datetime.strptime(time.ctime(os.path.getmtime('stats_update.csv')), "%a %b %d %H:%M:%S %Y")
    roster_date = datetime.strptime(time.ctime(os.path.getmtime('current_roster.csv')), "%a %b %d %H:%M:%S %Y")

    if(DATE!=stats_date.strftime('%m/%d/%Y')):
        scrape_stats()
        STATS = pd.read_csv('stats_update.csv', dtype=str)
    else:
        STATS = pd.read_csv('stats_update.csv', dtype=str)

    if(DATE!=roster_date.strftime('%m/%d/%Y')):
        get_all_rosters()
        ROSTER = pd.read_csv("current_roster.csv", dtype=str)
    else:
        ROSTER = pd.read_csv("current_roster.csv", dtype=str)


    team_roster = get_team_roster('atl')
    #print(team_roster)
    base_team = BASE.loc[BASE['Team'] == 'atl']
    #print(base_team)
    for index, row in team_roster.iterrows():
        player = row['Player']
        print(player)
        update_stats = STATS.loc[STATS['Player'] == player]
        print(update_stats)

    # for team in TEAMS:
    #    print(team)

def update_mins():
    injury_date = datetime.strptime(time.ctime(os.path.getmtime('injury_updates.csv')), "%a %b %d %H:%M:%S %Y")

    if (DATE != injury_date.strftime('%m/%d/%Y')):
        injury_update()
        injuries = pd.read_csv('injury_updates.csv', dtype=str)
    else:
        injuries = pd.read_csv('injury_updates.csv', dtype=str)

    for index, row in injuries.iterrows():
        #print(row['Player'] +", " + row['Expected Return'])
        player = row['Player']
        status = row['Expected Return']
        player_base = BASE.loc[BASE['Player'].replace("'", "").replace('.', '').replace(' II', '').replace(' III', '').replace(' Jr.', '') == player.replace("'", "").replace('.', '').replace(' II', '').replace(' III', '').replace(' Jr.', '')]

        #print(player_base['Player'])
        if 'out' in status:
            #print(player_base['Player'])
            BASE.loc[BASE['Player'].replace("'", "").replace('.', '').replace(' II', '').replace(' III', '').replace(' Jr.', '') == player.replace("'", "").replace('.', '').replace(' II', '').replace(' III', '').replace(' Jr.', ''), 'Playing'] = 0

    BASE.to_csv("player_updates.csv", index=False)

if __name__ == "__main__":
    update_mins()
