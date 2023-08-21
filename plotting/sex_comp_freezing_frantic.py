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
panic_df = df.loc[mask_day_1_to_2, ['Sex', 'Tank_number', 'ID', 'Freezing_fraction', 'frantic_fraction']]
stress_df = df.loc[mask_day_3_to_8, ['Sex', 'Tank_number', 'ID', 'Freezing_fraction', 'frantic_fraction']]
hab_df = df.loc[mask_day_9_to_22, ['Sex', 'Tank_number', 'ID', 'Freezing_fraction', 'frantic_fraction']]
rehab_df = df.loc[mask_day_23_to_27, ['Sex', 'Tank_number', 'ID', 'Freezing_fraction', 'frantic_fraction']]

#create a dataframe that contains the sum of freezing and frantic swimming for each individual fish over the respective days 
# Group by 'ID' and 'Tank_number' and sum the columns for panic phase
sum_panic_df = panic_df.groupby(['ID', 'Tank_number', 'Sex']).agg({
    'Freezing_fraction': 'sum',
    'frantic_fraction': 'sum'
}).reset_index()

# Group by 'ID' and 'Tank_number' and sum the columns for stress phase
sum_stress_df = stress_df.groupby(['ID', 'Tank_number', 'Sex']).agg({
    'Freezing_fraction': 'sum',
    'frantic_fraction': 'sum'
}).reset_index()

# Group by 'ID' and 'Tank_number' and sum the columns for habituated phase
sum_hab_df = hab_df.groupby(['ID', 'Tank_number', 'Sex']).agg({
    'Freezing_fraction': 'sum',
    'frantic_fraction': 'sum'
}).reset_index()

# Group by 'ID' and 'Tank_number' and sum the columns for rehabituated phase
sum_rehab_df = rehab_df.groupby(['ID', 'Tank_number', 'Sex']).agg({
    'Freezing_fraction': 'sum',
    'frantic_fraction': 'sum'
}).reset_index()






# plotting of all datapoints for either panic phase, stress phase, habituated phase or rehabituated phase
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
sns.set(style="whitegrid")

# Subplot 1: Freezing
sns.boxplot(x="Sex", y="Freezing_fraction", data=sum_stress_df, ax=axes[0]) # data = dataframe of interest
axes[0].set_title('Freezing_fraction')
axes[0].set_xlabel('Sex')
axes[0].set_ylabel('Freezing_fraction')

# Subplot 2: Frantic
sns.boxplot(x="Sex", y="frantic_fraction", data=sum_stress_df, ax=axes[1])
axes[1].set_title('frantic_fraction')
axes[1].set_xlabel('Sex')
axes[1].set_ylabel('frantic_fraction')

plt.tight_layout()
plt.show()


# Plotting mean freezing and frantic fractions for each dataframe
def plot_fractions(dataframe, title):
    plt.figure(figsize=(10, 6))
    
    # Calculate the mean freezing and frantic fractions for each sex
    mean_data = dataframe.groupby('Sex').mean()
    
    # Plot mean freezing fraction
    plt.subplot(1, 2, 1)
    sns.barplot(x=mean_data.index, y='Freezing_fraction', data=mean_data.reset_index(), errorbar=None)
    plt.xlabel('Sex')
    plt.ylabel('Mean Freezing Fraction')
    plt.title(f'{title} - Mean Freezing Fraction')
    
    # Plot mean frantic fraction
    plt.subplot(1, 2, 2)
    sns.barplot(x=mean_data.index, y='frantic_fraction', data=mean_data.reset_index(), errorbar=None)
    plt.xlabel('Sex')
    plt.ylabel('Mean Frantic Fraction')
    plt.title(f'{title} - Mean Frantic Fraction')
    
    plt.tight_layout()
    plt.show()

# Call the plotting function for each dataframe
plot_fractions(sum_panic_df, 'Panic')
plot_fractions(sum_stress_df, 'Stress')
plot_fractions(sum_hab_df, 'Habituation')
plot_fractions(sum_rehab_df, 'Rehab')






#statistics for specific phase

# Separate data for males and females, select dataframe of interest in data_male & data_female. Here: stress phase
data_male = sum_stress_df[sum_stress_df['Sex'] == 'M']
data_female = sum_stress_df[sum_stress_df['Sex'] == 'F']

# check normal distribution with shapiro wilk test
_, p_value_freezing_male = shapiro(data_male['Freezing_fraction'])
_, p_value_frantic_male = shapiro(data_male['frantic_fraction'])

_, p_value_freezing_female = shapiro(data_female['Freezing_fraction'])
_, p_value_frantic_female = shapiro(data_female['frantic_fraction'])

# Perform t-test for normally distributed data, and Wilcoxon signed-rank test for non-normally distributed data
if p_value_freezing_male > 0.05 and p_value_freezing_female > 0.05:
    t_statistic_freezing, p_value_freezing = ttest_ind(data_male['Freezing_fraction'], data_female['Freezing_fraction'])
    used_test_freezing = "t-test"
else:
    t_statistic_freezing, p_value_freezing = wilcoxon(data_male['Freezing_fraction'], data_female['Freezing_fraction'])
    used_test_freezing = "Wilcoxon signed-rank test"
if p_value_frantic_male > 0.05 and p_value_frantic_female > 0.05:
    t_statistic_frantic, p_value_frantic = ttest_ind(data_male['frantic_fraction'], data_female['frantic_fraction'])
    used_test_frantic = "t-test"
else:
    t_statistic_frantic, p_value_frantic = wilcoxon(data_male['frantic_fraction'], data_female['frantic_fraction'])
    used_test_frantic = "Wilcoxon signed-rank test"
    
# Function to add significance stars
def add_significance_stars(p_value):
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return 'n.s.'

#print test results
print("Test results for Freezing:")
print("Used Test:", used_test_freezing)
print("P-value:", p_value_freezing, add_significance_stars(p_value_freezing))

print("\nTest results for Frantic:")
print("Used Test:", used_test_frantic)
print("P-value:", p_value_frantic, add_significance_stars(p_value_frantic))














        







