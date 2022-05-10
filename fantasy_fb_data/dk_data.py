import requests
import json
import pandas as pd
import re


class GetData:
    def __init__(self):
        self.get_players()

    # Search for matchup in contest name
    def parse_match(self, s):
        try:
            found = re.search('(....vs....)', s).group(1)
            found = found.strip('(')
            found = found.strip(')')
            return (found)
        except AttributeError:
            pass

    def get_contests(self):
        # Get NFL Matchup Data from Draft Kings
        nfl_contests = requests.get("https://www.draftkings.com/lobby/getcontests?sport=NFL")
        # Convert to JSON format
        contests_data = nfl_contests.json()
        # Use JSON Object to create Pandas DataFrame and select desired columns
        contest_df = pd.DataFrame(contests_data['Contests'])
        contest_df =  contest_df[['dg', 'gameType', 'n']]
        # contest_df = contest_df.groupby('gameType').first()

        # More Data Cleaning
        contest_df['n'] = contest_df['n'].apply(lambda x: self.parse_match(x))
        contest_df = contest_df.rename(columns={'dg': 'contest_id', 'n': 'event'})
        # contest_df = contest_df.loc[contest_df['gameType'] == 'Showdown Captain Mode']
        contest_df = contest_df.loc[contest_df['gameType'] != 'Madden Showdown Captain Mode']
        contest_df = contest_df.loc[contest_df['gameType'] != 'Madden Classic']

        # Aggregate by gameType
        contest_df = contest_df.groupby('gameType', ).first()
        print('Upcoming Challenges: \n', contest_df.head(), '\n')
        return contest_df

    def get_players(self):
        c_ids = self.get_contests()['contest_id']  # Grab contest IDs and search for players

        for c in c_ids:  # Get Player Data for each NFL Contest
            players_response = requests.get(
                "https://api.draftkings.com/draftgroups/v1/draftgroups/{}/draftables".format(c))
            raw_data = players_response.text
            # print(raw_data)

            # Filter Results
            data = json.loads(raw_data)
            df = pd.DataFrame(data['draftables'])
            df_players = df[['displayName', 'position', 'salary', 'draftStatAttributes', 'teamAbbreviation', 'status']]
            df_players = df_players.rename(columns={'displayName': 'Name', 'position': 'POS', 'salary': 'Salary',
                                                    'teamAbbreviation': 'Team', 'status': 'Status',
                                                    'draftStatAttributes': 'FPPG'})
            df_players['FPPG'] = df_players['FPPG'].apply(lambda z: z[0])
            df_players['FPPG'] = df_players['FPPG'].apply(lambda z: float(z['value']) if z['id'] == 90 else None)
            df_players = df_players.dropna()
            df_players.drop_duplicates(inplace=True)
            df_players.reset_index(drop=True, inplace=True)
            # Calculate a "Points Per 1k Salary" Data Point
            df_players['Points_per_1k$'] = df_players['FPPG'] / df_players['Salary'] * 1000
            print('Event_ID: ', c, '\n', 'Player Data: \n', df_players.head(8))

            df_value = df_players.sort_values('Points_per_1k$', ascending=False)
            df_value = df_value.loc[df_value['Status'] != 'IR']
            df_value.reset_index(drop=True, inplace=True)
            print('Top 25 Best Value Players: \n', df_value.head(25))  # Show top 25 best-value players for each contest

        return


#TODO Use results DB to compute historical average prices
# https://rotogrinders.com/resultsdb/nfl

#TODO Find data on % of snaps each player is in and total playtime


if __name__ == '__main__':
    GetData()
