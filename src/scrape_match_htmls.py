import gzip
import requests
import os

def scrape_match_htmls(full_run, begin_match, end_match, verbose = False):

    print("matches to scrape: ")
    n_matches = end_match - begin_match

    print(n_matches)

    if(full_run):
        for i in range(n_matches):
            match_id = end_match - i
            api_string = "https://fumbbl.com/FUMBBL.php?page=match&id=" + str(match_id)

            response = requests.get(api_string)

            dirname = "raw/match_html_files/" + str(match_id)[0:4]
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            fname_string = dirname + "/match_" + str(match_id) + ".html.gz"
            
            with gzip.open(fname_string, mode = "wb") as f:
                f.write(response.text.encode("utf-8"))
                f.close()

            
            if i % 1000 == 0: 
                if verbose:
                # write progress report
                    print(i, end='')
                    print(".", end='')