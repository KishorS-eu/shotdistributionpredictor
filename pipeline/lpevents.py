"""Lineup Event Processing for StatsBomb data."""
 
import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
from statsbombpy import sb


def get_teamsheet(lineup):
    """Return frozenset representing a teamsheet.
    
    Arguments:
    lineup: Dictionary from StatsBomb event data, from the 'tactics' column of a Starting XI event.
    
    Using frozensets to represent teamsheets allows for easy and quick comparison between event points.

    """
    player_data = set()
    for player in lineup['lineup']:
        player_data.add((str(player['player']['id']), player['player']['name']))
    return frozenset(player_data)

def sub_teamsheet(lineup, subin_id, subin_name, subout_id, subout_name):
    """Return frozenset representing a teamsheet after a substitution.
    
    Arguments:
    lineup: Current teamsheet as a frozenset.
    subin_id: ID of the player coming on.
    subin_name: Name of the player coming on.
    subout_id: ID of the player going off.
    subout_name: Name of the player going off.

    """
    mut_lineup = set(lineup)
    mut_lineup.remove((str(int(subout_id)), subout_name))
    mut_lineup.add((str(int(subin_id)), subin_name))
    return frozenset(mut_lineup)

def playeroff_teamsheet(lineup, out_id, out_name):
    """Return frozenset representing a teamsheet after a player is substituted off.

    Arguments:
    lineup: Current teamsheet as a frozenset.
    out_id: ID of the player being substituted off.
    out_name: Name of the player being substituted off.

    """
    mut_lineup = set(lineup)
    mut_lineup.remove((str(int(out_id)), out_name))
    return frozenset(mut_lineup)

def playeron_teamsheet(lineup, on_id, on_name):
    """Return frozenset representing a teamsheet after a player is substituted on.

    Arguments:
    lineup: Current teamsheet as a frozenset.
    on_id: ID of the player being substituted on.
    on_name: Name of the player being substituted on.

    """
    mut_lineup = set(lineup)
    mut_lineup.add((str(int(on_id)), on_name))
    return frozenset(mut_lineup)

def mandown_teamsheet(lineup):
    """Return boolean indicating if a teamsheet has fewer than 11 players.

    Arguments:
    lineup: Teamsheet as a frozenset.

    """
    return len(lineup) < 11

def get_lineup_events(team_id, match_id):
    """Return dataframe, given a team and match, with teamsheet change events for that team and match.
    
    Arguments:
    team_id: StatsBomb team ID
    match_id: StatsBomb match ID
    
    """
    selected_types = ['Starting XI', 'Half End', 'Substitution',
                     'Player On', 'Player Off']

    # get match event data
    event_df = sb.events(match_id = match_id)
    filtered_df = event_df[event_df['type'].isin(selected_types)]
    filtered_df = filtered_df[filtered_df['team_id'] == team_id]
    filtered_df = filtered_df.sort_values(by = ['period', 'timestamp']).copy()
    filtered_df = filtered_df[ ~((filtered_df['type'] == 'Half End') &
                                (filtered_df['period'] == 1))]
    filtered_df = filtered_df.reset_index(drop = True)


    # get the starting lineup array
    starting_xi_event = filtered_df[
        (filtered_df['type'] == 'Starting XI') &
        (filtered_df['team_id'] == team_id)
        ].iloc[0]

    starting_xi = starting_xi_event['tactics']
    starting_ts = get_teamsheet(starting_xi)

    teamsheets = [starting_ts]
    mandown = []
    for idx, row in filtered_df.iterrows():
        event_type = row['type']
        # handling changes in teamsheets for different event types
        if event_type == 'Starting XI':
            pass

        elif event_type == 'Substitution':
            subout_id = row['player_id']
            subout_name = row['player']
            subin_id = row['substitution_replacement_id']
            subin_name = row['substitution_replacement']
            teamsheets.append(sub_teamsheet(teamsheets[idx - 1], subin_id,
                                            subin_name, subout_id, subout_name))

        elif event_type == 'Player Off':
            out_id = row['player_id']
            out_name = row['player']
            teamsheets.append(playeroff_teamsheet(teamsheets[idx - 1], out_id,
                                                  out_name))

        elif event_type == 'Player On':
            on_id = row['player_id']
            on_name = row['player']
            teamsheets.append(playeron_teamsheet(teamsheets[idx - 1], on_id,
                                                 on_name))

        elif event_type == 'Half End':
            teamsheets.append(teamsheets[idx - 1])

        # adding boolean value to mandown based on if the teamsheet has a numpy nan value
        # keeps track of when a team is playing with 10 or less players
        mandown.append(mandown_teamsheet(teamsheets[idx]))

    # adding teamsheet and "mandown" information corresponding to the lineup change events
    filtered_df['teamsheet'] = teamsheets
    filtered_df['mandown'] = mandown
    filtered_df.loc[:, 'teamsheet'] = filtered_df['teamsheet']

    columns_to_retain = ['id', 'index', 'match_id', 'team', 'team_id', 'period',
                         'timestamp', 'type', 'teamsheet', 'mandown']

    return filtered_df[columns_to_retain].reset_index(drop=True)
