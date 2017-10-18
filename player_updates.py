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

    if(DATE!=stats_date.strftime('%m/%d/%Y')):
        scrape_stats()
        STATS = pd.read_csv('stats_update.csv', dtype=str)
    else:
        STATS = pd.read_csv('stats_update.csv', dtype=str)

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


#### Not working
def update_rosters():
    #get_all_rosters()
    ROSTER = pd.read_csv("current_roster.csv", dtype=str)
    player_updates = pd.read_csv("player_updates.csv", dtype=str)

    for index, row in player_updates[:10].iterrows():
        player = row['Player'].replace("'", "").replace(' Jr.', '').replace(' III', '').replace('.', '').replace(' II', '')
        roster_row = ROSTER.loc[ROSTER['Player'].str.contains(player) == True]
        team = roster_row['Team']

        if not roster_row.empty:
            print(player)
            print(team)
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

        if 'out' in status:
            BASE.loc[BASE['Player'].replace("'", "").replace(' Jr.', '').replace('.', '').replace(' III', '').replace(' II', '').str.contains(player.replace("'", "").replace(' Jr.', '').replace('.', '').replace(' III', '').replace(' II', '')) == True, 'Playing'] = 0

    BASE.to_csv("player_updates.csv", index=False)

if __name__ == "__main__":
    update_mins()
    #update_rosters()
