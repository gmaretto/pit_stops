import pandas as pd
import os
import numpy as np
import re
import datetime


def distances(x):
    return x.values[:, None]-x.values


def reset_lap_counter(lap, pits):
    return lap - np.append(np.intersect1d(pits, np.arange(1, lap)), 0).max()


def pit_time(x):
    if isinstance(x, float):
        return x
    else:
        if ':' in x:
            return int(x.split(':')[0])*60 + float(x.split(':')[1])
        else:
            return float(x)


ref_df = pd.read_csv('which_race.csv', header=0)
driver_df = pd.read_csv('drivers_numbers.csv')
source_conflict = [0, 14, 20, 25]
tire_csvs = np.intersect1d(np.array(range(0, 34)), [int(
    x[:-4]) for x in os.listdir('stints_frames')])
csv_list = os.listdir('clean_frames')
counter = 34
good_races = np.setdiff1d(tire_csvs, source_conflict)

d2 = {}
d3 = {}
d4 = {}
d5 = {}
# for race_id in range(counter):
for race_id in good_races:
    print(race_id)
    d2['race_df_' +
        str(race_id)] = pd.read_csv('clean_frames/race_df_'+str(race_id)+'.csv')
    d3['pit_stop_df_' +
        str(race_id)] = pd.read_csv('clean_frames/pit_stop_df_'+str(race_id)+'.csv')
    race_df = d2['race_df_'+str(race_id)]
    # dfone = pd.concat(d2.values())
    pit_stop_df = d3['pit_stop_df_'+str(race_id)]
# turning timestrings in seconds (float)
    race_df['TIME'] = race_df['TIME'].apply(
        lambda x: int(x.split(':')[0])*60 + float(x.split(':')[1]))
# creating cumulative times to construct gaps at every lap
    race_df['cumtime'] = race_df[['TIME', 'NO']
                                 ].groupby('NO').cumsum(skipna=True)

    race_df.drop(columns=['Unnamed: 0'], inplace=True)

    pit_stop_df.drop(
        columns=['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 6'], inplace=True)

    # last_lap = max(race_df['LAP'])

    race_df.set_index(['NO', 'LAP'], inplace=True)

    race_df = race_df[~race_df.index.duplicated(keep='first')]

    new_index = [x for x in range(
        1, race_df.index.get_level_values('LAP').nunique()+1)]

    reindex_d = dict(
        zip(list(race_df.index.get_level_values('LAP').unique()), new_index))

    race_df.rename(index=reindex_d, level=1, inplace=True)

    last_lap = race_df.index.get_level_values('LAP').nunique()
    race_df['last_lap'] = last_lap
    # race_df['temp_lap'] =  race_df['LAP']
    race_df['temp_lap'] = race_df.index.get_level_values('LAP')

    race_df['progress'] = race_df.index.get_level_values(
        'LAP')/(race_df.index.get_level_values('LAP').nunique())
# constructing distance matrices
    d_gaps = {}
    for i in range(0, last_lap):
        lap = i+1
        gaps_df = pd.DataFrame(distances(race_df['TIME'][race_df.index.get_level_values('LAP') == lap]), columns=list(race_df.index.get_level_values(
            0)[race_df.index.get_level_values('LAP') == lap].values), index=race_df.index.get_level_values('NO')[race_df.index.get_level_values('LAP') == lap].values)

        gaps_df['LAP'] = lap

        gaps_df.reset_index(level=0, inplace=True)

        gaps_df.rename({'index': 'NO'}, axis='columns', inplace=True)

    #     gaps_df.set_index(['NO','LAP'], inplace=True)

        d_gaps['gaps_df_lap_'+str(lap)] = gaps_df


# merging gaps/distances data in the main df
    for i in range(0, last_lap):
        lap = i+1
        gaps_df = d_gaps['gaps_df_lap_'+str(lap)]
        gaps_df.set_index(['NO', 'LAP'], inplace=True)
        if lap == 1:
            race_df = race_df.merge(gaps_df, on=['NO', 'LAP'], how="outer")
        else:
            race_df.update(gaps_df, join='left')

    new_df = race_df.merge(pit_stop_df, on=['NO', 'LAP'], how='outer')
    # new_df.drop(columns = ['Unnamed: 0','Unnamed: 0'], inplace=True)

    new_df.set_index(['NO', 'LAP'], inplace=True)

    new_df['TOTAL TIME'][new_df['TOTAL TIME'].notna(
    )] = new_df['TOTAL TIME'][new_df['TOTAL TIME'].notna()].apply(pit_time)

    new_df['mean_pit'] = np.mean(
        new_df['TOTAL TIME'][new_df['TOTAL TIME'].notna()])

    new_df['median_pit'] = np.median(
        new_df['TOTAL TIME'][new_df['TOTAL TIME'].notna()])

# creating some useful pit stop features (and the target variable) and merging them back in the main dataset
    new_df['d_stop'] = new_df['STOP'] > 0
    new_df['target'] = np.nan
    new_df['stop_count'] = new_df['STOP']

# filling the first lap stop_count0s
    new_df['stop_count'][(new_df.index.get_level_values('LAP')
                          == 1) & (new_df['STOP'] != 1)] = 0
    new_df['stint'] = new_df['STOP']
    new_df['laps_since_pit'] = new_df.index.get_level_values('LAP')
    for _num in new_df.index.get_level_values('NO').unique():

        new_df['target'][(new_df.index.get_level_values('NO') == _num)] = new_df['d_stop'][(
            new_df.index.get_level_values('NO') == _num)].shift(-1)

        pits = new_df.index.get_level_values('LAP')[(new_df['d_stop']) & (
            new_df.index.get_level_values('NO') == _num)].values
        new_df['stop_count'][new_df.index.get_level_values(
            'NO') == _num] = new_df['stop_count'][new_df.index.get_level_values('NO') == _num].ffill()
        new_df['stint'][new_df.index.get_level_values(
            'NO') == _num] = new_df['STOP'][new_df.index.get_level_values('NO') == _num].bfill().ffill()
        new_df['stint'][new_df.index.get_level_values('NO') == _num] = new_df['stint'][new_df.index.get_level_values(
            'NO') == _num].fillna(new_df['stint'][new_df.index.get_level_values('NO') == _num].max()+1)
        new_df['laps_since_pit'][new_df.index.get_level_values('NO') == _num] = new_df['laps_since_pit'][new_df.index.get_level_values(
            'NO') == _num].apply(lambda x: reset_lap_counter(x, pits))
        # print('race_id', race_id)
        # print('lap', lap)
        # print('stint', stint)
        # new_df['stint'] = new_df['stop_count'].astype('int32')+1
    # storing new dfs
    # d4['lap_level_df_'+str(race_id)] = new_df

    tires_df = pd.read_csv('stints_frames/'+str(race_id)+'.csv', header=None)
    for i in range(1, tires_df.shape[1]):
        tires_df.rename(columns={i: 'stint_'+str(i)}, inplace=True)
        if i > 0:
            tires_df['stint_'+str(i)][tires_df['stint_'+str(i)].notna()] = tires_df['stint_'+str(
                i)][tires_df['stint_'+str(i)].notna()].apply(np.vectorize(lambda x: x.split(' (')[0]))
    tires_df.rename(columns={0: 'Driver'}, inplace=True)
    tires_df = tires_df.merge(driver_df, how='left', on='Driver')
    d5['tires_df_'+str(race_id)] = tires_df
    tires_df.to_csv('clean_frames/tires_df_'+str(race_id)+'.csv')

    new_df = new_df.merge(tires_df, how='outer', on='NO')

    new_df['tyres'] = np.nan
    print('race_id', race_id)
    for stint in new_df['stint'][new_df['stint'].notna()].unique():
        new_df['tyres'][new_df['stint'] == stint] = new_df['stint_' +
                                                           str(int(stint))][new_df['stint'] == stint]
    d4['lap_level_df_'+str(race_id)] = new_df

# merging them and saving them
full_df = pd.concat([v for k, v in d4.items()], ignore_index=False)
full_df.to_csv('full_data.csv')
