import requests
import json
import pandas as pd
import re

# class DiscountPlayers: #Grab top 30 Players in each competition
#     def

nfl_contests = requests.get("https://www.draftkings.com/lobby/getcontests?sport=NFL")
contests_data = nfl_contests.json()
contest_df = pd.DataFrame(contests_data['Contests'])
contest_df = contest_df[['dg', 'gameType', 'n']]
# contest_df = contest_df.groupby('gameType').first()


#Search for matchup in contest name
def parse_match(s):
    try:
        found = re.search('(....vs....)', s).group(1)
        found = found.strip('(')
        found = found.strip(')')
        return(found)
    except AttributeError:
        pass

contest_df['n'] = contest_df['n'].apply(lambda x: parse_match(x))
contest_df = contest_df.rename(columns={'dg': 'contest_id', 'n': 'event'})
contest_df = contest_df.loc[contest_df['gameType'] == 'Showdown Captain Mode']
contest_df = contest_df.groupby('gameType',).first()
print('Upcoming Showdowns: \n', contest_df.head(), '\n')

c_ids = contest_df['contest_id'] #Grab contest IDs and search for players

for c in c_ids:
    players_response = requests.get("https://api.draftkings.com/draftgroups/v1/draftgroups/{}/draftables".format(c))
    raw_data = players_response.text
    # print(raw_data)

    data = json.loads(raw_data)
    df = pd.DataFrame(data['draftables'])
    df_players = df[['displayName', 'position', 'salary', 'teamAbbreviation', 'status', ]]
    df_players = df_players.rename(columns={'displayName': 'Name', 'position': 'POS', 'salary': 'Salary',
                                            'teamAbbreviation': 'Team', 'status': 'Status'})
    print('Event_ID: ', c, '\n', 'Player Data: \n', df_players.head())
