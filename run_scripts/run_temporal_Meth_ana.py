import pandas as pd
from data_handlers.EthoVisionReader import EthoVisionReader
import sqlite3
import os
from pathlib import Path
from tqdm import tqdm

def get_all_tra_files(folder):
    """
    Searches for all .csv files with the name ending in "trajectory_data.csv" 
    in the given folder and its subdirectories.

    This function is useful for aggregating trajectory data from multiple 
    subdirectories within a specified folder. The search is non-recursive 
    and will return a list of all matching files within the immediate 
    directory and its subdirectories.

    Args:
        folder (str): The path to the folder to search for .csv files that 
                      end with "trajectory_data.csv".

    Returns:
        list: A list of .csv file paths with the name ending in "trajectory_data.csv" 
              found in the folder and its subdirectories.
    """
    trajectory_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith("trajectory_data.csv"):
                trajectory_files.append(os.path.join(root, file))
    return trajectory_files


def check_application_days(df_tra):    
    """
    Checks if days 28 and 29 are present in the 'Day_number' column of the given DataFrame.

    This function is used to verify whether a given DataFrame contains the specific 
    days 28 and 29 in the 'Day_number' column. The function returns a boolean value 
    indicating the presence or absence of these particular days. It is particularly useful 
    in scenarios where the existence of data for these days is critical for further analysis 
    or processing.

    Args:
        df_tra (pandas.DataFrame): The DataFrame containing a 'Day_number' column, 
                                   which holds numerical day values.

    Returns:
        bool: Returns True if days 28 and 29 are present in the 'Day_number' column,
              otherwise returns False.

    Example:
        >>> df = pd.DataFrame({'Day_number': [27, 28, 29, 30]})
        >>> check_application_days(df)
        True
    """
    if  28 and 29 in df_tra.Day_number.unique():
        return(True)
    else:
        return(False)
    
def check_drug_application_record(df_drug_admin, df_tra):
    # Using `.loc` to filter rows that meet both conditions.
    matching_rows = df_drug_admin.loc[(df_drug_admin['Tank_nr'] == df_tra['Tank_number'][0]) & 
                                    (df_drug_admin['ID'] == df_tra['ID'][0])]

    # Check if any such rows exist.
    if matching_rows.empty:
        return False
    else:
       return True
    
def reduce_to_drug_treatment(df_tra,df_drug_admin):
    matching_rows = df_drug_admin.loc[(df_drug_admin['Tank_nr'] == df_tra['Tank_number'][0]) & 
                                    (df_drug_admin['ID'] == df_tra['ID'][0])]
    if matching_rows.Drug_day.iloc[0] == 2:
        treatment_day = 29
        control_day = 28
    else: 
        treatment_day = 28
        control_day = 29

    df_tra = df_tra.loc[df_tra.Day_number > 27,:].copy()
    df_tra['treatment'] = 'control'
    df_tra.loc[df_tra.Day_number == treatment_day,'treatment'] = 'application'

    return df_tra

def reduce_tenmporal_resolution(df,bin_size_sec=10):

    # Create a new column 'Unique_ID' combining 'ID' and 'Tank_number'
    df['Unique_ID'] = df['ID'].astype(str) + "_" + df['Tank_number'].astype(str)

    df['Trial_time_s'] = pd.to_numeric(df['Trial_time_s'], errors='coerce')

    # Create a new column that divides the trial time by bin_size_sec and rounds to the nearest integer
    df['Time_bin'] = (df['Trial_time_s'] // bin_size_sec) 

    # Group by the new time bin, treatment, sex, tank number, and ID, then aggregate
    agg_dict = {
        'tigmo_taxis': 'sum',
        'freezing': 'sum',
        'stress': 'sum',
        'frantic': 'sum',
        'boldness': 'sum',
        'speed_cmPs': 'mean'
    }



    df_agg = df.groupby(['Unique_ID', 'treatment', 'Time_bin', 'Sex']).agg(agg_dict).reset_index()

    return df_agg


# ╔══════════════════════════════════════════╗
# ║                  File I/O                ║
# ╚══════════════════════════════════════════╝

parent_dir = "/home/bgeurten/ethoVision_database"
target_csv = os.path.join(parent_dir,'drug_fish_data.csv')
bin_size_sec = 60
if os.path.isfile(target_csv): 
    drug_df = pd.read_csv(target_csv)
else:
    # read drug administration days
    df_drug_admin = pd.read_csv(os.path.join(parent_dir,'drug_administration.csv'))
    # get all trajectory files 
    tra_files = get_all_tra_files(parent_dir)

    all_drug_recordings = list()

    for tra_file in tqdm(tra_files, desc = "Reading trajectories"):
        go_on = True
        df_tra = pd.read_csv(tra_file)
        go_on = check_application_days(df_tra)
        go_on = go_on and check_drug_application_record(df_drug_admin,df_tra)
        if go_on:
            df_agg = reduce_tenmporal_resolution(reduce_to_drug_treatment(df_tra,df_drug_admin),bin_size_sec)
            all_drug_recordings.append(df_agg)

    drug_df = pd.concat(all_drug_recordings)
    drug_df.to_csv(target_csv,index=False)

# ╔══════════════════════════════════════════╗
# ║                  PLOTTING                ║
# ╚══════════════════════════════════════════╝


import seaborn as sns
import matplotlib.pyplot as plt
grouped_df= drug_df

fps = 25
grouped_control_df = grouped_df[grouped_df['treatment'] == 'control']
grouped_application_df = grouped_df[grouped_df['treatment'] == 'application']
merged_df = pd.merge(grouped_control_df, grouped_application_df, on=['Unique_ID', 'Time_bin', 'Sex'], suffixes=('_control', '_application'))#, how= 'outer')
y_columns = ['tigmo_taxis', 'freezing', 'stress', 'boldness','frantic']

for column in y_columns:
    merged_df[f'{column}_difference'] = (merged_df[f'{column}_application'] - merged_df[f'{column}_control'])/(fps) #/ (merged_df[f'{column}_application'] + merged_df[f'{column}_control'])

merged_df[f'speed_cmPs_difference'] = (merged_df[f'speed_cmPs_application'] - merged_df[f'speed_cmPs_control']) 
                    

import seaborn as sns
import matplotlib.pyplot as plt

fig_dir = '/home/bgeurten/ethoVision_database/meth_figures'
# Defining y-axis columns
y_columns = [f'{column}_difference' for column in ['tigmo_taxis', 'freezing', 'stress', 'boldness', 'frantic', 'speed_cmPs']]

# Looping through each y-axis column
for column in y_columns:
    g = sns.relplot(data=merged_df, 
                    x='Time_bin', 
                    y=column, 
                    hue='Sex', 
                    kind='line', 
                    errorbar=('ci', 95), 
                    estimator='mean',
                    hue_order=['M','F'],
                    facet_kws={'sharey': False, 'sharex': True},
                    height=5, 
                    aspect=2)
    for ax in g.axes.flat:
        ax.axhline(0, color='black', linestyle='--')
        # Setting y-axis limits
    
    if column != 'speed_cmPs_difference':
        ax.set_ylim(-bin_size_sec/4, bin_size_sec/4)
        g.set_axis_labels('Time (min)', f'{column}, sec')

    else:
        ax.set_ylim(-0.1,0.1)
        g.set_axis_labels('Time (min)', f'{column}, cm/s')

    g.set_titles('Treatment: {col_name}')
    g.savefig(os.path.join(fig_dir,f'timeseries_{column}.svg'))
    g.savefig(os.path.join(fig_dir,f'timeseries_{column}.png'))

plt.show()





# Group by the new time bin, treatment, sex, tank number, and ID, then aggregate
agg_dict = {
    'tigmo_taxis_difference': 'sum',
    'freezing_difference': 'sum',
    'stress_difference': 'sum',
    'frantic_difference': 'sum',
    'boldness_difference': 'sum',
    'speed_cmPs_difference': 'mean'
}



df_agg = merged_df.groupby(['Unique_ID', 'Sex']).agg(agg_dict).reset_index()


for col in y_columns:
    fig, ax = plt.subplots()
    g = sns.boxplot(
        data=df_agg, x="Sex", y=col,
        notch=True, showcaps=True,
        flierprops={"marker": "x"},
        hue='Sex',
        hue_order=['M','F'],
        ax=ax)  # Specifying the ax parameter to plot on this subplot
    
    # Add a horizontal dashed line at y=0
    ax.axhline(0, color='black', linestyle='--')
    
    # Save the figure
    plt.savefig(os.path.join(fig_dir,f"{col}_boxplot.png"))
    
    if col != 'speed_cmPs_difference':
        ax.set_ylabel(f'{col}, sec')

    else:
       ax.set_ylabel(f'{col}, cm/s')

plt.show()

    