import tabula
import pandas as pd
import os
import numpy as np
import re
import datetime


def make_race_df(race_id):
    '''
    takes a race_id number as argument
    gets the appropriate csv's from '/race_frames'
    returns the main lap level df (NOT YET, another function? with added pit stop info and and the race level df_
    '''
    def split_PIT(x):
        if x['NO'] not in starters:
            if pd.notna(x['NO']):
                if x['NO'][:-4] in starters:
                    return pd.Series([x['NO'][:-4],'PIT',x['TIME'],x['LAP']])
            else:
                return pd.Series([None, None, None, None])
        else:
            return x

    def split_TIMES(x):
        if x['NO'] not in starters:
            return pd.Series([None, None, None, None])
        elif pd.isna(x['GAP']):
            return pd.Series([x['NO'],0,x['TIME'],x['LAP']])
        elif (' ' in str(x['GAP'])) & ('LAP' not in str(x['GAP'])):
            timez = x['GAP'].split()
            return pd.Series([x['NO'],timez[0],timez[1],x['LAP']])
        elif pd.isna(x['TIME']):
            return pd.Series([x['NO'],0,x['GAP'],x['LAP']])
        else:
            return x

    year = ref_df[ref_df['race_id'] == race_id]['year'].values[0]
    race_in_year = ref_df[ref_df['race_id'] == race_id]['year'].values[0]
    for _csv in csv_list:
        if (_csv.lower().endswith(('.csv'))):
            _name = _csv[:-4]
            if ('history' in _csv.lower()):
                exec('df = pd.read_csv("race_frames/'+_csv+'")')
                df.rename(columns = {'NO':'NO.0','GAP':'GAP.0','TIME':'TIME.0'},inplace=True)
                divisorz = df.loc[df['NO.0']=='NO'].index
                # slicing the history dataframe horizontally
                previous_divisor = -1
                for _id,_val in enumerate(divisorz):
                    exec('df_'+str(_id)+'= df.loc[previous_divisor+1:_val-1]' )
                    previous_divisor = _val
                    div_counter = _id
                last_id = div_counter + 1
                exec('df_'+str(last_id)+'= df.loc[previous_divisor+1:]' )
                starters = df_1['NO.0'].unique()
                laps_dfs=[]
                for j in range(len(divisorz)+1):
                #     print('j is ', j)
                    for i in [0,1,2,3,4]:
                #         print('i is ', i)
                #         print('doing lap',j*5+(i+1))
                        if j*5+(i+1):
                            # Take the horizontal slices and slice them vertically into laps 
                            exec('df_lap_'+str(j*5+(i+1))+' = df_'+str(j)+'[["NO.'+str(i)+'","GAP.'+str(i)+'","TIME.'+str(i)+'"]]')
                            # add lap feature 
                            exec('df_lap_'+str(j*5+(i+1))+'["lap"] = '+str(j*5+(i+1)))
                            # uniforming column names
                            exec('df_lap_'+str(j*5+(i+1))+'.columns = ["NO","GAP","TIME","LAP"]')
                            # putting 0 were 'GAP' is none (!!WORKAROUND!!the first row of a frame appear to behave differently than 
                            # other rows resulting in adding new columns to the data in an incompatible way. 
                            # considering a bug report to pandas developers
                            exec('df_lap_'+str(j*5+(i+1))+'["GAP"].fillna(0,inplace=True)')
                            # removing empty rows (where racing number is empty)
                            exec('df_lap_'+str(j*5+(i+1))+' = df_lap_'+str(j*5+(i+1))+'[df_lap_'+str(j*5+(i+1))+'["NO"].notnull()]' )
                            # solving the problem of 'PIT' value being collected in the 'NO' field
                            exec('df_lap_'+str(j*5+(i+1))+' = df_lap_'+str(j*5+(i+1))+'.apply(split_PIT, axis =1)')
                            # putting back the right names
                            exec('df_lap_'+str(j*5+(i+1))+'.columns = ["NO","GAP","TIME","LAP"]')
                            # removing empty rows (where racing number is empty).
                            exec('df_lap_'+str(j*5+(i+1))+' = df_lap_'+str(j*5+(i+1))+'[df_lap_'+str(j*5+(i+1))+'["NO"].notnull()]' )            
                            # solving the problem of 'NO' and 'GAP' fields merging
                            exec('df_lap_'+str(j*5+(i+1))+' = df_lap_'+str(j*5+(i+1))+'.apply(split_TIMES, axis =1)')
                            # putting back the right names
                            exec('df_lap_'+str(j*5+(i+1))+'.columns = ["NO","GAP","TIME","LAP"]')
                            # removing empty rows (where racing number is empty).
                            exec('df_lap_'+str(j*5+(i+1))+' = df_lap_'+str(j*5+(i+1))+'[df_lap_'+str(j*5+(i+1))+'["NO"].notnull()]' )            
                            # putting all temp dataframes in a list
                            exec('laps_dfs.append(df_lap_'+str(j*5+(i+1))+')')
                race_df = pd.concat(laps_dfs,ignore_index=True)

                race_df['race_id'] = race_id

                race_df.drop(race_df.index[race_df['NO'].isna()],axis=0, inplace=True)

                race_df['NO'] = race_df['NO'].astype('int64')

                race_df['LAP'] = race_df['LAP'].astype('int64')

                starters = starters.astype('int64')

                finishers = race_df[race_df['LAP'] == max(race_df['LAP'])]['NO'].unique()
                
            elif ('stop' in _csv.lower()):
                exec('pit_stop_df = pd.read_csv("race_frames/'+_csv+'")')
                pit_stop_df = pit_stop_df[pit_stop_df['NO']!='NO']

                pit_stop_df.rename(columns = {'S  T  OP':'STOP'},inplace=True)

                pit_stop_df['NO'] = pit_stop_df['NO'].astype('int64')

                pit_stop_df['LAP'] = pit_stop_df['LAP'].astype('int64')
# def pdf_to_csv(race_id):
#     '''
#     takes a race_id number as argument
#     gets the appropriate pdf files from '/raw_data'
#     read them into df's
#     saves the df's into csvs in '/race_frames'
#     '''
#     ref_df = pd.read_csv('which_race.csv', header=0)
#     year = ref_df[ref_df['race_id'] == race_id]['year'].values[0]
#     race_in_year = ref_df[ref_df['race_id']
#                           == race_id]['race_in_year'].values[0]
#     correction = len(str(race_in_year))
#     for _pdf in os.listdir('raw_data'):
#         if (_pdf.lower().endswith(('.pdf'))) & ('jpg' not in _pdf.lower()) & (_pdf.lower().startswith(str(year))) & (_pdf.lower()[5:].startswith(str(race_in_year))) & (('history' in _pdf.lower()) | ('stop' in _pdf.lower())):
#             #         if (_pdf.lower().endswith(('.pdf'))) & ('jpg' not in _pdf.lower()) & (_pdf.lower().startswith(str(year))) & (_pdf.lower()[5:].startswith(str(race_in_year))):
#             #         print(_pdf[6+correction:])
#             _name = _pdf[6+correction:-4]+'_'+str(race_id)+'_df'
#             exec(_name+" = tabula.read_pdf('raw_data/'+_pdf,pages='all')")
#             exec(_name+'["race_id"] = race_id')
#             exec(_name+".to_csv('race_frames/'+_name+'.csv')")
#     #         print(_name)
#     return None


if __name__ == "__main__":
    ref_df = pd.read_csv('which_race.csv', header=0)
    pdf_list = os.listdir('raw_data')
    csv_list = os.listdir('race_frames')
    for j in range(17, 19):
        #             pdf_to_csv(j)
        make_race_df(j)
