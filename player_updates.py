import pandas as pd
from nba_py.constants import TEAMS
from roster import get_all_rosters, get_team_roster
import os.path, time
from datetime import datetime
from bball_ref_scrape import scrape_stats

DATE = datetime.today().strftime('%m/%d/%Y')
BASE = pd.read_csv("1718_sam_base_projections.csv", dtype=str)

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

