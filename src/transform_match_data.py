import pandas as pd
import numpy as np

def transform_match_data(df_matches, api_change = 258150):

    # convert object dtype columns to proper pandas dtypes datetime and numeric
    df_matches['match_date'] = pd.to_datetime(df_matches.match_date) # Datetime object

    # calculate match score difference
    df_matches['team1_win'] = np.sign(df_matches['team1_score'] - df_matches['team2_score'])
    df_matches['team2_win'] = np.sign(df_matches['team2_score'] - df_matches['team1_score'])

    # mirror match
    df_matches['mirror_match'] = 0
    df_matches.loc[df_matches['team1_race_name'] == df_matches['team2_race_name'], 'mirror_match'] = 1

    # add total CAS
    df_matches['team1_cas'] = df_matches['team1_cas_bh'] + df_matches['team1_cas_si'] + df_matches['team1_cas_rip']

    # add total CAS
    df_matches['team2_cas'] = df_matches['team2_cas_bh'] + df_matches['team2_cas_si'] + df_matches['team2_cas_rip']

    # convert 1150000 integer to 1150k string for newer matches
    mask = (df_matches.match_id > 4474450)
    df_matches.loc[mask, 'team1_value'] = df_matches.loc[mask, 'team1_value']//1000 # force division result as int
    df_matches.loc[mask, 'team1_value'] = df_matches.loc[mask, 'team1_value'].astype(str) + 'k'
    df_matches.loc[mask, 'team2_value'] = df_matches.loc[mask, 'team2_value']//1000 # force division result as int
    df_matches.loc[mask, 'team2_value'] = df_matches.loc[mask, 'team2_value'].astype(str) + 'k'

    # convert team value 1100k to 1100 integer
    df_matches['team1_value'] = df_matches['team1_value'].str.replace('k$', '')
    df_matches['team1_value'] = df_matches['team1_value'].fillna(0).astype(np.int64)

    df_matches['team2_value'] = df_matches['team2_value'].str.replace('k$', '')
    df_matches['team2_value'] = df_matches['team2_value'].fillna(0).astype(np.int64)
    

    df_matches['tv_diff'] = np.abs(df_matches['team2_value'] - df_matches['team1_value'])
    df_matches['tv_diff2'] = df_matches['team2_value'] - df_matches['team1_value']

    df_matches['tv_match'] = df_matches[["team1_value", "team2_value"]].max(axis=1)

    df_matches['tv_bin'] = pd.cut(df_matches['tv_match'], 
        bins = [0, 950, 1250,1550, 1850, float("inf")], 
        labels=['< 950K', '1.1M', '1.4M', '1.7M', '> 1850K']
    )

    df_matches['tv_bin2'] = pd.cut(df_matches['tv_match'], 
        bins = [0, 950, 1050, 1150, 1250, 1350, 1450, 1550, float("inf")], 
        labels=['< 950K', '1.0M', '1.1M', '1.2M',  '1.3M', '1.4M', '1.5M', '> 1550K']
    )
    return df_matches