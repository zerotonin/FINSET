# Importing necessary libraries
import pandas as pd
import os
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import scipy.stats as stats


parent_dir = "D:\\uni\\Biologie\\Master\\Masterarbeit_NZ\\analyses\\python_analysis\\ethoVision_database"
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

drug_admin_df = pd.read_csv('D:\\uni\\Biologie\\Master\\Masterarbeit_NZ\\analyses\\python_analysis\\ethoVision_database\\drug_administration.csv')
column_strings = ['Freezing_fraction', 'Tigmotaxis_fraction', 'Latency_to_top_s', 
                    'boldness_fraction', 'frantic_fraction', 'stress_fraction','stress_score','Median_speed_cmPs'] 

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


# ... (your existing code)



def significance_stars(p_value):
    """
    Function to add significance stars to the plot.
    """
    if p_value < 0.001:
        return "***"
    elif p_value < 0.01:
        return "**"
    elif p_value < 0.05:
        return "*"
    else:
        return "n.s."

all_p_values_pre_vs_drug = []  # List to store all p-values for "Pre vs. Drug" comparison
all_p_values_pre_vs_post_male = []  # List to store all p-values for "Pre vs. Post" comparison in males
all_p_values_pre_vs_post_female = []  # List to store all p-values for "Pre vs. Post" comparison in females


# Function to perform tests and add results to the respective lists
def perform_test_and_store_results(col_str, males, females):
    # Check if both pre and drug data are normally distributed
    shapiro_pre = stats.shapiro(drug_df[f'pre_{col_str}'])
    shapiro_drug = stats.shapiro(drug_df[f'drug_{col_str}'])
    shapiro_post = stats.shapiro(drug_df[f'post_{col_str}'].dropna())  # Drop NA values for the post group

    if shapiro_pre.pvalue > 0.05 and shapiro_drug.pvalue > 0.05:
        # If data is normally distributed, perform separate two-tailed paired t-tests for male and female groups
        t_statistic_male, p_value_pre_vs_drug_male = stats.ttest_rel(*males)
        t_statistic_female, p_value_pre_vs_drug_female = stats.ttest_rel(*females)

        all_p_values_pre_vs_drug.append((f"Pre vs. Drug (Male) ({col_str})", p_value_pre_vs_drug_male, "Two-tailed paired t-test"))
        all_p_values_pre_vs_drug.append((f"Pre vs. Drug (Female) ({col_str})", p_value_pre_vs_drug_female, "Two-tailed paired t-test"))
    else:
        # If data is not normally distributed, perform separate Wilcoxon signed-rank tests for male and female groups
        t_statistic_male, p_value_pre_vs_drug_male = stats.wilcoxon(*males)
        t_statistic_female, p_value_pre_vs_drug_female = stats.wilcoxon(*females)

        all_p_values_pre_vs_drug.append((f"Pre vs. Drug (Male) ({col_str})", p_value_pre_vs_drug_male, "Wilcoxon signed-rank test"))
        all_p_values_pre_vs_drug.append((f"Pre vs. Drug (Female) ({col_str})", p_value_pre_vs_drug_female, "Wilcoxon signed-rank test"))

    # Perform t-test only for animals that have both pre and post data for males
    pre_post_data_male = pre_post_animals_male[f'pre_{col_str}'], pre_post_animals_male[f'post_{col_str}']
    t_statistic_pre_vs_post_male, p_value_pre_vs_post_male = stats.ttest_rel(*pre_post_data_male)
    all_p_values_pre_vs_post_male.append((f"Pre vs. Post (Male) ({col_str})", p_value_pre_vs_post_male, "Two-tailed paired t-test"))

    # Perform t-test only for animals that have both pre and post data for females
    pre_post_data_female = pre_post_animals_female[f'pre_{col_str}'], pre_post_animals_female[f'post_{col_str}']
    t_statistic_pre_vs_post_female, p_value_pre_vs_post_female = stats.ttest_rel(*pre_post_data_female)
    all_p_values_pre_vs_post_female.append((f"Pre vs. Post (Female) ({col_str})", p_value_pre_vs_post_female, "Two-tailed paired t-test"))

# Iterate through the columns and perform the tests
for col_str in column_strings:
    data = drug_df.loc[:, f'pre_{col_str}'].to_list()
    data += drug_df.loc[:, f'drug_{col_str}'].to_list()
    data += drug_df.loc[:, f'post_{col_str}'].to_list()

    plot_df = pd.DataFrame({'time': time, col_str: data, 'sex': sex})
    f = plt.figure(figsize=(10, 6))
    sns.boxplot(x="time", y=col_str,
                hue="sex", palette=["b", "r"],
                data=plot_df, notch=True)
    sns.despine(offset=10, trim=True)

    # Extract data for males and females
    males = drug_df[drug_df['sex'] == 'M'][f'pre_{col_str}'], drug_df[drug_df['sex'] == 'M'][f'drug_{col_str}']
    females = drug_df[drug_df['sex'] == 'F'][f'pre_{col_str}'], drug_df[drug_df['sex'] == 'F'][f'drug_{col_str}']

    # Perform tests and store results in the respective lists
    perform_test_and_store_results(col_str, males, females)

# Print all p-values and normality test results in the terminal
print("Pre vs. Drug comparisons:")
for group_comparison, p_value, test_used in all_p_values_pre_vs_drug:
    sig_stars = significance_stars(p_value)
    print(f"{group_comparison}: {p_value:.4f} {sig_stars} (Test used: {test_used})")

print("\nPre vs. Post comparisons (Males):")
for group_comparison, p_value, test_used in all_p_values_pre_vs_post_male:
    sig_stars = significance_stars(p_value)
    print(f"{group_comparison}: {p_value:.4f} {sig_stars} (Test used: {test_used})")

print("\nPre vs. Post comparisons (Females):")
for group_comparison, p_value, test_used in all_p_values_pre_vs_post_female:
    sig_stars = significance_stars(p_value)
    print(f"{group_comparison}: {p_value:.4f} {sig_stars} (Test used: {test_used})")

plt.show()












