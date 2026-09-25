"""Utilities for Lineup Information."""

# this probably needs some work but this is more so for exploratory analysis
def get_uniquelineups(matchevents_df):  # noqa D103
    unique_lineups = matchevents_df['teamsheet'].unique()

    lineup_df= []
    for idx, l_key in enumerate(unique_lineups):
        subset_df = matchevents_df[matchevents_df['teamsheet'] == l_key].copy()
        lineup_df.append([subset_df, l_key])

    return lineup_df


def get_allfeaturedplayers(matchevents_df):  # noqa D103
    unique_lineups = matchevents_df['teamsheet'].unique()

    listoflineups = list(unique_lineups)
    return frozenset().union(*listoflineups)