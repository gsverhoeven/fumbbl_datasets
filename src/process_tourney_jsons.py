import gzip
import json
import pandas as pd
import time

def process_tourney_jsons(tournament_ids, fullrun, target = None):
    
    n_tourneys = len(tournament_ids)

    if target is None:
        target = 'raw/df_tourneys_' + time.strftime("%Y%m%d_%H%M%S") + '.h5'

    if fullrun:
        tournament_id = []
        group_id = []
        tournament_type = []
        tournament_progression = []
        tournament_name = []
        tournament_start = []
        tournament_end = []

        print('processing tourney data for ', n_tourneys, ' tournaments')

        for t in range(n_tourneys):    
            tournament_id_tmp = int(tournament_ids[t])
            dirname = "raw/tournament_files/" + str(tournament_id_tmp)[0:2]

            fname_string_gz = dirname + "/tournament_" + str(tournament_id_tmp) + ".json.gz"        
            
            # read compressed json file
            with gzip.open(fname_string_gz, mode = "rb") as f:
                tournament = json.load(f)

            if str(tournament) != 'No such tournament.':
                # grab fields
                tournament_id.append(tournament['id'])
                group_id.append(tournament['group'])
                tournament_type.append(tournament['type'])
                tournament_progression.append(tournament['progression'])
                tournament_name.append(tournament['name'])
                tournament_start.append(tournament['start'])
                tournament_end.append(tournament['end'])   

            if t % 500 == 0: 
                # write tmp data as hdf5 file
                print(t, end='')
                print(".", end='')
        # create list of tuples
        data = zip(tournament_id, group_id, tournament_type, tournament_progression, tournament_name, tournament_start, tournament_end)
        # create dataframe from list
        df_tourneys = pd.DataFrame(data, columns=['tournament_id', 'group_id', 'tournament_type', 'tournament_progression', 
        'tournament_name', 'tournament_start', 'tournament_end'])
        df_tourneys.to_hdf(target, key='df_tourneys', mode='w')   


    else:
        # read from hdf5 file
        if target is None:
            print("error choose a cached target file")      
        df_tourneys = pd.read_hdf(target)

    df_tourneys['tournament_id'] = pd.to_numeric(df_tourneys.tournament_id) 
    df_tourneys['group_id'] = pd.to_numeric(df_tourneys.group_id) 
    df_tourneys['tournament_type'] = pd.to_numeric(df_tourneys.tournament_type) 

    return df_tourneys