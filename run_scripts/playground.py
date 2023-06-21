import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fish_data_base.EthoVisionSQLdataBase import EthoVisionSQLdataBase
import os

tag = 'habituation2023'
parent_directory = '/home/bgeurten/ethoVision_database/'


db_name = os.path.join(parent_directory, f"{tag}_ethovision_data.db")
ev_db = EthoVisionSQLdataBase(db_name)

fish_names_df= ev_db.get_unique_subjects()

#%%
fish_df = pd.read_csv('/home/bgeurten/ethoVision_database/tankNum_01__fishID_G/trajectory_data.csv')

#%% Individual Fish
subject_df = ev_db.get_data_for_subject(3, 'G')

#%% all fish

for i, row in fish_names_df.iterrows():
    # i is the row counter
    # row.Tank_number, row.ID are the identification variables.
    subject_df = ev_db.get_data_for_subject(row.Tank_number, row.ID
                                            )

