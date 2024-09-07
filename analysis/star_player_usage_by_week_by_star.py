import pandas as pd
import numpy as np
import plotnine as p9

# point this to the location of the HDF5 datasets
path_to_datasets = 'datasets/current/'

# FUMBBL matches
target = 'df_matches.csv'
df_matches = pd.read_csv(path_to_datasets + target) 

# FUMBBL inducements
target = 'inducements.csv'
inducements = pd.read_csv(path_to_datasets + target) 

# top 10 star players in BB2020
top10 = (inducements
.merge(df_matches[['match_id', 'division_name', 'week_date']], how='left', on='match_id')
.query("star_player == 1 and division_name == 'Competitive'")
.groupby(['inducements'])
.agg(
    n_games = ('match_id', 'count')
)
.reset_index()
.sort_values('n_games',ascending = False)
.head(10)['inducements'])

res = (inducements
.merge(df_matches[['match_id', 'division_name', 'week_date']], how='left', on='match_id')
.query("star_player == 1 and division_name == 'Competitive' and inducements in @top10")
.groupby(['inducements', 'week_date'])
.agg(
    n_games = ('match_id', 'count')
)
.reset_index())

# week totals over all star players
res2 = (inducements
.merge(df_matches[['match_id', 'division_name', 'week_date']], how='left', on='match_id')
.assign(inducements = 'total')
.query("star_player == 1 and division_name == 'Competitive'")
.groupby(['inducements', 'week_date'])
.agg(
    n_games = ('match_id', 'count')
)
.reset_index())

res = pd.concat([res, res2], axis = 0)

my_plot = (p9.ggplot(data = res, mapping = p9.aes(x = 'week_date', y = 'n_games', 
group = 'factor(inducements)', color = 'factor(inducements)'))
    + p9.geom_point() 
    + p9.geom_line() 
    + p9.expand_limits(y=[0,1])
    + p9.scale_size_area()
    + p9.geom_vline(xintercept = '2021-09-01', color = "red")
    + p9.ggtitle("FUMBBL BB2020 Star player usage over time")
    + p9.theme(figure_size = (10, 6))
    + p9.ylab("matches"))

my_plot.save(filename = 'star_players_by_week.png', height=6, width=10, units = 'in')