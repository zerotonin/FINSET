import pandas as pd
import os
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt


parent_dir = "D:\\uni\\Biologie\\Master\\Masterarbeit_NZ\\analyses\\habituation_data\\python_analyses\\ethoVision_database\\habituation_individuals"
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

    
collated_data = list()

for position in tqdm(file_positions, desc='reading files...'):
    collated_data.append(pd.read_csv(position))

df = pd.concat(collated_data)

# Draw a nested boxplot to show bills by day and time
df.dropna(subset=['Latency_to_top_s'], inplace=True) #drop non-annotated values
sns.boxplot(x="Day_number", y="Latency_to_top_s",
            hue="Sex", palette=["m", "g"], 
            data=df)
sns.despine(offset=10, trim=False) #cutoff y axis at 10 or not?
#plt.yscale('symlog')
#plt.ylim(bottom=0)
#plt.ylim(0, 1) #set y axis limits
plt.show()

# lineplot with 95% CI
df.dropna(subset=['Latency_to_top_s'], inplace=True) #drop non-annotated values
sns.lineplot(x="Day_number", y="Latency_to_top_s",
             hue="Sex",estimator='median',
             data=df)
#plt.yscale('log')
plt.ylim(0, 2)
plt.show()

#velocity histograms
filtered_df = df[["Day_number", "Median_speed_cmPs"]]
Vel_comp_df = filtered_df[filtered_df["Day_number"].isin([1, 15])]
# Set up the figure and axes
fig, ax = plt.subplots()
# Create a custom color palette for day 1 and day 15
colors = {1: "orange", 15: "steelblue"}

# Plot the histogram using seaborn and specify the color palette
sns.histplot(data=Vel_comp_df, x="Median_speed_cmPs", hue="Day_number", element="step", stat="density", ax=ax, palette=colors)

# Set the labels and title
ax.set_xlabel("Median Speed (cm/s)")
ax.set_ylabel("Density of Velocity")
ax.set_title("Comparison of Median Speed between Day 1 and Day 15")
plt.show()