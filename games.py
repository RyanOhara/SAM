import pandas as pd
from datetime import datetime
from nba_py.constants import TEAMS
DATE = datetime.today().strftime('%m/%d/%Y')


def get_all_games(today=DATE):
    sched = pd.read_csv('1718_schedule.csv')
    sched['Date'] = pd.to_datetime(sched['Date'], format='%m/%d/%Y')

    todays_games = sched.loc[sched['Date'] == today]
    #print(todays_games)
    return todays_games

def get_team_game(team_abrv, today=DATE):
    sched = pd.read_csv('1718_schedule.csv')
    sched['Date'] = pd.to_datetime(sched['Date'], format='%m/%d/%Y')
    todays_games = sched.loc[sched['Date'] == today]

    team_city = TEAMS[team_abrv.upper()]['city']
    team_name = TEAMS[team_abrv.upper()]['name']
    team = team_city + ' ' + team_name
    #print(team)

    home_game = todays_games.loc[sched['Home'] == team]
    away_game = todays_games.loc[sched['Visitor'] == team]
    team_game = home_game.append(away_game)
    #print(team_game)
    return team_game

if __name__ == "__main__":
    test_date = datetime(2017, 10, 17, 0, 0, 0).strftime('%m/%d/%Y')
    #print(TEST_DATE)

    games = get_all_games(today=test_date)
    print(games)

    #game = get_team_game('cle', test_date)
    #print(game)