# Importing necessary libraries
import pandas as pd
import os
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import scipy.stats as stats

"""
    This script is designed to visualize data from the 2023 habituation experiments of Alexander Busch. The quantifications are calculated for different categories 
    including 'Frantic Swim', 'Freezing', 'In Bottom Margin', 'Tigmo Taxis', and 'Stress Index'. These quantifications are then plotted individually for each category with 
    their mean and standard error over the days. The files containing the data are located and read from the specified parent directory.
"""

def plot_individual_values(data, labels, x_label, y_label):
    """
    Function for creating and displaying plots from data.

    :param data: A list of 2D numpy arrays with the data to be plotted. 
                 Each 2D array represents different categories to be plotted in different subplots.
    :param labels: A list of strings containing the labels for the different categories of data.
    :param x_label: The label for the x-axis of the plots.
    :param y_label: The label for the y-axis of the plots.
    """
    num_plots = len(data)
    num_rows = (num_plots + 1) // 2  # Calculate the number of rows needed
    num_cols = 2  # Set the number of columns to 2

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 6 * num_rows))

    cmap = cm.get_cmap('plasma')
    axes = axes.ravel()  # Flatten the axes array for easy iteration

    for i, (values, label) in enumerate(zip(data, labels)):
        color = cmap((i + 1) / num_plots)

        mean_value = np.nanmean(values, axis=1)
        std_error = np.nanstd(values, axis=1) / np.sqrt(np.sum(~np.isnan(values), axis=1))
        axes[i].plot(mean_value, color='black', linestyle='--', label='Mean')
        axes[i].fill_between(range(22), mean_value - std_error, mean_value + std_error, color=color, alpha=0.2,
                             label='Standard Error')

        axes[i].set_xlabel(x_label)
        axes[i].set_ylabel(y_label)
        axes[i].set_title(label)

        axes[i].legend()

    # Remove empty subplots
    for j in range(num_plots, num_rows * num_cols):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()


parent_dir = '/home/bgeurten/ethoVision_database/'
file_name = 'trajectory_data.csv'

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

trajectory_data = list()
fish_counter    = 0
frantic         = np.full((22, 64), np.nan)
freezing        = np.full((22, 64), np.nan)
bottom          = np.full((22, 64), np.nan)
tigmo_taxis     = np.full((22, 64), np.nan)
top_margin      = np.full((22, 64), np.nan)
stress          = np.full((22, 64), np.nan)
boldness        = np.full((22, 64), np.nan)
normal          = np.full((22, 64), np.nan)

bottom_threshold  = 2.5 # cm    
side_threshold    = 4.0 # which is half a body length of 4 cm long adult zebrafish
top_threshold     = 4.0
speed_threshold   = 0.5 # cm/s  
frantic_threshold = 8.0 # cm/s

# Iterate over each file position and extract the relevant data
for position in tqdm(file_positions, desc='reading files...'):
    df = pd.read_csv(position)
    df['frantic_swim'] = df.speed_cmPs > frantic_threshold
    #df.freezing = df.speed_cmPs        < speed_threshold
    df.in_bottom_margin = df.Y_center_cm < bottom_threshold
    df.in_left_margin  = df.X_center_cm < side_threshold
    df.in_right_margin = df.X_center_cm > (20.5-side_threshold)
    df.in_top_margin = df.Y_center_cm > (20.5-top_threshold)
    df.activity = df.speed_cmPs > speed_threshold
    df['freezing'] = (df['activity']) & (df['in_bottom_margin'])
    df['in_side_margin'] = df[['in_left_margin', 'in_right_margin']].any(axis=1)
    df['vert_activity'] = df.speed_vert_cmPs > speed_threshold
    df['tigmo_taxis'] = df[['vert_activity', 'in_side_margin']].all(axis=1)
    #df.loc[df.in_top_margin, 'tigmo_taxis'] = False
    df['stress_index'] = df[['tigmo_taxis','frantic_swim', 'freezing']].any(axis=1)
    df['boldness'] = (df.in_top_margin) & (df.speed_cmPs < frantic_threshold)
    df['normal'] = ~((df['boldness']) & (df['stress_index']))

    #df.loc[df.in_top_margin, 'stress_index'] = False
    for day_num in df.Day_number.unique():
        subset = df[df['Day_number'] == day_num]
        frantic[day_num, fish_counter] = subset.frantic_swim.sum() / 25
        freezing[day_num, fish_counter] = subset.freezing.sum() / 25
        tigmo_taxis[day_num, fish_counter] = subset.tigmo_taxis.sum() / 25
        top_margin[day_num, fish_counter] = subset.in_top_margin.sum() / 25
        stress[day_num, fish_counter] = subset.stress_index.sum() / 25 
        boldness[day_num, fish_counter] = subset.boldness.sum() / 25 
        normal[day_num, fish_counter] = subset.normal.sum() / 25 
    fish_counter += 1

# Data for plotting
data = [frantic, freezing,  tigmo_taxis, top_margin, stress, boldness,normal]
labels = ['Frantic Swim', 'Freezing', 'Tigmo Taxis', 'Top margin', 'Stress Index','boldness','normal']
x_label = 'Days'
y_label = 'Duration (s)'

# Call the plotting function
plot_individual_values(data, labels, x_label, y_label)



stress_score_matrix = (stress-boldness)/(stress+boldness)
stress_score_matrix[-1,0] = stress_score_matrix[-1,1]
median = np.median(stress_score_matrix, axis=1)
confidence_interval = stats.t.interval(0.95, len(stress_score_matrix) - 1, 
                                       loc=np.mean(stress_score_matrix, axis=1), 
                                       scale=stats.sem(stress_score_matrix, axis=1))

plt.figure(figsize=(10, 6))

# assuming your x-axis is just a range from 0 to the length of your median
x = np.arange(len(median))

# plotting the median line
plt.plot(x, median, color='blue', label='Median')

# filling the confidence interval
plt.fill_between(x, confidence_interval[0], confidence_interval[1], color='blue', alpha=0.2)

plt.axhline(0, color='red', linestyle='--')  # Add a horizontal line at y=0


plt.ylim([-1, 1])  # setting y limits
plt.legend(loc='best')

plt.show()
