import os
import requests
import time
from src.write_json_file import write_json_file


def update_match_jsons(full_run, begin_match, end_match, verbose = False):

    n_matches = end_match - begin_match

    print("matches to grab:")
    print(n_matches)

    if(full_run):
        for i in range(n_matches):
            if i % 100 == 0: 
                if verbose:
                    # write progress report
                    print(i, end='')
                    print(".")

            match_id = end_match - i

            dirname = "raw/match_html_files/" + str(match_id)[0:4]
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            fname_string = dirname + "/match_" + str(match_id) + ".json"

            # check if file already exists, else scrape it
            try:
                f = open(fname_string, mode = "rb")

            except OSError as e:
              # scrape it
                api_string = "https://fumbbl.com/api/match/get/" + str(match_id)

                match = requests.get(api_string)
                match = match.json()

                write_json_file(match, fname_string)
                if verbose:
                    print("x", end = '')
                time.sleep(0.3)
            else:
                # file already present
                if verbose:
                    print("o", end = '')
                continue # continue forces the loop to start at the next iteration, 
            #whereas pass means, “there is no code to execute here,” and it will continue through the remainder of the loop body