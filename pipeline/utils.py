"""Utilities for fetching data from StatsBomb API."""

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
from statsbombpy import sb


def get_teams(comp_id, season_id):
    """Return dataframe of teams for given competition and season.
    
    Arguments:
    comp_id: StatsBomb competition ID
    season_id: StatsBomb season ID

    """
    season_matches = sb.matches(competition_id=comp_id,
                                season_id=season_id)

    return (season_matches[['home_team_id', 'home_team']]
            .copy()
            .drop_duplicates()
            .sort_values(by=['home_team_id'])
            .reset_index(drop=True))


def get_team_matchids(comp_id, season_id, team_id):
    """Return list of match IDs for a given team in given competition and season.
    
    Arguments:
    comp_id: StatsBomb competition ID
    season_id: StatsBomb season ID
    team_id: StatsBomb team ID

    """
    season_matches = sb.matches(competition_id=comp_id,
                                season_id=season_id)
    team_matches = (season_matches[(season_matches['home_team_id']
                                    == team_id)
                                   | (season_matches['away_team_id']
                                      == team_id)]
                    .reset_index(drop=True))
    return team_matches['match_id'].to_list()
