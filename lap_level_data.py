import pandas as pd
import os
import numpy as np
import re
import datetime


def distances(x):
    return x.values[:, None]-x.values


ref_df = pd.read_csv('which_race.csv', header=0)
csv_list = os.listdir('clean_frames')
counter = 34

d2 = {}
d3 = {}
d4 = {}
for race_id in range(counter):
    #     print(race_id)
    d2['race_df_' +
        str(race_id)] = pd.read_csv('clean_frames/race_df_'+str(race_id)+'.csv')
    d3['pit_stop_df_' +
        str(race_id)] = pd.read_csv('clean_frames/pit_stop_df_'+str(race_id)+'.csv')
    race_df = d2['race_df_'+str(race_id)]
    # dfone = pd.concat(d2.values())
    pit_stop_df = d3['pit_stop_df_'+str(race_id)]

    race_df['TIME'] = race_df['TIME'].apply(
        lambda x: int(x.split(':')[0])*60 + float(x.split(':')[1]))

    race_df['cumtime'] = race_df[['TIME', 'NO']
                                 ].groupby('NO').cumsum(skipna=True)

    race_df.drop(columns=['Unnamed: 0'], inplace=True)

    pit_stop_df.drop(
        columns=['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 6'], inplace=True)

    last_lap = max(race_df['LAP'])

    race_df.set_index(['NO', 'LAP'], inplace=True)

    race_df = race_df[~race_df.index.duplicated(keep='first')]

    d_gaps = {}
    for i in range(0, last_lap):
        lap = i+1
        gaps_df = pd.DataFrame(distances(race_df['TIME'][race_df.index.get_level_values(1) == lap]), columns=list(race_df.index.get_level_values(
            0)[race_df.index.get_level_values(1) == lap].values), index=race_df.index.get_level_values(0)[race_df.index.get_level_values(1) == lap].values)

        gaps_df['LAP'] = lap

        gaps_df.reset_index(level=0, inplace=True)

        gaps_df.rename({'index': 'NO'}, axis='columns', inplace=True)

    #     gaps_df.set_index(['NO','LAP'], inplace=True)

        d_gaps['gaps_df_lap_'+str(lap)] = gaps_df

    #     gaps_df.drop(columns = ['Unnamed: 0'], inplace=True)

    for i in range(0, last_lap):
        lap = i+1
        gaps_df = d_gaps['gaps_df_lap_'+str(lap)]
        gaps_df.set_index(['NO', 'LAP'], inplace=True)
        if lap == 1:
            race_df = race_df.merge(gaps_df, on=['NO', 'LAP'], how="outer")
        else:
            # , overwrite=True, filter_func=None, raise_conflict=False)
            race_df.update(gaps_df, join='left')

    new_df = race_df.merge(pit_stop_df, on=['NO', 'LAP'], how='outer')
    # new_df.drop(columns = ['Unnamed: 0','Unnamed: 0'], inplace=True)

    new_df.set_index(['NO', 'LAP'], inplace=True)

    # new_df['stop_count'] = np.nan
    new_df['stop_count'] = new_df['STOP']
    # filling the first lap stop_count0s
    new_df['stop_count'][(new_df.index.get_level_values(1)
                          == 1) & (new_df['STOP'] != 1)] = 0

    new_df['d_stop'] = new_df['STOP'] > 0
    new_df['target'] = np.nan

    for j in new_df.index.get_level_values(0).unique():
        x = pd.concat([new_df['stop_count'][new_df.index.get_level_values(
            0) == j].unstack(0).ffill().stack(0)], axis=1).swaplevel()
        x.columns = ['stop_count']
        new_df.update(x, join='left')
        new_df['target'][(new_df.index.get_level_values(0) == j)] = new_df['d_stop'][(
            new_df.index.get_level_values(0) == j)].shift(-1)
    d4['lap_level_df_'+str(race_id)] = new_df

full_df = pd.concat([v for k, v in d4.items()], ignore_index=False)
full_df.to_csv('full_data.csv')
