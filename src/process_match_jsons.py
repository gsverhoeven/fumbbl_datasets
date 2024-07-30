import time
import os
import json
import pandas as pd

def process_match_jsons(full_run, begin_match, end_match, verbose = True, target_file = None):

    n_matches = end_match - begin_match

    print("matches to process:")
    print(n_matches)

    if(full_run):
        if target_file is None:
            target = 'raw/df_matches_' + time.strftime("%Y%m%d_%H%M%S") + '.h5'
        else:
            target = target_file
            
        print(target)

        match_id_list = []
        replay_id = []
        tournament_id = []
        division_id = []
        division_name = []
        scheduler = []
        match_date = []
        match_time = []
        match_conceded = []
        team1_id = []
        team2_id = []
        # touchdowns
        team1_score = []
        team2_score = []
        # casualties
        team1_cas_bh = []
        team1_cas_si = []
        team1_cas_rip = []
        team2_cas_bh = []
        team2_cas_si = []
        team2_cas_rip = []
        # other
        team1_roster_id = []
        team2_roster_id = []
        team1_coach_id = []
        team2_coach_id = []
        team1_race_name = []
        team2_race_name = []
        team1_value = []
        team2_value = []

        for i in range(n_matches):
            if i % 10000 == 0: 
                if verbose:
                    # write progress report
                    print(i, end='')
                    print(".", end='')

            match_id = end_match - i

            dirname = "raw/match_html_files/" + str(match_id)[0:4]
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            fname_string = dirname + "/match_" + str(match_id) + ".json"
             
            
            # read compressed json file
            with open(fname_string, mode = "rb") as f:
                match = json.load(f)

            if match: # fix for matches that do not exist
                match_id_list.append(match['id'])
                replay_id.append(match['replayId'])
                tournament_id.append(match['tournamentId']) # key to tournament table
                division_id.append(match['divisionId'])
                division_name.append(match['division'])
                scheduler.append(match['scheduler'])
                match_date.append(match['date'])
                match_time.append(match['time'])
                match_conceded.append(match['conceded'])
                team1_id.append(match['team1']['id'])
                team2_id.append(match['team2']['id'])
                # touchdowns
                team1_score.append(match['team1']['score'])
                team2_score.append(match['team2']['score'] ) 
                # casualties
                team1_cas_bh.append(match['team1']['casualties']['bh'])
                team1_cas_si.append(match['team1']['casualties']['si'])
                team1_cas_rip.append(match['team1']['casualties']['rip'])
                team2_cas_bh.append(match['team2']['casualties']['bh'])
                team2_cas_si.append(match['team2']['casualties']['si'])
                team2_cas_rip.append(match['team2']['casualties']['rip'])
                # other
                team1_roster_id.append(match['team1']['roster']['id'])
                team2_roster_id.append(match['team2']['roster']['id'] )           
                team1_coach_id.append(match['team1']['coach']['id'])
                team2_coach_id.append(match['team2']['coach']['id'])
                team1_race_name.append(match['team1']['roster']['name'] )
                team2_race_name.append(match['team2']['roster']['name'] )
                team1_value.append(match['team1']['teamValue'])
                team2_value.append(match['team2']['teamValue'])
                
            else:
                # skip match
                continue 
                
        data = zip(match_id_list, replay_id, tournament_id, division_id, division_name, scheduler, match_date, match_time,  match_conceded, 
                   team1_id, team1_coach_id, team1_roster_id, team1_race_name, team1_value, team1_cas_bh, team1_cas_si, team1_cas_rip,
                   team2_id, team2_coach_id, team2_roster_id, team2_race_name, team2_value, team2_cas_bh, team2_cas_si, team2_cas_rip,
                   team1_score, team2_score)

        df_matches = pd.DataFrame(data, columns=['match_id', 'replay_id', 'tournament_id', 'division_id', 'division_name', 'scheduler', 'match_date', 'match_time',  'match_conceded',
        'team1_id', 'team1_coach_id', 'team1_roster_id', 'team1_race_name', 'team1_value', 'team1_cas_bh', 'team1_cas_si', 'team1_cas_rip',
        'team2_id', 'team2_coach_id', 'team2_roster_id', 'team2_race_name', 'team2_value', 'team2_cas_bh', 'team2_cas_si', 'team2_cas_rip',
        'team1_score', 'team2_score'])
      
        df_matches = df_matches.sort_values(by=['match_id']).reset_index(drop=True)
        df_matches.to_hdf(target, key='df_matches', mode='w')
    else:
        # read from hdf5 file    
        df_matches = pd.read_hdf(target_file) 

    return df_matches