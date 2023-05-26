def extract_player_ids_from_single_file(match_id):
    
    dirname = "raw/match_html_files/" + str(match_id)[0:4]
    fname_string = dirname + "/match_" + str(match_id) + ".html"  

    with open(fname_string, mode = "r") as f:
        # https://stackoverflow.com/questions/30277109/beautifulsoup-takes-forever-can-this-be-done-faster
        soup = BeautifulSoup(f, 'xml')

    if soup.find("div", {"class": "matchrecord"}) is not None:
        # match record is available
        player_id = []
        player_number = []
        player_name = []

        players = soup.find_all("div", class_="player")

        for p in range(len(players)):
            div = players[p].find("div", class_= "name")
            # https://stackoverflow.com/questions/55442727/remove-unicode-xa0-from-pandas-column
            div_number = players[p].find("div", class_= "number")
            if div_number is not None:
                div_number = div_number.get_text().strip()
                if div_number is not '':
                    player_number.append(div_number)

            for a in div.find_all('a'):
                # url to scrape
                #player_number = p
                player_url = a.get('href') #for getting link
                player_id.append(player_url.split('=', 1)[1])
                # player name
                player_name.append(a.text) #for getting text between the link
        return [match_id] * len(player_id), player_id, player_number, player_name
    else:
        # NOT SMART, this will fuck up the data types (PyTables pickle performance warning)
        return [match_id], [-1], [None], [None]
    

%load_ext line_profiler
%lprun -f extract_player_ids_from_single_file extract_player_ids_from_single_file(4386470)

# 31% of the time is parsing the HTML!!

extract_player_ids_from_single_file(4353200)

def extract_player_ids(N):

    target = 'raw/df_player_ids_html_' + time.strftime("%Y%m%d_%H%M%S") + '.h5' # 

    print(target)

    end_match = 4386470 #use from previous cell # 
    begin_match = 4216257 #

    n_matches = end_match - begin_match
    print(n_matches)
    full_run = 1

    #print(n_matches)

    if(full_run):
        match_ids = []
        player_ids = []
        player_numbers = []
        player_names = []
        
        for i in range(n_matches):
            match_id = end_match - i

            # it spends 99% of the time in this function
            match_id_tmp, player_id_tmp, player_number_tmp, player_name_tmp = extract_player_ids_from_single_file(match_id)

            match_ids.extend(match_id_tmp) # use extend instead of + for efficiency
            player_ids.extend(player_id_tmp)
            player_numbers.extend(player_number_tmp)
            player_names.extend(player_name_tmp)

            if i % 1000 == 0: 
            # write progress report
                print(i, end='')
                print(".", end='')

            if i % 1000 == 0:  
            # write data as hdf5 file     
                data = zip(match_ids, player_ids, player_numbers, player_names)

                df_player_ids_html = pd.DataFrame(data, columns = ['match_id', 'player_id', 'player_number', 'player_name'])

                df_player_ids_html.to_hdf(target, key='df_player_ids_html', mode='w')

        # write data as hdf5 file
        data = zip(match_ids, player_ids, player_numbers, player_names)

        df_player_ids_html = pd.DataFrame(data, columns = ['match_id', 'player_id', 'player_number', 'player_name'])
        df_player_ids_html.to_hdf(target, key='df_player_ids_html', mode='w')
    else:
        print("do nothing")
        # read from hdf5 file


#extract_player_ids(-1)

%load_ext line_profiler
#%lprun -f extract_player_ids extract_player_ids(100)

df_player_ids_html = pd.read_hdf('raw/df_player_ids_html_20221229_121951.h5')
df_player_ids_html.query('match_id == 4353201') # 4353065

# remove duplicates
df_player_ids_html[df_player_ids_html.duplicated(['player_id'], keep=False)]

df_player_ids_html.match_id.nunique()

df_player_ids_html.info()

df_player_ids_html = df_player_ids_html.drop_duplicates(subset='player_id', keep='first')

""" ## Extracting the match id - player id list from the match HTML files

This gives us for each match the participating player ids.
Each match contains on average 25 players.
So for 170K matches, we are looking at some 5M player records to create. 
This likely drops again as there will be lots of duplicates, as players are reused.

Processing the HTML for 100 matches takes 24 s, 
Processing the HTML for 1000 matches takes 5 min, 
for 150K we are at 750 min. So roughly 12 hours.
13K 725 min ???

After profiling, now 1000 matches takes 60s and scales (down from 5 min, and increasing due to memory problems).
The trick is to work with lists, and only in the end convert them to to a pandas dataframe.

Expect up to 3 hours """