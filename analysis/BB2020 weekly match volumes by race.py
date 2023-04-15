import pandas as pd
import numpy as np
import plotnine as p9

from mizani.formatters import date_format

# point this to the location of the HDF5 datasets
path_to_datasets = 'datasets/current/'

# FUMBBL matches
target = 'df_matches.h5'
df_matches = pd.read_hdf(path_to_datasets + target) 

# FUMBBL matches by team
target = 'df_mbt.h5'
df_mbt = pd.read_hdf(path_to_datasets + target) 

# FUMBBL inducements
target = 'inducements.h5'
inducements = pd.read_hdf(path_to_datasets + target) 

# top 26 most popular races in FUMBBL BB2020
top10 = (df_mbt
.query("division_name == 'Competitive'") # filter 
.groupby(['race_name'])
.agg(
    n_games = ('match_id', 'count')
)
.reset_index()
.sort_values('n_games',ascending = False)
.head(29)['race_name'])

divisions = [ 'Competitive']

res = (df_mbt
.query("division_name in @divisions and race_name in @top10")
.groupby(['division_name', 'race_name', 'week_date'])
.agg(
    n_games = ('match_id', 'count')
)
.reset_index()
.sort_values("n_games", ascending=False)
)

res2 = (df_mbt
.assign(race_name = 'total')
.query("division_name in @divisions")
.groupby(['division_name', 'race_name', 'week_date'])
.agg(
    n_games = ('match_id', 'count')
)
.reset_index()
.sort_values("n_games", ascending=False)
)

resx = pd.concat([res, res2], axis = 0)

my_plot = (p9.ggplot(data = resx.query("week_date < '2023-02-01'"), mapping = p9.aes(x = 'week_date', y = 'n_games', 
group = 'factor(race_name)', color = 'factor(race_name)'))
    + p9.geom_point() 
    + p9.geom_line() 
    + p9.expand_limits(y=[0,1])
    + p9.facet_wrap('race_name', scales = 'free_y', ncol = 3)
    + p9.scale_x_datetime(labels = date_format('%b'))   
    + p9.geom_vline(xintercept = '2021-09-01', color = "red")
    + p9.ggtitle("BB2020 Matches by race")
    + p9.theme(figure_size = (10, 12))
    + p9.ylab("Number of matches") 
    + p9.guides(color = False)
    + p9.theme(subplots_adjust={'wspace': 0.25})
)

my_plot.save(filename = 'match_volumes_by_race.png', height=10, width=12, units = 'in')
