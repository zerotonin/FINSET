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


def analyze_phase_behavior(df, mask, behavior_column, phase_name, save_figs):
    phase_df = df.loc[mask, ['Sex', 'Tank_number', 'ID', behavior_column]]
    grouped_phase_df = phase_df.groupby(['ID', 'Tank_number', 'Sex']).mean().reset_index()
    data_male = grouped_phase_df[grouped_phase_df['Sex'] == 'M']
    data_female = grouped_phase_df[grouped_phase_df['Sex'] == 'F']

    calculate_test_and_print_results(data_male, data_female, behavior_column)

    plt.figure(figsize=(6, 6))
    sns.set(style="whitegrid")
    colors = {"M": "lightsteelblue", "F": "pink"} 
    sns.boxplot(x="Sex", y=behavior_column, data=phase_df, palette = colors)
    plt.title(f'{behavior_column} - {phase_name}')
    plt.xlabel('Sex')
    plt.ylabel(behavior_column)
    
    ymin, ymax = plt.ylim()
    y_range = ymax - ymin
    additional_space = y_range * 0.1  # Adjust this factor as needed
    plt.ylim(ymin - additional_space, ymax + additional_space)
     
    plt.tight_layout()
    save_path = os.path.join(save_figs, f'{behavior_column}_{phase_name}_boxplot.png')
    plt.savefig(save_path)
    plt.show()

def calculate_test_and_print_results(data_male, data_female, behavior_column):
    _, p_value_male = shapiro(data_male[behavior_column])
    _, p_value_female = shapiro(data_female[behavior_column])

    if p_value_male > 0.05 and p_value_female > 0.05:
        _, p_value = mannwhitneyu(data_male[behavior_column], data_female[behavior_column], alternative="two-sided")
        used_test = "Mann-Whitney U test"
    else:
        _, p_value = mannwhitneyu(data_male[behavior_column], data_female[behavior_column], alternative="two-sided")
        used_test = "Mann-Whitney U test"

    def add_significance_stars(p_value):
        if p_value < 0.001:
            return '***'
        elif p_value < 0.01:
            return '**'
        elif p_value < 0.05:
            return '*'
        else:
            return 'n.s.'
    rounded_p_value = round(p_value, 4)
    print("Test results for", behavior_column)
    print("Used Test:", used_test)
    print("P-value:", rounded_p_value, add_significance_stars(p_value))
    
save_figs = "D:\\uni\\Biologie\\Master\\Masterarbeit_NZ\\analyses\\python_analysis\\ethoVision_database\\sex_comparisson_figures\\sex_comp_means"    
    
column = 'Bottom_fraction'
analyze_phase_behavior(df, mask_day_1_to_2, column, 'Panic', save_figs)
analyze_phase_behavior(df, mask_day_3_to_8, column, 'Stress', save_figs)
analyze_phase_behavior(df, mask_day_9_to_22, column, 'Habituation', save_figs)
analyze_phase_behavior(df, mask_day_23_to_27, column, 'Rehabituation', save_figs)
