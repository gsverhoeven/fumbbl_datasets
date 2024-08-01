# save tournament API call as gzipped JSON object.

import os
import gzip
import requests
import time
import json

def update_tourney_jsons(tournament_ids, fullrun = 0):
    print("total nr of tournaments in the data:")

    n_tourneys = len(tournament_ids)

    print(n_tourneys)

    if fullrun:
        print('fetching tournament data for ', n_tourneys, ' tourneys')

        for t in range(n_tourneys):
            tournament_id = int(tournament_ids[t])
            if t % 100 == 0: 
                # write progress report
                print(t, end='')
                print(".")

            dirname = "raw/tournament_files/" + str(tournament_id)[0:2]
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            fname_string = dirname + "/tournament_" + str(tournament_id) + ".json.gz"

            # check if file already exists, else scrape it
            try:
                f = open(fname_string, mode = "rb")

            except OSError as e:
                # file not present, scrape it         
                api_string = "https://fumbbl.com/api/tournament/get/" + str(tournament_id)

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