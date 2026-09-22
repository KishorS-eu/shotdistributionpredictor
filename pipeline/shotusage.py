"""Shot Usage metrics derived from StatsBomb event data."""

import numpy as np
import pandas as pd
from statsbombpy import sb

from pipeline.lpevents import get_lineup_events
from pipeline.utils import get_team_matchids


def get_shots_from_timeline(team_id, match_id):
    """Return dataframe of shot events for a given team and match attached with teamsheet and mandown information for each shot.
    
    Arguments:
    team_id: StatsBomb team ID
    match_id: StatsBomb match ID

    Note - This function only works for league matches, need to implement check for knockout matches

    """
    # initialise shot and lineup events for the given team and match
    events = sb.events(match_id = match_id)
    shots_df = events[(events['type'] == 'Shot') & (events['team_id'] == team_id)].copy()
    shots_df = shots_df.sort_values(by=['period', 'timestamp']).reset_index(drop=True)
    lineup_events = get_lineup_events(team_id, match_id)

    # match each shot with the teamsheet and mandown state at the time of the shot
    shot_teamsheets = []
    shot_mandown = []
    for idx, shot in shots_df.iterrows():
        shot_period = shot['period']
        shot_time = shot['timestamp']

        # we get a list of lineup events occuring before the shot, within the same game period
        # the game period corresponds to game halves
        #
        # if there are no lineup events, occuring before the shot, check the previous period
        # since we only consider league matches, there is always a starting lineup event, so we
        # will always find a corresponding teamsheet in the previous period (which can only ever
        # be the first half)
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
    """Return dataframe of shot events with teamsheets attached for a given team over a season.
    
    Arguments:
    comp_id: StatsBomb competition ID
    season_id: StatsBomb season ID
    team_id: StatsBomb team ID

    Note - This function only works for league matches, waiting on get_shots_from_timeline to be adapted for knockout matches

    """
    # get list of match IDs for the team over the season
    team_matchids = get_team_matchids(comp_id, season_id, team_id)

    games = len(team_matchids)
    print(f'Found {games} games for the season')

    # get shot events with teamsheets for the first game, which serves as initial dataframe for concatenation
    team_shot_events = get_shots_from_timeline(team_id, team_matchids[0])
    print(f'Processed shot event data for game 1/{games}')

    # concatenating shot events with teamsheets for the other games played in the season
    for id_x, id_game in enumerate(team_matchids[1:]):
        team_shot_events = pd.concat([team_shot_events, get_shots_from_timeline(team_id, id_game)])
        print(f'Processed shot event data for game {id_x + 2}/{games}')
    return team_shot_events

# adapt this for lineup events
def get_uniquelineups(shotevents_df):  # noqa D103
    unique_lineups = shotevents_df['teamsheet'].unique()

    lineup_df= []
    for idx, l_key in enumerate(unique_lineups):
        subset_df = shotevents_df[shotevents_df['teamsheet'] == l_key].copy()
        lineup_df.append([subset_df, l_key])

    return lineup_df

# adapt this for lineup events
def get_allfeaturedplayers(shotevents_df):  # noqa D103
    unique_lineups = shotevents_df['teamsheet'].unique()

    listoflineups = list(unique_lineups)
    return frozenset().union(*listoflineups)

def get_playerusage(shotevents_df, player_id, player_name):
    """Return a list of shot stats, including player usage, and associated dataframes for a given player over a season.

    Arguments:
    shotevents_df: Dataframe of shot events with teamsheets attached for a given team over a season.
    player_id: StatsBomb player ID
    player_name: StatsBomb player name

    Output:
    5 element list - [player_shots, team_shots, player_usage, team_shots_df, player_shots_df]

    player_shots: Number of shots taken by the player over the season.
    team_shots: Number of shots taken by the team over the season when the player was on the field
    player_usage: Percentage of shots taken by the player over the season when the player was on the field.
    team_shots_df: Dataframe of all shots taken by the team over the season when the player was on the field.
    player_shots_df: Dataframe of all shots taken by the player over the season.

    Note - The returned dataframes are filtered to only include events where the team was playing with 11 players on the field.
           Will be replaced by two functions that return the each dataframe; this is a temporary solution to get the player usage metric.

    """
    # proccessedshots_df is a list of tuples with a dataframe of shot events linked to a unique team sheet
    # with the corresponding teamsheet as a frozenset
    processedshots_df = get_uniquelineups(shotevents_df)

    # filter list of tuples via the frozenset to only get dataframes where the player is found in the teamsheet
    sublist = [
        (df, f_set) for df, f_set in processedshots_df
        if (str(int(player_id)), player_name) in f_set
    ]
    # numpy array and pandas dataframe manipulation to get dataframes of all shot events with player on the field
    # and shots taken by the player, filtering out any events where the team was playing with fewer than 11 players
    subarray = np.array(sublist, dtype = object)
    new_df = pd.concat(list(subarray[:, 0]))
    new_df = new_df[(~new_df['mandown'])]
    player_df = new_df[(new_df['player_id'] == player_id)]

    return [len(player_df), len(new_df), (100*(len(player_df)/len(new_df))), new_df, player_df]