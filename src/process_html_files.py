import time
import re
from bs4 import BeautifulSoup
import gzip
import pandas as pd

import lxml
import cchardet
# https://thehftguy.com/2020/07/28/making-beautifulsoup-parsing-10-times-faster/



def process_html_files(begin_match = None, end_match = None, target = None, verbose = False):

    if target is None:
        target = 'raw/df_matches_html_' + time.strftime("%Y%m%d_%H%M%S") + '.h5'

    print(target)

    n_matches = end_match - begin_match

    print(n_matches)
    match_id = [] # used CTRL + D to add to selection
    team1_inducements = []
    team2_inducements = []
    coach1_ranking = []
    coach2_ranking = []
    team1_comp = []
    team2_comp = []
    team1_pass = []
    team2_pass = []
    team1_rush = []
    team2_rush = []
    team1_block = []
    team2_block = []
    team1_foul = []
    team2_foul = []

    for i in range(n_matches):
        match_id_tmp = end_match - i
        dirname = "raw/match_html_files/" + str(match_id_tmp)[0:4]

        # PM first check gz, if not exist then check for unzipped html
        #fname_string = dirname + "/match_" + str(match_id_tmp) + ".html"        
        fname_string_gz = dirname + "/match_" + str(match_id_tmp) + ".html.gz"        

        with gzip.open(fname_string_gz, mode = "rb") as f:
            soup = BeautifulSoup(f, 'lxml')

        if soup.find("div", {"class": "matchrecord"}) is not None:
            # match record is available
            inducements = soup.find_all("div", class_="inducements")

            pattern = re.compile(r'\s+Inducements: (.*)\n')

            match = re.match(pattern, inducements[0].get_text())
            if match:
                team1_inducements_tmp = match.group(1)
            else:
                team1_inducements_tmp = ''
            if len(inducements) < 2: # not ok
                print(match_id_tmp)
                return inducements
            match = re.match(pattern, inducements[1].get_text())
            if match:
                team2_inducements_tmp = match.group(1)
            else:
                team2_inducements_tmp = ''

            coach_info = soup.find_all("div", class_="coach")
            # grab the ranking
            coach1_ranking_tmp = coach_info[0].get_text()
            coach2_ranking_tmp = coach_info[1].get_text()

            # match performance stats
            div = soup.find_all('div', class_= "player foot")
            # passing completions
            regex = re.compile('.*front comp statbox.*')
            team1_comp_tmp = div[0].find("div", {"class" : regex}).get_text()
            team2_comp_tmp = div[1].find("div", {"class" : regex}).get_text()                   
            # passing distance in yards
            regex = re.compile('.*back pass statbox.*')
            team1_pass_tmp = div[0].find("div", {"class" : regex}).get_text()
            team2_pass_tmp = div[1].find("div", {"class" : regex}).get_text()
            # rushes
            regex = re.compile('.*back rush statbox.*')
            team1_rush_tmp = div[0].find("div", {"class" : regex}).get_text()
            team2_rush_tmp = div[1].find("div", {"class" : regex}).get_text()
            # block
            regex = re.compile('.*back block statbox.*')
            team1_block_tmp = div[0].find("div", {"class" : regex}).get_text()
            team2_block_tmp = div[1].find("div", {"class" : regex}).get_text()
            # foul
            regex = re.compile('.*back foul statbox.*')
            team1_foul_tmp = div[0].find("div", {"class" : regex}).get_text()
            team2_foul_tmp = div[1].find("div", {"class" : regex}).get_text()

            match_id.append(match_id_tmp) # append for single item, extend for multiple items
            team1_inducements.append(team1_inducements_tmp)
            team2_inducements.append(team2_inducements_tmp)
            coach1_ranking.append(coach1_ranking_tmp)
            coach2_ranking.append(coach2_ranking_tmp)
            team1_comp.append(team1_comp_tmp)
            team2_comp.append(team2_comp_tmp)
            team1_pass.append(team1_pass_tmp)
            team2_pass.append(team2_pass_tmp)
            team1_rush.append(team1_rush_tmp)
            team2_rush.append(team2_rush_tmp)
            team1_block.append(team1_block_tmp)
            team2_block.append(team2_block_tmp)
            team1_foul.append(team1_foul_tmp)
            team2_foul.append(team2_foul_tmp)
        
        if i % 1000 == 0: 
        # write progress report
            print(i, end='')
            print(".", end='')

    data = zip(match_id, team1_inducements, team2_inducements, 
                            coach1_ranking, coach2_ranking, team1_comp, team2_comp,
                            team1_pass, team2_pass, team1_rush, team2_rush,
                            team1_block, team2_block, team1_foul, team2_foul)

    df_matches_html_ = pd.DataFrame(data, columns = ['match_id', 'team1_inducements', 'team2_inducements',
    'coach1_ranking', 'coach2_ranking', 'team1_comp', 'team2_comp',
    'team1_pass', 'team2_pass', 'team1_rush', 'team2_rush',
    'team1_block', 'team2_block', 'team1_foul', 'team2_foul'])

    return df_matches_html_