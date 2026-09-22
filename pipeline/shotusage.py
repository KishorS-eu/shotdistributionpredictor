from statsbombpy import sb
import pandas as pd
import numpy as np

from pipeline.utils import get_team_matchids
from pipeline.lpevents import get_lineup_events

def get_shots_from_timeline(team_id, match_id, lineup_events):
    events = sb.events(match_id = match_id)
    shots_df = events[(events['type'] == 'Shot') & (events['team_id'] == team_id)].copy()
    shots_df = shots_df.sort_values(by=['period', 'timestamp']).reset_index(drop=True)

    shot_teamsheets = []
    shot_mandown = []

    for idx, shot in shots_df.iterrows():
        shot_period = shot['period']
        shot_time = shot['timestamp']

        past_events = lineup_events[
            (lineup_events['period'] == shot_period) &
            (lineup_events['timestamp'] <= shot_time)
        ]

        if len(past_events) > 0:
            active_state = past_events.iloc[-1]
        else:
            active_state = lineup_events[(lineup_events['period'] == shot_period - 1)].iloc[-1]

        shot_teamsheets.append(active_state['teamsheet'])
        shot_mandown.append(active_state['mandown'])

    shots_df['teamsheet'] = shot_teamsheets
    shots_df['mandown'] = shot_mandown

    return shots_df.dropna(axis = 1, how = 'all')

def get_teamseason_shot_events(comp_id, season_id, team_id):
    team_matchids = get_team_matchids(comp_id, season_id, team_id)

    games = len(team_matchids)
    print(f'Found {games} games for the season')

    team_shot_events = get_shots_from_timeline(team_id, team_matchids[0], get_lineup_events(team_id, team_matchids[0]))
    print(f'Processed shot event data for game 1/{games}')

    for id_x, id_game in enumerate(team_matchids[1:]):
        team_shot_events = pd.concat([team_shot_events, get_shots_from_timeline(team_id, id_game, get_lineup_events(team_id, id_game))])
        print(f'Processed shot event data for game {id_x + 2}/{games}')
    return team_shot_events

# adapt this for lineup events
def get_uniquelineups(shotevents_df):
    unique_lineups = shotevents_df['teamsheet'].unique()

    lineup_df= []
    for idx, l_key in enumerate(unique_lineups):
        subset_df = shotevents_df[shotevents_df['teamsheet'] == l_key].copy()
        lineup_df.append([subset_df, l_key])

    return lineup_df

# adapt this for lineup events
def get_allfeaturedplayers(shotevents_df):
    unique_lineups = shotevents_df['teamsheet'].unique()

    listoflineups = list(unique_lineups)
    return frozenset().union(*listoflineups)

def get_playerusage(processedshots_df, player_id, player_name):

    sublist = [
        (df, f_set) for df, f_set in processedshots_df
        if (str(int(player_id)), player_name) in f_set
    ]
    subarray = np.array(sublist, dtype = object)
    new_df = pd.concat(list(subarray[:, 0]))
    new_df = new_df[(~new_df['mandown'])]
    player_df = new_df[(new_df['player_id'] == player_id)]

    return [len(player_df), len(new_df), (100*(len(player_df)/len(new_df))), new_df, player_df]