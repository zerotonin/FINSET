import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import shapiro, mannwhitneyu
from data_base_analyser.EthoVisionExperimentSeries import EthoVisionExperimentSeries
from plotting.DaywiseAnalysis import DaywiseAnalysis
from plotting.FishHabituationProfiler import FishHabituationProfiler
import os
import pandas as pd
import numpy as np
import seaborn as sns
import glob
import matplotlib.pyplot as plt
import scipy.ndimage
from matplotlib.colors import LogNorm
import matplotlib.cm as cm
from scipy.stats import ttest_rel, wilcoxon, shapiro, mannwhitneyu, ttest_ind


#[print(x.shape) for x in histograms]
# Usage
tag = 'combined'
#parent_directory = '/home/bgeurten/ethoVision_database/'
parent_directory = "D:\\uni\\Biologie\\Master\\Masterarbeit_NZ\\analyses\\python_analysis\\ethoVision_database\\"

db_position = f'{parent_directory}{tag}_daywise_analysis.csv'
df = pd.read_csv(db_position)
columns = df.columns

# Create masks for each day range 1-3 = panic phase; 4-9 = stress phase; 10-22 = habituated phase, rehbabituation = 23-27
mask_day_1_to_2 = (df['Day_number'] >= 1) & (df['Day_number'] <= 2)
mask_day_3_to_8 = (df['Day_number'] >= 3) & (df['Day_number'] <= 8)
mask_day_9_to_22 = (df['Day_number'] >= 9) & (df['Day_number'] <= 22)
mask_day_23_to_27 = (df['Day_number'] >= 23) & (df['Day_number'] <= 27)

    
    # Create new DataFrames for each day range with needed columns
panic_df = df.loc[mask_day_1_to_2, ['Sex', 'Tank_number', 'ID', 'stress_score', 'stress_fraction', 'boldness_fraction']]
stress_df = df.loc[mask_day_3_to_8, ['Sex', 'Tank_number', 'ID', 'stress_score', 'stress_fraction', 'boldness_fraction']]
hab_df = df.loc[mask_day_9_to_22, ['Sex', 'Tank_number', 'ID', 'stress_score', 'stress_fraction', 'boldness_fraction']]
rehab_df = df.loc[mask_day_23_to_27, ['Sex', 'Tank_number', 'ID', 'stress_score', 'stress_fraction', 'boldness_fraction']]
    
# Calculate means for each behavioral state in the dataframes
stress_means = stress_df[['stress_score', 'stress_fraction', 'boldness_fraction']].mean()
hab_means = hab_df[['stress_score', 'stress_fraction', 'boldness_fraction']].mean()
rehab_means = rehab_df[['stress_score', 'stress_fraction', 'boldness_fraction']].mean()


# Plotting
behavioral_states = ['stress_score', 'stress_fraction', 'boldness_fraction']
state_labels = ['Stress', 'Habituated', 'Rehab']
group_colors = {
    'stress': 'pink',
    'habituated': 'lightsteelblue',
    'rehabituated': 'royalblue'
}

# Create a new figure for each behavioral state
for i, state in enumerate(behavioral_states):
    plt.figure(figsize=(6, 4))  # Adjust the figsize as needed
    plt.title(f'Mean {state}')
    
    means = [stress_means[state], hab_means[state], rehab_means[state]]
    
    bars = plt.bar(state_labels, means, color=[group_colors['stress'], group_colors['habituated'], group_colors['rehabituated']])
    plt.ylabel(state)
    
    y_max = max(means)
    y_min = min(0, min(means))  # Ensure y-axis starts from 0 or the smallest value, whichever is lower
    y_margin = 0.2 * (y_max - y_min)  # Additional margin as a percentage of the data range
    plt.ylim(y_min, y_max + y_margin)
    
    plt.tight_layout()
    plt.show()



