import gzip
import requests
import os
import json

def scrape_match_htmls(full_run, begin_match, end_match, verbose = False):

    print("matches to scrape: ")
    n_matches = end_match - begin_match

    print(n_matches)

    if(full_run):
        for i in range(n_matches):

            match_id = end_match - i
            dirname = "raw/match_html_files/" + str(match_id)[0:4]
            fname_string = dirname + "/match_" + str(match_id) + ".html.gz"

            # check if file already exists, else scrape it
            try:
                f = open(fname_string, mode = "rb")

            except OSError as e:
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                # fetch html
                api_string = "https://fumbbl.com/FUMBBL.php?page=match&id=" + str(match_id)

                response = requests.get(api_string)
                # write html
                with gzip.open(fname_string, mode = "wb") as f:
                    f.write(response.text.encode("utf-8"))
                    f.close()
                    if verbose:
                        print("o", end = '')
            else:
                # file already present
                pass

            if i % 1000 == 0: 
                if verbose:
                # write progress report
                    print(i, end = '')
                    print(".", end = '')

def scrape_single_html(verbose = False):

    dirname = "raw/match_html_files/"
    fname_string = dirname +  "tst.html.gz"

    # check if file already exists, else scrape it
    try:
        f = open(fname_string, mode = "rb")

    except OSError as e:
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        # fetch html
        api_string = 'https://fumbbl.com/p/boxtrophy'
        headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}

        response = requests.get(api_string, headers = headers)
        # write html
        with gzip.open(fname_string, mode = "wb") as f:
            f.write(response.text.encode("utf-8"))
            f.close()
            if verbose:
                print("o", end = '')
    else:
        # file already present
        pass
    return json.loads(response.text)