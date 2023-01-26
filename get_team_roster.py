import gzip
import pandas as pd
import numpy as np
import plotnine as p9
import requests
import json

def get_team_roster(match_id, team_id, df_skills, df_matches, inducements):

    dirname = "raw/team_files/" + str(team_id)[0:4]

    fname_string_gz = dirname + "/team_" + str(team_id) + ".json.gz"        

    # PM read compressed json file
    with gzip.open(fname_string_gz, mode = "rb") as f:
        team_obj = json.load(f)

    fname_string_gz = dirname + "/team_" + str(team_id) + "_skills.json.gz"        

    # PM read compressed json file
    with gzip.open(fname_string_gz, mode = "rb") as f:
        team_skill_obj = json.load(f)

    df_roster = pd.json_normalize(team_obj, 'players', ['rerolls', 'assistantCoaches', 'cheerleaders', 'apothecary', ['roster', 'name']])

    df_roster.rename({'id' : 'player_id'}, axis = 1, inplace = True)

    df_roster = df_roster.loc[:, ['player_id', 'number', 'position', 'rerolls', 'assistantCoaches', 'cheerleaders', 'apothecary', 'roster.name']]

    df_roster['team_id'] = team_id

    # Next we extract the player skill info into a nice pd dataFrame:
    pd_skills = pd.json_normalize(team_skill_obj, 'tournamentSkills')

    # next we add the skill info to the roster.
    pd_skills = pd.json_normalize(team_skill_obj, 'tournamentSkills')

    if pd_skills.empty is False:    
        pd_skills.columns = ['player_id', 'skill_id']

        pd_skills['player_id'] = pd_skills['player_id'].fillna(0).astype(np.int64)
        pd_skills['skill_id'] = pd_skills['skill_id'].fillna(0).astype(np.int64)

    else:
        pd_skills = pd.DataFrame({'player_id': [-1], 'skill_id': [-1]})

    # Next we add the skill names:
    pd_skills= pd.merge(pd_skills, df_skills, on='skill_id', how='left')

    # next we combine the skills with the roster
    df_roster = pd.merge(df_roster, pd_skills, on='player_id', how='left')

    # Next we add the inducements (Star players, bribes etc)
    if (df_matches.query('match_id == @match_id')['team1_id'].values[0] == team_id):
        inducement_id = 'team1'
    elif (df_matches.query('match_id == @match_id')['team2_id'].values[0] == team_id):
        inducement_id = 'team2'
    else:
        inducement_id = -1

    inducements_to_add = inducements.query('match_id == @match_id and team == @inducement_id')['inducements'].values.tolist()

    for inducement in inducements_to_add:
        if not inducement == ['']:
            new_row = df_roster.iloc[[1]].copy()
            new_row['position'] = inducement
            new_row['player_id'] = 99999999
            new_row['number'] = 99
            new_row['skill_id'] = np.NaN
            new_row['name'] = np.nan
            df_roster = df_roster.append(new_row)

    df_roster = df_roster.fillna('')
    #df_roster = df_roster.drop(df_roster[df_roster.position == ''].index)
    #df_roster['skill_id'] = df_roster['skill_id'].replace(-1, None)

    return df_roster