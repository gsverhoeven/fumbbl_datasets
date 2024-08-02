
import time
import gzip
import json
import pandas as pd


def process_group_jsons(group_ids, fullrun, target = None):

    n_groups = len(group_ids)
    if target is None:
        target = 'raw/df_groups_' + time.strftime("%Y%m%d_%H%M%S") + '.h5'

    if fullrun:
        group_id = []
        group_name = []
        ruleset = []

        print('processing group data for ', n_groups, ' groups')

        for t in range(n_groups):    
            group_id_tmp = int(group_ids[t])
            dirname = "raw/group_files/" + str(group_id_tmp)[0:2]

            fname_string_gz = dirname + "/group_" + str(group_id_tmp) + ".json.gz"        
            
            # read compressed json file
            with gzip.open(fname_string_gz, mode = "rb") as f:
                group = json.load(f)

            if str(group) != 'No such group.':
                # grab fields
                group_id.append(group['id'])
                group_name.append(group['name'])
                ruleset.append(group['ruleset'])

            if t % 500 == 0: 
                # write tmp data as hdf5 file
                print(t, end='')
                print(".", end='')

        data = zip(group_id, group_name, ruleset)
        df_groups = pd.DataFrame(data, columns=['group_id', 
        'group_name', 'ruleset'])
        df_groups.to_hdf(target, key='df_groups', mode='w')   


    else:
        # read from hdf5 file
        if target is None:
            print("error choose target file")
        df_groups = pd.read_hdf(target)

    df_groups['group_id'] = pd.to_numeric(df_groups.group_id) 
    df_groups['ruleset'] = pd.to_numeric(df_groups.ruleset) 

    return df_groups