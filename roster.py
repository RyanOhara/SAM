import pandas as pd
from nba_py import team
from nba_py.constants import TEAMS
from datetime import datetime

_curr_year = datetime.now().year
if datetime.now().month > 6:
    CURRENT_SEASON = str(_curr_year) + "-" + str(_curr_year + 1)[2:]
else:
    CURRENT_SEASON = str(_curr_year - 1) + "-" + str(_curr_year)[2:]

def get_all_rosters():
    all_players = []

    for t in TEAMS:
        #print(t.lower())
        team_id = TEAMS[t]['id']

        roster_df = team.TeamCommonRoster(team_id, CURRENT_SEASON).roster()
        for p in roster_df['PLAYER']:
            row = [str(p), str(t).lower()]
            all_players.append(row)

    all_players_df = pd.DataFrame(all_players, columns=['Player', 'Team'])
    #print(all_players_df.head())
    all_players_df.to_csv('current_roster.csv', index=False)
    #return all_players_df

def get_team_roster(team_abrv):
    team_players = []

    # print(team_abrv.lower())
    team_id = TEAMS[team_abrv.upper()]['id']

    roster_df = team.TeamCommonRoster(team_id, CURRENT_SEASON).roster()
    for p in roster_df['PLAYER']:
        row = [str(p), str(team_abrv).lower()]
        team_players.append(row)

    team_players_df = pd.DataFrame(team_players, columns=['Player', 'Team'])
    # print(team_players_df.head())
    return team_players_df

if __name__ == "__main__":
    get_all_rosters()
    #all_rosters_df.to_csv('current_roster.csv', index=False)
    #hawks = get_team_roster('atl')
    #print(hawks)
