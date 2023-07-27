import pandas as pd
import numpy as np


class EthovisionDataProcessor:
    """
    EthovisionDataProcessor is a class for processing and analyzing behavioral data
    from Ethovision tracking software. It takes a subject DataFrame and computes various
    metrics related to the subject's movement, including speed, activity, freezing,
    tigmotaxis, and more.

    Attributes:
    subject_df (pd.DataFrame): The input DataFrame containing the subject's data.
    speed_threshold (float): The speed threshold for considering a subject active.
    Defaults to 0.02.
    fps (int): The frames per second of the recording. Defaults to 25.
    left_margin (float): The boundary value for the left margin. Defaults to 2.0.
    right_margin (float): The boundary value for the right margin. Defaults to 18.5.
    bottom_margin (float): The boundary value for the bottom margin. Defaults to 2.5.
    top_margin (float): The boundary value for the top margin. Defaults to 18.5.
    """
    def __init__(self, subject_df, speed_threshold=0.5, fps=25, margins = (2.0,18.5,2.5,18.5)):
        self.subject_df = subject_df
        self.speed_threshold = speed_threshold
        self.fps = fps
        self.left_margin   = margins[0]
        self.right_margin  = margins[1]
        self.bottom_margin = margins[2]
        self.top_margin    = margins[3]

    def add_day_number(self):
        """
        Adds a new 'Day_number' column to the subject DataFrame based on the 'Start_time' column.
        The 'Day_number' column starts at 0 for the earliest date and increments by one for each
        unique date in the 'Start_time' column.
        """
        # Convert 'Start_time' column to datetime format
        self.subject_df['Start_time'] = pd.to_datetime(self.subject_df['Start_time'], format='%m/%d/%Y %H:%M:%S.%f')

        # Extract only the date from 'Start_time' column and drop duplicates
        unique_dates = self.subject_df['Start_time'].dt.normalize().drop_duplicates().sort_values()

        # Create a dictionary mapping unique dates to their day number
        day_number_mapping = {date: i for i, date in enumerate(unique_dates)}

        # Add a new 'Day_number' column based on the mapping
        self.subject_df['Day_number'] = self.subject_df['Start_time'].dt.normalize().map(day_number_mapping)


    def calculate_speed(self):
        """
        Calculates the speed in cm per second based on the first derivative of the columns
        'X_center_cm', 'Y_center_cm', and 'Recording_time_s', and adds the speed to the
        subject DataFrame as a new column called 'speed_cmPs'.
        """

        # Initialize a new column for the speed
        self.subject_df['speed_cmPs'] = np.nan

        # Iterate through the unique Day_numbers
        for day_number in self.subject_df['Day_number'].unique():
            # Extract the data for the current day
            day_data = self.subject_df[self.subject_df['Day_number'] == day_number]

            # Calculate the first derivative for the specified columns
            x_diff = day_data['X_center_cm'].diff()
            y_diff = day_data['Y_center_cm'].diff()
            vertical_speed = y_diff * self.fps
            horizontal_speed = x_diff * self.fps

            # Calculate the norm of the vector
            norm_vector = np.sqrt(x_diff ** 2 + y_diff ** 2)

            # Calculate the speed in cm per second
            speed_cmPs = norm_vector * self.fps


            # Update the 'speed_cmPs' column for the current day
            self.subject_df.loc[self.subject_df['Day_number'] == day_number, 'speed_cmPs'] = speed_cmPs
            self.subject_df.loc[self.subject_df['Day_number'] == day_number, 'speed_vert_cmPs'] = vertical_speed
            self.subject_df.loc[self.subject_df['Day_number'] == day_number, 'speed_horiz_cmPs'] = horizontal_speed

    def set_activity_status(self, speed_threshold=0.5):
        """
        Adds an 'activity' column to the subject DataFrame, indicating whether the
        subject's speed is greater than the given speed_threshold.

        Args:
            speed_threshold (float, optional): The threshold for considering a subject
                                               active. Defaults to 0.02.
        """

        self.subject_df['activity'] = self.subject_df.speed_cmPs > speed_threshold
    
    def set_frantic_status(self, speed_threshold=8.0):
        """
            Adds a 'frantic_status' column to the zebrafish DataFrame, indicating whether the
            zebrafish's swimming speed is greater than the given speed_threshold. This threshold
            originates from comparing the swimming histograms of zebrafish that have
            been habituated for 15 days against their swimming patterns on the first day.

            Args:
                speed_threshold (float, optional): The threshold for considering a zebrafish
                                                frantic. This function specifically uses a
                                                different threshold of 8 cm/s. Defaults to 8.
        """

        self.subject_df['frantic'] = self.subject_df.speed_cmPs > speed_threshold

    def set_bold_status(self):
        """
        Set the boldness status of the subject by calculating the boldness index. The boldness index is calculated
        as the logical AND operation between the 'in_top_margin' and the logical NOT operation of 'frantic_swim' column.
        This method should only be called after the 'set_frantic_status' method has been called.

        The result is stored in a new column in the DataFrame named 'boldness_index'.

        Args:
            None

        Returns:
            None
        """
        self.subject_df['boldness'] = ( self.subject_df.in_top_margin) & ~(self.subject_df.frantic)

    def set_stress_status(self):
        """
        Set the stress status of the subject by calculating the stress index. The stress index is calculated
        as the logical OR operation ('any' in pandas) across the 'tigmo_taxis', 'frantic_swim', and 'freezing' columns.
        This method should only be called after the 'set_frantic_status' method has been called.

        The result is stored in a new column in the DataFrame named 'stress_index'.

        Args:
            None

        Returns:
            None
        """
        self.subject_df['stress'] =  self.subject_df[['tigmo_taxis','frantic', 'freezing']].any(axis=1)



    def compute_zones(self):
        """
        Calculates the boolean values for each zone (left, right, bottom, top) and
        adds them as new columns to the subject DataFrame.

        Args:
            left_margin (float): The boundary value for the left margin.
            right_margin (float): The boundary value for the right margin.
            bottom_margin (float): The boundary value for the bottom margin.
            top_margin (float): The boundary value for the top margin.
        """

        self.subject_df['in_left_margin']   = self.subject_df.X_center_cm < self.left_margin
        self.subject_df['in_right_margin']  = self.subject_df.X_center_cm > self.right_margin
        self.subject_df['in_bottom_margin'] = self.subject_df.Y_center_cm < self.bottom_margin        
        self.subject_df['in_top_margin']    = self.subject_df.Y_center_cm > self.top_margin
    

    def map_zones_to_integers(self):
        """
        Maps the boolean zone values in the input DataFrame to corresponding
        integers (similar to a numeric keypad layout) and adds a new column named
        'zone_map' to the DataFrame.
        """

        num_pad_direction = list()

        for i, row in self.subject_df.iterrows():
            if row['in_bottom_margin']:
                if row['in_left_margin']:
                    num_pad_direction.append(1)
                elif row['in_right_margin']:
                    num_pad_direction.append(3)
                else:
                    num_pad_direction.append(2)
            elif row['in_top_margin']:
                if row['in_left_margin']:
                    num_pad_direction.append(7)
                elif row['in_right_margin']:
                    num_pad_direction.append(9)
                else:
                    num_pad_direction.append(8)
            else:
                if row['in_left_margin']:
                    num_pad_direction.append(4)
                elif row['in_right_margin']:
                    num_pad_direction.append(6)
                else:
                    num_pad_direction.append(5)

        self.subject_df['zone_map'] = num_pad_direction

    def side_tigmotaxis(self):
        """
        Adds a new 'tigmo_taxis' column to the subject DataFrame, containing rows where activity is True
        and either in_left_margin or in_right_margin is True. This column represents a direct measure
        of tigmotaxis in the fish.
        """
        self.subject_df['tigmo_taxis'] = (self.subject_df['speed_vert_cmPs'].abs() > self.speed_threshold) & (self.subject_df['in_left_margin'] | self.subject_df['in_right_margin']) 

    def true_freezing(self):
        """
        Adds a new 'freezing' column to the subject DataFrame, containing rows where in_bottom_margin is
        True and activity is False. This column quantifies "true" freezing, in which the fish sits on the
        bottom in rigor.
        """
        self.subject_df['freezing'] = (~self.subject_df['activity']) & (self.subject_df['in_bottom_margin'])

    
    def latency_to_top(self,day_data):
        """
        Calculate the latency until the fish first enters the top zone.

        Returns:
            float: The index when the fish first enters the top zone.
        """
        try:
            first_top_entry = day_data.loc[day_data['in_top_margin']].index[0]
            return (first_top_entry-day_data.index[0])/self.fps
        except:
            return np.nan

    def zonening_analysis(self,day_data):
        """
        Calculate the total number of transitions in the zone map between the lateral zones.
        and general entries into the top zone
        This represents the etho-vision version of the tigmotaxis analysis.

        Returns:
            int: The total number of transitions between the specified zones.
        """
        tigmo_transitions = 0
        into_top_transitions = 0
        tigmo_transition_patterns = [(1, 4), (4, 1), (4, 7), (7, 4), (9, 6), (6, 9), (6, 3), (3, 6)]
        into_top_transition_patterns = [(4, 7), (5, 7), (4, 8), (5, 8), (6, 8), (5, 9), (6, 9)]
        
        for i in range(len(day_data) - 1):
            current_zone = day_data['zone_map'].iloc[i]
            next_zone = day_data['zone_map'].iloc[i + 1]
            
            if (current_zone, next_zone) in tigmo_transition_patterns:
                tigmo_transitions += 1

            if (current_zone, next_zone) in into_top_transition_patterns:
                into_top_transitions += 1
                
        return tigmo_transitions, into_top_transitions    
    
    def calculate_bout_metrics(self, data, column_name, total_time):
        """
        Calculate the median bout duration and the fraction of time spent in a given behavioral state
        (activity, freezing, or tigmotaxis) based on the specified boolean column.

        Args:
            data (pd.DataFrame): A DataFrame containing the data for a specific day.
            column_name (str): The name of the boolean column representing the behavioral state.
            total_time (float): The total recording time for the specific day.

        Returns:
            median_bout_duration (float): The median duration of bouts for the given behavioral state.
            fraction (float): The fraction of time spent in the given behavioral state.
        """
        bouts = data.groupby((data[column_name].shift() != data[column_name]).cumsum())
        bout_durations = bouts['Recording_time_s'].agg(np.ptp)
        boolean_value = bouts[column_name].first()

        # Filter out zero values before calculating the median bout duration
        non_zero_bout_durations = bout_durations[boolean_value][bout_durations[boolean_value] > 0]

        median_bout_duration = non_zero_bout_durations.median()
        fraction = bout_durations[boolean_value].sum() / total_time

        return median_bout_duration, fraction

    def calculate_2d_histogram(self, day_data, tank_width, tank_height, num_bins):
        """
        Calculates a 2D histogram for day_data.X_center_cm and day_data.Y_center_cm using
        linearly spaced bins along the input variables tank_width and tank_height.

        Args:
            day_data (pd.DataFrame): A DataFrame containing the X_center_cm and Y_center_cm columns.
            tank_width (float): The width of the tank.
            tank_height (float): The height of the tank.
            num_bins (int, optional): The number of linearly spaced bins.

        Returns:
            numpy.ndarray: A 2D histogram (10x10 numpy array) of X_center_cm and Y_center_cm values.
        """

        # Define bin edges for X_center_cm and Y_center_cm
        x_bin_edges = np.linspace(0, tank_width, num_bins + 1)
        y_bin_edges = np.linspace(0, tank_height, num_bins + 1)

        # Calculate the 2D histogram
        hist_2d, _, _ = np.histogram2d(day_data.X_center_cm, day_data.Y_center_cm, bins=[x_bin_edges, y_bin_edges])

        return hist_2d
    
    def calculate_bout_metrics_for_day(self, day_data, total_time):
        """
        Calculate all bout metrics for a given day.

        Args:
            day_data (pd.DataFrame): A DataFrame containing the data for a single day.
            total_time (float): The total recording time for the day in seconds.

        Returns:
            bout_metrics (dict): A dictionary containing median bout duration and fraction for each bout type.
        """
        bout_metrics = {}
        for bout_type in ['activity', 'freezing', 'in_top_margin', 'in_bottom_margin', 'tigmo_taxis','frantic','stress','boldness']:
            median_duration, fraction = self.calculate_bout_metrics(day_data, bout_type, total_time)
            bout_metrics[f'Median_{bout_type}_duration_s'] = median_duration
            bout_metrics[f'{bout_type}_fraction'] = fraction
            bout_metrics[f'{bout_type}_duration_s'] = fraction*total_time
        return bout_metrics

    def calculate_latency_and_transitions_for_day(self, day_data):
        """
        Calculate latency to the top of the tank and tigmotaxis transitions for a given day.

        Args:
            day_data (pd.DataFrame): A DataFrame containing the data for a single day.

        Returns:
            latency_and_transitions (dict): A dictionary containing latency to the top, transiotions into top, and tigmotaxis transitions.
        """
        tigmo_transitions, into_top_transitions = self.zonening_analysis(day_data)
        return {
            'Latency_to_top_s': self.latency_to_top(day_data),
            'top_zone_entries': into_top_transitions,
            'Tigmotaxis_transitions':tigmo_transitions
        }

    def calculate_distance_and_histogram_for_day(self, day_data, tank_width, tank_height, num_bins_2D_hist):
        """
        Calculate the distance travelled and the 2D histogram for a given day.

        Args:
            day_data (pd.DataFrame): A DataFrame containing the data for a single day.
            tank_width (float): The width of the tank in centimeters.
            tank_height (float): The height of the tank in centimeters.
            num_bins_2D_hist (int): The number of linearly spaced bins along the tank width and height for the 2D histogram.

        Returns:
            distance (float): The distance travelled in centimeters.
            histogram (np.ndarray): A 2D histogram of the subject's position in the tank.
        """
        distance = (day_data.speed_cmPs / self.fps).sum()
        histogram = self.calculate_2d_histogram(day_data, tank_width, tank_height, num_bins_2D_hist)
        return distance, histogram

    def add_subject_info(self, stats_df):
        """
        Adds subject information (Sex, Tank_number, and ID) to the result DataFrame.
        
        Parameters
        ----------
        stats_df : pd.DataFrame
            The DataFrame containing the results data to be updated.
            
        Returns
        -------
        stats_df : pd.DataFrame
            The updated result DataFrame containing the added subject information.
        """
        stats_df["Sex"] = self.subject_df.Sex.iloc[0]
        stats_df["Tank_number"] = self.subject_df.Tank_number.iloc[0]
        stats_df["ID"] = self.subject_df.ID.iloc[0]
        
        return stats_df

    def process_data(self, tank_width, tank_height, num_bins_2D_hist=10):
        """
        Process the subject data and compute various metrics for each day, such as median speed,
        gross speed, median activity bout duration, activity fraction, median freezing bout duration, 
        freezing fraction, median top duration, top fraction, median bottom duration, bottom fraction,
        median tigmotaxis bout duration, tigmotaxis fraction, tigmotaxis transitions, latency to top,
        distance travelled, and positional 2D histograms.

        Args:
            tank_width (float): The width of the tank in centimeters.
            tank_height (float): The height of the tank in centimeters.
            num_bins_2D_hist (int, optional): The number of bins along each axis for the 2D histogram.
                Default is 10.

        Returns:
            stats_df (pd.DataFrame): A DataFrame containing the computed metrics for each day.
            histograms (np.ndarray): A 3D numpy array containing the 2D histograms for each day.
        """
        self.add_day_number()
        self.calculate_speed()
        self.set_activity_status()
        self.set_frantic_status()
        self.compute_zones()
        self.map_zones_to_integers()
        self.side_tigmotaxis()
        self.true_freezing()
        self.set_stress_status()
        self.set_bold_status()

        median_speeds               = list()
        gross_speeds                = list()

        median_activity_durations   = list()
        activity_fractions          = list()
        activity_duration_s         = list()

        median_freezing_durations   = list()
        freezing_fractions          = list()
        freezing_duration_s         = list()

        median_top_durations        = list()
        top_fractions               = list()
        top_duration_s              = list()

        median_bottom_durations     = list()
        bottom_fractions            = list()
        bottom_duration_s           = list()

        median_tigmotaxis_durations = list()
        tigmotaxis_fractions        = list()
        tigmotaxis_duration_s       = list()

        median_frantic_durations     = list()
        frantic_fractions            = list()
        frantic_duration_s           = list()

        median_stress_durations     = list()
        stress_fractions            = list()
        stress_duration_s           = list()

        median_bold_durations       = list()
        bold_fractions              = list()
        bold_duration_s             = list()

        tigmotaxis_transition_freq  = list()
        time_to_top                 = list()
        top_zone_entries            = list()
        distance_travelled          = list()
        histograms                  = list()
        stress_score                = list()
        

        for day in self.subject_df.Day_number.unique():
            day_data = self.subject_df.loc[self.subject_df.Day_number == day]
            total_time = day_data['Recording_time_s'].iloc[-1]

            # Median and gross speeds
            median_speeds.append(day_data.loc[day_data['activity'], 'speed_cmPs'].median())
            gross_speeds.append(day_data.speed_cmPs.median())

            # Bout metrics
            bout_metrics = self.calculate_bout_metrics_for_day(day_data, total_time)
            median_activity_durations.append(bout_metrics['Median_activity_duration_s'])
            activity_duration_s.append(bout_metrics['activity_duration_s'])
            activity_fractions.append(bout_metrics['activity_fraction'])
            median_freezing_durations.append(bout_metrics['Median_freezing_duration_s'])
            freezing_duration_s.append(bout_metrics['freezing_duration_s'])
            freezing_fractions.append(bout_metrics['freezing_fraction'])
            median_top_durations.append(bout_metrics['Median_in_top_margin_duration_s'])
            top_duration_s.append(bout_metrics['in_top_margin_duration_s'])
            top_fractions.append(bout_metrics['in_top_margin_fraction'])
            median_bottom_durations.append(bout_metrics['Median_in_bottom_margin_duration_s'])
            bottom_duration_s.append(bout_metrics['in_bottom_margin_duration_s'])
            bottom_fractions.append(bout_metrics['in_bottom_margin_fraction'])
            median_tigmotaxis_durations.append(bout_metrics['Median_tigmo_taxis_duration_s'])
            tigmotaxis_duration_s.append(bout_metrics['tigmo_taxis_duration_s'])
            tigmotaxis_fractions.append(bout_metrics['tigmo_taxis_fraction'])
            median_frantic_durations.append(bout_metrics['Median_frantic_duration_s'])
            frantic_duration_s.append(bout_metrics['frantic_duration_s'])
            frantic_fractions.append(bout_metrics['frantic_fraction'])
            median_stress_durations.append(bout_metrics['Median_stress_duration_s'])
            stress_duration_s.append(bout_metrics['stress_duration_s'])
            stress_fractions.append(bout_metrics['stress_fraction'])
            median_bold_durations.append(bout_metrics['Median_bold_duration_s'])
            bold_duration_s.append(bout_metrics['bold_duration_s'])
            bold_fractions.append(bout_metrics['bold_fraction'])
            
            # Stress Score
            stress_score.append((bout_metrics['stress_fraction']-bout_metrics['bold_fraction'])/(bout_metrics['stress_fraction']+bout_metrics['bold_fraction']))
            
            # Latency and transitions
            latency_and_transitions = self.calculate_latency_and_transitions_for_day(day_data)
            time_to_top.append(latency_and_transitions['Latency_to_top_s'])
            top_zone_entries.append(latency_and_transitions['top_zone_entries'])
            tigmotaxis_transition_freq.append(latency_and_transitions['Tigmotaxis_transitions']/total_time)

            # Distance travelled and 2D histogram
            distance, histogram = self.calculate_distance_and_histogram_for_day(day_data, tank_width, tank_height, num_bins_2D_hist)
            distance_travelled.append(distance)
            histograms.append(histogram)
        
        stats_df = pd.DataFrame({   'Day_number': self.subject_df.Day_number.unique(),
            'Median_speed_cmPs': median_speeds,
            'Gross_speed_cmPs': gross_speeds,
            'Median_activity_duration_s': median_activity_durations,
            'activity_duration_s': activity_duration_s,
            'Activity_fraction': activity_fractions,
            'Median_freezing_duration_s': median_freezing_durations,
            'freezing_duration_s': freezing_duration_s,
            'Freezing_fraction': freezing_fractions,
            'Median_top_duration_s': median_top_durations,
            'top_duration_s': top_duration_s,
            'Top_fraction': top_fractions,
            'Median_bottom_duration_s': median_bottom_durations,
            'bottom_duration_s': bottom_duration_s,
            'Bottom_fraction': bottom_fractions,
            'Median_tigmotaxis_duration_s': median_tigmotaxis_durations,
            'tigmotaxis_duration_s': tigmotaxis_duration_s,
            'Tigmotaxis_fraction': tigmotaxis_fractions,
            'Median__duration_s': median_stress_durations,
            'stress_duration_s': stress_duration_s,
            'stress_fraction': stress_fractions,
            'Median_boldness_duration_s': median_bold_durations,
            'boldness_duration_s': bold_duration_s,
            'boldness_fraction': bold_fractions,
            'stress_score': stress_score,
            'Tigmotaxis_transition_freq': tigmotaxis_transition_freq,
            'Latency_to_top_s': time_to_top,
            'top_zone_entries': top_zone_entries,
            'Distance_travelled_cm': distance_travelled
        })
        # add subject information
        stats_df =  self.add_subject_info(stats_df)

        # Combine the list of 2D histograms into a single 3D numpy array
        histograms = np.stack(histograms, axis=0)

        return stats_df,histograms
