# save group API call as gzipped JSON object.
import os
import gzip
import json
import time
import requests

def update_group_jsons(group_ids, fullrun = 0):
    print("total nr of groups in the data:")

    n_groups = len(group_ids)

    print(n_groups)

    if fullrun:
        print('fetching group data for ', n_groups, ' groups')

        for t in range(n_groups):
            group_id = int(group_ids[t])
            if t % 100 == 0: 
                # write progress report
                print(t, end='')
                print(".")

            dirname = "raw/group_files/" + str(group_id)[0:2]
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            fname_string = dirname + "/group_" + str(group_id) + ".json.gz"

            # check if file already exists, else scrape it
            try:
                f = open(fname_string, mode = "rb")

            except OSError as e:
                # file not present, scrape it         
                api_string = "https://fumbbl.com/api/group/get/" + str(group_id)

                response = requests.get(api_string)
                response = response.json()

                with gzip.open(fname_string, mode = "w") as f:
                    f.write(json.dumps(response).encode('utf-8'))  
                    print('x', end = '')
                    f.close()
                time.sleep(0.3)
            else:
                # file already present
                print("o", end = '')
                continue


    else:
        print("full run is off")