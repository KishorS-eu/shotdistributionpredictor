from statsbombpy import sb
import pandas as pd
import numpy as np

def get_teams(comp_id, season_id):
    season_matches = sb.matches(competition_id = comp_id, season_id = season_id)
    return season_matches[['home_team_id', 'home_team']].copy().drop_duplicates().sort_values(by = ['home_team_id']).reset_index(drop=True)

def get_team_matchids(comp_id, season_id, team_id):
    season_matches = sb.matches(competition_id = comp_id, season_id = season_id)
    team_matches = season_matches[(season_matches['home_team_id'] == team_id)
                                  |(season_matches['away_team_id'] == team_id)].reset_index(drop=True)
    return team_matches['match_id'].to_list()