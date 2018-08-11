import tabula
import pandas as pd
import os
import numpy as np
import re
import datetime

def find_divisorz(x): 
    if pd.notna(x):
        if 'NO' in x:
            #print(x,'is a special row')
            return True
        else:
            return False
    else: return True
        
def split_PIT(x,starters):
#     print(type(x['NO']))
    if x['NO'] not in starters:
        # print('x non in starters')
        if pd.notna(x['NO']):
            # print('x not null')
#        if x['NO'].notnull:
            if x['NO'][:-4] in starters:
                # print('correcting PIT')
                return pd.Series([x['NO'][:-4],'PIT',x['TIME'],x['LAP']],index = ["NO","GAP","TIME","LAP"])
            elif x['NO'][:-6] in starters:
                # print('correcting 1 LAP')
                return pd.Series([x['NO'][:-6],x['NO'][-5:],x['TIME'],x['LAP']],index = ["NO","GAP","TIME","LAP"])                
            else:
                # print('trashing it')
                return pd.Series([None, None, None, None],index = ["NO","GAP","TIME","LAP"])
        else:
            # print('it is a nan')
            return pd.Series([None, None, None, None],index = ["NO","GAP","TIME","LAP"])
    else:
        # print('proper')
        return pd.Series(x,index = ["NO","GAP","TIME","LAP"])

def split_TIMES(x,starters):
    if x['NO'] not in starters:
        return pd.Series([None, None, None, None],index = ["NO","GAP","TIME","LAP"])
    elif pd.isna(x['GAP']):
        return pd.Series([x['NO'],0,x['TIME'],x['LAP']],index = ["NO","GAP","TIME","LAP"])
    elif (' ' in str(x['GAP'])) & ('LAP' not in str(x['GAP'])):
        timez = x['GAP'].split()
        return pd.Series([x['NO'],timez[0],timez[1],x['LAP']],index = ["NO","GAP","TIME","LAP"])
    elif pd.isna(x['TIME']):
        return pd.Series([x['NO'],0,x['GAP'],x['LAP']],index = ["NO","GAP","TIME","LAP"])
    else:
        return x

def check_times(x):
    if re.search('[a-zA-Z]', x):
        return True
    else: 
        return False


def make_race_df(race_id):
    '''
    takes a race_id number as argument
    gets the appropriate csv's from '/race_frames'
    returns the main lap level df (NOT YET, another function? with added pit stop info and and the race level df_
    '''
    # def split_PIT(x):
    #     if x['NO'] not in starters:
    #         if pd.notna(x['NO']):
    #             if x['NO'][:-4] in starters:
    #                 return pd.Series([x['NO'][:-4],'PIT',x['TIME'],x['LAP']])
    #         else:
    #             return pd.Series([None, None, None, None])
    #     else:
    #         return x

    # def split_TIMES(x):
    #     if x['NO'] not in starters:
    #         return pd.Series([None, None, None, None])
    #     elif pd.isna(x['GAP']):
    #         return pd.Series([x['NO'],0,x['TIME'],x['LAP']])
    #     elif (' ' in str(x['GAP'])) & ('LAP' not in str(x['GAP'])):
    #         timez = x['GAP'].split()
    #         return pd.Series([x['NO'],timez[0],timez[1],x['LAP']])
    #     elif pd.isna(x['TIME']):
    #         return pd.Series([x['NO'],0,x['GAP'],x['LAP']])
    #     else:
    #         return x
    # print('race_id:', race_id)
    year = ref_df[ref_df['race_id'] == race_id]['year'].values[0]
    race_in_year = ref_df[ref_df['race_id'] == race_id]['year'].values[0]
    for _csv in csv_list:
        if (_csv.lower().endswith(('.csv'))) & ('_'+str(race_id)+'_' in _csv.lower()):
            _name = _csv[:-4]
            if ('history' in _csv.lower()):
                df = pd.read_csv('race_frames/'+_csv)
                # print(df.columns)
                # df.rename(columns = {'NO':'NO.0','GAP':'GAP.0','TIME':'TIME.0'},inplace=True)
                df.columns=['Unnamed: 0', 'NO.0', 'GAP.0', 'TIME.0', 'NO.1', 'GAP.1', 'TIME.1', 'NO.2',
       'GAP.2', 'TIME.2', 'NO.3', 'GAP.3', 'TIME.3', 'NO.4', 'GAP.4',
       'TIME.4']
                # divisorz = df.loc[df['NO.0']=='NO'].index
                divisorz = df.loc[df['NO.0'].apply(find_divisorz)].index
                # slicing the history dataframe horizontally
# slicing the history dataframe horizontally
                previous_divisor = -1
                d={}
                for _id,_val in enumerate(divisorz):
                #     print (_id,_val)
                    d['df_'+str(_id)] = df.loc[previous_divisor+1:_val-1]
                    previous_divisor = _val
                    div_counter = _id
                last_id = div_counter + 1
                d['df_'+str(last_id)] = df.loc[previous_divisor+1:]
                # starters = d['df_1']['NO.0'].unique()
                laps_dfs=[]
                d1={}
                for j in range(len(divisorz)+1):
                    # print('j is ', j)
                    for i in [0,1,2,3,4]:
                        # print('i is ', i)
                        # print('doing lap',j*5+(i+1))
                        if j*5+(i+1):
                            if j*5+(i+1)==1:
                                if year==2016:
                                    starters = starters_2016
                                elif year==2017:
                                    starters = starters_2017
                            # print('race_id:', race_id)
                            # print('horizontal slice:',j)
                            # print('vertical slice:',i)                        
                            # Take the horizontal slices and slice them vertically into laps 
                            d1['df_lap_'+str(j*5+(i+1))] = d['df_'+str(j)][['NO.'+str(i),'GAP.'+str(i),'TIME.'+str(i)]]
                            # print(print(d1['df_lap_'+str(j*5+(i+1))].columns))                           
                            # add lap feature 
                            d1['df_lap_'+str(j*5+(i+1))]['lap'] = str(j*5+(i+1))
                            # uniforming column names
                            d1['df_lap_'+str(j*5+(i+1))].columns = ["NO","GAP","TIME","LAP"]
                            # putting 0 were 'GAP' is none (!!WORKAROUND!!the first row of a frame appear to behave differently than 
                            # other rows resulting in adding new columns to the data in an incompatible way. 
                            # considering a bug report to pandas developers
                            d1['df_lap_'+str(j*5+(i+1))]["GAP"].fillna(0,inplace=True)
                            # removing empty rows (where racing number is empty)
                            d1['df_lap_'+str(j*5+(i+1))] = d1['df_lap_'+str(j*5+(i+1))][d1['df_lap_'+str(j*5+(i+1))]["NO"].notnull()]
                            # solving the problem of 'PIT' value being collected in the 'NO' field
                            # d1['df_lap_'+str(j*5+(i+1))] = d1['df_lap_'+str(j*5+(i+1))].apply(split_PIT, axis =1)
                            d1['df_lap_'+str(j*5+(i+1))] = d1['df_lap_'+str(j*5+(i+1))].transform(lambda x: split_PIT(x,starters), axis =1)
                #             # putting back the right names
                            # print(d1['df_lap_'+str(j*5+(i+1))].columns)
                            d1['df_lap_'+str(j*5+(i+1))].columns = ["NO","GAP","TIME","LAP"]
                #             # removing empty rows (where racing number is empty).
                            # print(d1['df_lap_'+str(j*5+(i+1))].columns)
                            d1['df_lap_'+str(j*5+(i+1))] = d1['df_lap_'+str(j*5+(i+1))][d1['df_lap_'+str(j*5+(i+1))]['NO'].notnull()]
                #             # solving the problem of 'NO' and 'GAP' fields merging
                            # d1['df_lap_'+str(j*5+(i+1))] = d1['df_lap_'+str(j*5+(i+1))].apply(split_TIMES, axis =1)
                            d1['df_lap_'+str(j*5+(i+1))] = d1['df_lap_'+str(j*5+(i+1))].transform(lambda x: split_TIMES(x,starters), axis =1)
                #             # putting back the right names
                            d1['df_lap_'+str(j*5+(i+1))].columns = ["NO","GAP","TIME","LAP"]
                #             # removing empty rows (where racing number is empty).
                            d1['df_lap_'+str(j*5+(i+1))] = d1['df_lap_'+str(j*5+(i+1))][d1['df_lap_'+str(j*5+(i+1))]["NO"].notnull()]                            
                            # if j*5+(i+1)==1:
                            #     starters = d['df_lap_1']['NO'].unique()
                            laps_dfs.append(d1['df_lap_'+str(j*5+(i+1))])
                            
                race_df = pd.concat(laps_dfs,ignore_index=True)
                race_df['race_id'] = race_id

                race_df.drop(race_df.index[race_df['NO'].isna()],axis=0, inplace=True)

                race_df['NO'] = race_df['NO'].astype('int64')

                race_df['LAP'] = race_df['LAP'].astype('int64')

                finishers = race_df[race_df['LAP'] == max(race_df['LAP'])]['NO'].unique()
                finishers = finishers[pd.notna(finishers)]
                
                ###checking times
                _mask = race_df['TIME'].apply(check_times)#.values[0]#.split(' ')[0:2]
                ###correcting only problem
                race_df['TIME'][_mask] = '2:11.365'
                race_df['GAP'][_mask] = '1 LAP'

                race_df.to_csv('clean_frames/race_df_'+str(race_id)+'.csv')

            # if 'stop' in _csv.lower():                
            elif 'stop' in _csv.lower():
                pit_stop_df = pd.read_csv('race_frames/'+_csv)
                
                pit_stop_df['NO'] = pit_stop_df['NO'].astype('str')

                pit_stop_df['LAP'] = pit_stop_df['LAP'].astype('str')

                pit_stop_df = pit_stop_df[pit_stop_df['NO']!='NO']

                pit_stop_df.rename(columns = {'S  T  OP':'STOP'},inplace=True)

                pit_stop_df['NO'] = pit_stop_df['NO'].astype('int64')

                pit_stop_df['LAP'] = pit_stop_df['LAP'].astype('int64')
                pit_stop_df.to_csv('clean_frames/pit_stop_df_'+str(race_id)+'.csv')
            # print(starters)
            starters = starters[pd.notna(starters)].astype('int64')
            

    
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
    counter = 34
    ref_df = pd.read_csv('which_race.csv', header=0)
    pdf_list = os.listdir('raw_data')
    csv_list = os.listdir('race_frames')
    starters_2016 = np.array(["5","7","11","27","8","21","14","47","22","6","44","88","31","94","3","26","33","20","30","9","12","33","26","55","19","77"])
    starters_2017 = np.array(["5","7","11","31","8","20","2","14","22","44","77","3","33","27","30","55","9","36","94","26","10","28","39","55","26","10","18","19","40"])
    for j in range(counter):
        # print('race_id',j)
        #             pdf_to_csv(j)
        make_race_df(j)
