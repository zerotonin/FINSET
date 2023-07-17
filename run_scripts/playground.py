import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fish_data_base.EthoVisionSQLdataBase import EthoVisionSQLdataBase
import os

tag = 'habituation2023'
parent_directory = "D:\\uni\\Biologie\\Master\\Masterarbeit_NZ\\analyses\\habituation_data\\python_analyses\\ethoVision_database"


db_name = os.path.join(parent_directory, f"{tag}_ethovision_data.db")
ev_db = EthoVisionSQLdataBase(db_name)

fish_names_df= ev_db.get_unique_subjects()

#%%
#fish_df = pd.read_csv("D:\\uni\\Biologie\\Master\\Masterarbeit_NZ\\analyses\\habituation_data\\python_analyses\\ethoVision_database\\habituation_individuals\\tankNum_01__fishID_O\\trajectory_data.csv")

#%% Individual Fish
subject_df = ev_db.get_data_for_subject(3, 'G')

#lists to store x and y values
x_values = []
y_values = []

#%% all fish

for i, row in fish_names_df.iterrows():
    # i is the row counter
    # row.Tank_number, row.ID are the identification variables.
    subject_df = ev_db.get_data_for_subject(row.Tank_number, row.ID)
    #calculate mean velocity for each  individual fish in the df
    mean_velocity = subject_df['Velocity_cm/s'].mean()
    #append the day number and the mean velocity of each fish to the empty lists
    x_values.append(subject_df['Day_number'].iloc[0])
    y_values.append(mean_velocity)

plt.plot(x_values, y_values, marker='o', linestyle='-', color='blue')
plt.xlabel('Day Number')
plt.ylabel('Mean Velocity [cm/s]')
plt.title('Mean Velocity Data for All Fish')
