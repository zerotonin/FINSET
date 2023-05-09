# FINSET: Fish Neuroscience and EthoVision SQL Trajectory Evaluation Tool

FINSET is a Python-based toolkit for processing and analyzing behavioral data from EthoVision tracking software. This toolkit includes several classes that facilitate the computation of various metrics related to the subject's movement, such as speed, activity, freezing, tigmotaxis, and more. The repository also includes tools for generating individual analysis reports and habituation profiles, and it can interface with an SQLite database for seamless data retrieval.

## Features

- EthoVision data processing and analysis
- Individual analysis reports with various plots
- Fish habituation profiling
- SQLite database support for data retrieval
- Extensible and customizable

## Installation

To install FINSET, clone the repository and install the required dependencies using the following commands:

```bash
git clone https://github.com/yourusername/finset.git
cd finset
pip install -r requirements.txt
```
## Usage

## Ethovision Python Classes Help Document

This document explains the relationship between the `EthovisionDataProcessor`, `IndividualAnalysisReportEthoVision`, `FishHabituationProfiler`, `EthoVisionSQLdataBase`, `EthoVisionReader`, and `DaywiseAnalysis` classes in Python.

### EthovisionDataProcessor

`EthovisionDataProcessor` is a class for processing and analyzing behavioral data from Ethovision tracking software. It takes a subject DataFrame and computes various metrics related to the subject's movement, including speed, activity, freezing, tigmotaxis, and more.

### IndividualAnalysisReportEthoVision

`IndividualAnalysisReportEthoVision` is a class for generating various plots for individual analysis based on EthoVision data. It takes a result DataFrame and a 3D numpy array containing histograms of fish positions for each day, and provides methods for plotting bout metrics, velocity metrics, bout and transition metrics, and normalized histograms.

### FishHabituationProfiler

`FishHabituationProfiler` is a class for profiling fish habituation using a DataFrame. It generates habituation profile plots for fish using their behavioral data, displaying line graphs of various measures over time, separated by sex, and highlighting the habituation limit using an arrow.

### EthoVisionSQLdataBase

`EthoVisionSQLdataBase` is a class for working with SQLite databases containing EthoVision data. It provides methods for opening a database, retrieving unique subject combinations, getting data for specific subjects, and closing the connection.

### EthoVisionReader

`EthoVisionReader` is a class for reading EthoVision Excel files and extracting trajectory and metadata. It provides methods for sorting DataFrames by start time and recording time.

### DaywiseAnalysis

`DaywiseAnalysis` is a class for plotting daywise histograms and boxplots of fish movement data. It takes a DataFrame, a list of file paths to histogram files, a list of fish IDs and tank numbers, and a 4D numpy array of histograms. It provides a method for running the daywise analysis, which loads the normalized histograms, sorts them by sex, calculates the median histograms, creates daywise histogram plots for male and female fish, and generates a boxplot.

## Example
```python
import pandas as pd

# Read data from an EthoVision Excel file
filename = "example_ethovision_file.xlsx"
ethovision_reader = EthoVisionReader(filename)
raw_data = ethovision_reader.read_excel()

# Process the data
processor = EthovisionDataProcessor(raw_data)
processed_data = processor.compute_metrics()

# Save the processed data to an SQLite database
database = EthoVisionSQLdataBase("example_database.db")
database.save_data_to_database(processed_data)

# Retrieve unique subjects from the database
unique_subjects = database.get_unique_subjects()

# Get data for a specific subject
subject_data = database.get_data_for_subject("Tank_1", "Subject_1")

# Generate an individual analysis report for the subject
individual_report = IndividualAnalysisReportEthoVision(subject_data)
figure_handles = individual_report.report()

# Run a daywise analysis on the data
daywise_analysis = DaywiseAnalysis(processed_data)
daywise_analysis.run_analysis()

# Check habituation profiles
habituation_profiler = FishHabituationProfiler(processed_data)
habituation_profiles, fish_id_list = habituation_profiler.check_habituation()
```
