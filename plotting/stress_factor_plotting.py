# Importing necessary libraries
import pandas as pd
import os
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

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
fish_counter = 0
frantic = np.full((22, 64), np.nan)
freezing = np.full((22, 64), np.nan)
bottom = np.full((22, 64), np.nan)
tigmo_taxis = np.full((22, 64), np.nan)
stress = np.full((22, 64), np.nan)

# Iterate over each file position and extract the relevant data
for position in tqdm(file_positions, desc='reading files...'):
    df = pd.read_csv(position)
    df['frantic_swim'] = df.speed_cmPs > 8
    df.freezing = df.speed_cmPs < 0.5
    df.in_bottom_margin = df.Y_center_cm < 2.5
    df['stress_index'] = df[['frantic_swim', 'freezing', 'in_bottom_margin']].any(axis=1)
    for day_num in df.Day_number.unique():
        subset = df[df['Day_number'] == day_num]
        frantic[day_num, fish_counter] = subset.frantic_swim.sum() / 25
        freezing[day_num, fish_counter] = subset.freezing.sum() / 25
        bottom[day_num, fish_counter] = subset.in_bottom_margin.sum() / 25
        tigmo_taxis[day_num, fish_counter] = subset.tigmo_taxis.sum() / 25
        stress[day_num, fish_counter] = subset.stress_index.sum() / 25
    fish_counter += 1

# Data for plotting
data = [frantic, freezing, bottom, tigmo_taxis, stress]
labels = ['Frantic Swim', 'Freezing', 'In Bottom Margin', 'Tigmo Taxis', 'Stress Index']
x_label = 'Days'
y_label = 'Duration (s)'

# Call the plotting function
plot_individual_values(data, labels, x_label, y_label)
