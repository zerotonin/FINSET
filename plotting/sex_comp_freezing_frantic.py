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





# plotting all values for certain behavior inclusive outliers
plt.figure(figsize=(6, 6))
sns.set(style="whitegrid")

sns.boxplot(x="Sex", y="Freezing_fraction", data=sum_stress_df)
plt.title('Freezing fraction stress phase')
plt.xlabel('Sex')
plt.ylabel('Freezing_fraction')

plt.tight_layout()
plt.show()


#mean plotting of each phase for a certain behavior
def plot_freezing(dataframe, title):
    plt.figure(figsize=(6, 6))
    
    # Calculate the mean freezing fraction for each sex
    mean_data = dataframe.groupby('Sex')['Freezing_fraction'].mean()
    
    # Plot mean freezing fraction
    sns.barplot(x=mean_data.index, y=mean_data.values, palette='Set2')
    plt.xlabel('Sex')
    plt.ylabel('Mean Freezing Fraction')
    plt.title(f'{title} Phase - Mean Freezing Fraction')
    
    plt.tight_layout()
    plt.show()

# Call the plotting function for each phase
plot_freezing(sum_panic_df, 'Panic')
plot_freezing(sum_stress_df, 'Stress')
plot_freezing(sum_hab_df, 'Habituation')
plot_freezing(sum_rehab_df, 'Rehab')




#statistics for specific phase and behaviors
#still to add: stress fraction, stress score, median speed, thigmotaxis fraction, (latency to top)

# Separate data for males and females, select dataframe of interest in data_male & data_female. Here: stress phase
data_male = sum_stress_df[sum_stress_df['Sex'] == 'M']
data_female = sum_stress_df[sum_stress_df['Sex'] == 'F']

# check normal distribution with shapiro wilk test
_, p_value_freezing_male = shapiro(data_male['Freezing_fraction'])
_, p_value_frantic_male = shapiro(data_male['frantic_fraction'])

_, p_value_freezing_female = shapiro(data_female['Freezing_fraction'])
_, p_value_frantic_female = shapiro(data_female['frantic_fraction'])

# Perform Mann-Whitney U test for non-normally distributed data
if p_value_freezing_male > 0.05 and p_value_freezing_female > 0.05:
    _, p_value_freezing = mannwhitneyu(data_male['Freezing_fraction'], data_female['Freezing_fraction'], alternative="two-sided")
    used_test_freezing = "Mann-Whitney U test"
else:
    _, p_value_freezing = mannwhitneyu(data_male['Freezing_fraction'], data_female['Freezing_fraction'], alternative="two-sided")
    used_test_freezing = "Mann-Whitney U test"
if p_value_frantic_male > 0.05 and p_value_frantic_female > 0.05:
    _, p_value_frantic = mannwhitneyu(data_male['frantic_fraction'], data_female['frantic_fraction'], alternative="two-sided")
    used_test_frantic = "Mann-Whitney U test"
else:
    _, p_value_frantic = mannwhitneyu(data_male['frantic_fraction'], data_female['frantic_fraction'], alternative="two-sided")
    used_test_frantic = "Mann-Whitney U test"

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

# print test results
print("Test results for Freezing:")
print("Used Test:", used_test_freezing)
print("P-value:", p_value_freezing, add_significance_stars(p_value_freezing))

print("\nTest results for Frantic:")
print("Used Test:", used_test_frantic)
print("P-value:", p_value_frantic, add_significance_stars(p_value_frantic))















        







