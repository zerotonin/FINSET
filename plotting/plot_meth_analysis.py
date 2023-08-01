# Importing necessary libraries
import pandas as pd
import os
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import scipy.stats as stats


parent_dir = '/home/bgeurten/ethoVision_database/'
file_name = 'collated_data.csv'

file_positions = []

# Iterate over all subfolders and files
for root, dirs, files in os.walk(parent_dir):
    for file in files:
        # Check if the file name matches the desired file name
        if file == file_name:
            # Get the file position (full path)
            file_position = os.path.join(root, file)
            # Append the file position to the list
            file_positions.append(file_position)

drug_admin_df = pd.read_csv('/home/bgeurten/ethoVision_database/drug_administration.csv')
column_strings = ['Freezing_fraction', 'Tigmotaxis_fraction', 'Latency_to_top_s', 
                    'boldness_fraction', 'frantic_fraction', 'stress_fraction','stress_score'] 

subject_list =list()
for i,row in drug_admin_df.iterrows():
    

    # create identifiable string pattern
    search_str=f'tankNum_{str(row.Tank_nr).zfill(2)}__fishID_{row.ID}'
    # look for corresponding file
    matching_positions = [s for s in file_positions if search_str in s]
    file_position = matching_positions[0]
    # load collated data
    subject_df = pd.read_csv(file_position)

    # get the correct indices for drug administration
    if row.Drug_day == 1:
        pre_index = [i for i in subject_df.index[-4:-2]]
        admin_index = subject_df.index[-2]
        post_index = subject_df.index[-1]
        
    elif row.Drug_day == 2:
        pre_index = [i for i in subject_df.index[-4:-1]]
        admin_index = subject_df.index[-1]
        post_index = None
    else:
        raise ValueError('Meth was not administered at the first or second day!')




    subject_dict = dict()

    for col_str in column_strings:
        subject_dict[f'pre_{col_str}']=subject_df.loc[pre_index,col_str].mean()
        subject_dict[f'drug_{col_str}']=subject_df.loc[admin_index,col_str]
        if post_index is not None:
            subject_dict[f'post_{col_str}']=subject_df.loc[post_index,col_str]
        else:
            subject_dict[f'post_{col_str}']= np.NAN

    subject_dict['ID'] =  row.ID
    subject_dict['sex'] =  row.sex
    subject_dict['tank_num'] =  row.Tank_nr
    subject_list.append(subject_dict)
            

drug_df = pd.DataFrame(subject_list)


time = ['pre' for i in range(len(drug_df))]
time+=['meth' for i in range(len(drug_df))]
time+=['post' for i in range(len(drug_df))]
sex = drug_df.sex.to_list()
sex+=drug_df.sex.to_list()
sex+=drug_df.sex.to_list()

for col_str in column_strings:
    data = drug_df.loc[:,f'pre_{col_str}'].to_list()
    data+=drug_df.loc[:,f'drug_{col_str}'].to_list()
    data+=drug_df.loc[:,f'post_{col_str}'].to_list()


    plot_df = pd.DataFrame({'time':time,col_str:data,'sex':sex})
    f = plt.figure(figsize=(10, 6))
    sns.boxplot(x="time", y=col_str,
                hue="sex", palette=["b", "r"],
                data=plot_df, notch=True)
    sns.despine(offset=10, trim=True)
    f.savefig(f'/home/bgeurten/ethoVision_database/meth_figures/{col_str}.svg')
plt.show()

