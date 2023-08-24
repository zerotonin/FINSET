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
import scipy.stats as stats

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
mask_day_23_to_27 = (df['Day_number'] >= 25) & (df['Day_number'] <= 27)

    
    # Create new DataFrames for each day range with needed columns
panic_df = df.loc[mask_day_1_to_2, ['Sex', 'Tank_number', 'ID', 'stress_score', 'stress_fraction', 'boldness_fraction', 'Median_speed_cmPs', 'Distance_travelled_cm', 'Freezing_fraction',
                                    'Top_fraction', 'Bottom_fraction', 'Tigmotaxis_fraction', 'frantic_fraction', 'Latency_to_top_s']]
stress_df = df.loc[mask_day_3_to_8, ['Sex', 'Tank_number', 'ID', 'stress_score', 'stress_fraction', 'boldness_fraction', 'Median_speed_cmPs', 'Distance_travelled_cm', 'Freezing_fraction',
                                    'Top_fraction', 'Bottom_fraction', 'Tigmotaxis_fraction', 'frantic_fraction', 'Latency_to_top_s']]
hab_df = df.loc[mask_day_9_to_22, ['Sex', 'Tank_number', 'ID', 'stress_score', 'stress_fraction', 'boldness_fraction', 'Median_speed_cmPs', 'Distance_travelled_cm', 'Freezing_fraction',
                                    'Top_fraction', 'Bottom_fraction', 'Tigmotaxis_fraction', 'frantic_fraction', 'Latency_to_top_s']]
rehab_df = df.loc[mask_day_23_to_27, ['Sex', 'Tank_number', 'ID', 'stress_score', 'stress_fraction', 'boldness_fraction', 'Median_speed_cmPs', 'Distance_travelled_cm', 'Freezing_fraction',
                                    'Top_fraction', 'Bottom_fraction', 'Tigmotaxis_fraction', 'frantic_fraction', 'Latency_to_top_s']]


# Calculate means for panic phase
panic_means = panic_df.drop('Sex', axis=1).groupby(['ID', 'Tank_number']).mean().reset_index()
stress_means = stress_df.drop('Sex', axis=1).groupby(['ID', 'Tank_number']).mean().reset_index()
hab_means = hab_df.drop('Sex', axis=1).groupby(['ID', 'Tank_number']).mean().reset_index()
rehab_means = rehab_df.drop('Sex', axis=1).groupby(['ID', 'Tank_number']).mean().reset_index()



# Define the columns to select in your DataFrames
columns_to_select = ['stress_score', 'stress_fraction', 'boldness_fraction', 'Median_speed_cmPs', 'Distance_travelled_cm', 'Freezing_fraction',
                     'Top_fraction', 'Bottom_fraction', 'Tigmotaxis_fraction', 'frantic_fraction', 'Latency_to_top_s']

# Define the labels for different phases
phase_labels = ['Stress', 'Habituated', 'Rehab']

# Define the colors for different groups
group_colors = {
    'stress phase': 'pink',
    'habituation phase': 'lightsteelblue',
    'rehabituation phase': 'royalblue'
}


def plot_behavioral_state_comparison(stress_means, hab_means, rehab_means, phase_labels, group_colors, save_directory):
    behavioral_states = columns_to_select
    
    for state in behavioral_states:
        plt.figure(figsize=(10, 6))
        plt.title(f'{state}')
        
        stress_stat = stress_means[state]
        hab_stat = hab_means[state]
        rehab_stat = rehab_means[state]
        
        # Test for normality
        _, stress_p_value = stats.shapiro(stress_stat)
        _, hab_p_value = stats.shapiro(hab_stat)
        _, rehab_p_value = stats.shapiro(rehab_stat)
        
        test_used = ""
        
        if stress_p_value > 0.05 and hab_p_value > 0.05:
            # All groups are normally distributed, use ANOVA
            f_stat, p_value = stats.f_oneway(stress_stat, hab_stat)
            test_used = "ANOVA"
        else:
            # At least one group is not normally distributed, use Kruskal-Wallis test
            h_stat, p_value = stats.kruskal(stress_stat, hab_stat)
            test_used = "Kruskal-Wallis"
        
        print(f"Behavioral state: {state}")
        print(f"Test used: {test_used}")
        print(f"P-value: {p_value}")
        
        if p_value < 0.05:
            print("Reject null hypothesis: There is a significant difference.")
        else:
            print("Fail to reject null hypothesis: No significant difference.")
        
        data = pd.DataFrame({
            'stress phase': stress_stat,
            'habituation phase': hab_stat,
            'rehabituation phase': rehab_stat
        })
        
        ax = sns.boxplot(data=data, palette=group_colors)
        plt.ylabel(state)
        # Add some additional space on the y-axis
        ax.set_ylim(ax.get_ylim()[0] - 0.0, ax.get_ylim()[1] + 0.3)
        plt.tight_layout()
        
         # Save the figure
        save_path = os.path.join(save_directory, f'{state}_boxplot.png')
        plt.savefig(save_path)
        
        plt.show()
        
        # Print significance stars
        if p_value < 0.001:
            significance = "***"
        elif p_value < 0.01:
            significance = "**"
        elif p_value < 0.05:
            significance = "*"
        else:
            significance = "ns"
        
        print(f"Significance: {significance}")

save_directory = "D:\\uni\\Biologie\\Master\\Masterarbeit_NZ\\analyses\\python_analysis\\ethoVision_database\\phase_comparison"
# Create new DataFrames for each day range with needed columns
panic_data = df.loc[mask_day_1_to_2, columns_to_select]
stress_data = df.loc[mask_day_3_to_8, columns_to_select]
hab_data= df.loc[mask_day_9_to_22, columns_to_select]
rehab_data = df.loc[mask_day_23_to_27, columns_to_select]

# Call the function to plot the comparison
plot_behavioral_state_comparison(stress_means, hab_means, rehab_means, phase_labels, group_colors, save_directory)

