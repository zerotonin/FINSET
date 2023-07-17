import pandas as pd
import os
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import numpy as np

parent_dir = "D:\\uni\\Biologie\\Master\\Masterarbeit_NZ\\analyses\\habituation_data\\python_analyses\\ethoVision_database\\habituation_individuals"
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


histogram_data  = np.full((22,26,64), np.nan)
trajectory_data = list()
fish_counter = 0
for position in tqdm(file_positions, desc='reading files...'):
    df = pd.read_csv(position)
    for day_num in df.Day_number.unique():
        subset = df[df['Day_number'] == day_num]
        histogram_data[day_num,:,fish_counter], _ = np.histogram(subset.speed_cmPs,bins=26,range=(0,25),density=True)
    fish_counter +=1

histogram_mean = np.nanmean(histogram_data,axis=2)

for i in range(histogram_mean.shape[0]):
    histogram_mean[i,:]= histogram_mean[i,:]/np.sum(histogram_mean[i,:])
#%% Plotting

# Create the figure and axis
fig, ax = plt.subplots(figsize=(8, 6))

# Plot the histograms with color coding
cmap = cm.get_cmap('plasma')
for i in range(22):
    color = cmap(i / 22)  # Assign color based on row index
    ax.plot(histogram_mean[i], color=color)

    # Find the peak of the histogram
    peak_index = np.argmax(histogram_mean[i])
    peak_value = histogram_mean[i, peak_index]

    # Mark the peak with a star symbol
    ax.plot(peak_index, peak_value, marker='*', markersize=10, color=color)


# Show the vertical dashed line
ax.axvline(x=8, color='black', linestyle='--')
ax.axvline(x=.5, color='black', linestyle='--')

ax.set_xlabel('speed, cm*s-1')
ax.set_ylabel('proability density')
ax.set_title('Mean speed histogram per day')

# Show the colorbar
sm = cm.ScalarMappable(cmap=cmap)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, pad=0.02 )
# Set custom tick positions and labels on the colorbar
tick_positions = np.linspace(0, 1, 22)  # Custom tick positions
tick_labels = np.arange(1, 23)  # Custom tick labels
cbar.set_ticks(tick_positions)
cbar.set_ticklabels(tick_labels)
cbar.set_label('Habituation Day')

# Display the figure
plt.tight_layout()
plt.show()

