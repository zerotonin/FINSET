import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import math

class IndividualAnalysisReportEthoVision:
    """
    A class to generate various plots for individual analysis based on EthoVision data.

    Attributes
    ----------
    result_df : pandas.DataFrame
        Dataframe containing EthoVision results data.
    histograms : numpy.ndarray
        3D numpy array containing histograms of fish positions for each day.
    tank_width : float, optional
        Width of the tank in centimeters (default is 20.5).
    tank_height : float, optional
        Height of the tank in centimeters (default is 20.5).

    Methods
    -------
    plot_bout_metrics():
        Plots bout metrics and fractions for activity, freezing, and tigmotaxis.
    plot_velocity_metrics():
        Plots velocity metrics, including median and gross velocity, and distance travelled.
    plot_bout_and_transition_metrics():
        Plots bout and transition metrics for top and bottom fractions, durations, and tigmotaxis transitions.
    plot_normalized_histograms():
        Plots the normalized histograms of fish positions for each day.
    report():
        Generates all the plots and returns the figure handles.
    """
    
    def __init__(self, result_df, histograms,tank_width = 20.5, tank_height = 20.5):
        self.result_df = result_df
        self.histograms = histograms
        self.tank_width = tank_width
        self.tank_height = tank_height

    def plot_bout_metrics(self):
        """
        Plots bout metrics and fractions for activity, freezing, tigmotaxis, frantic, boldness and stress.
        Transposes the original layout to have bout metrics as rows and data features as columns.

        Returns
        -------
        matplotlib.figure.Figure
            A figure containing the transposed subplots of bout metrics and fractions.
        """
        # Extract the necessary data from the self.result_df
        days = self.result_df['Day_number']
        metrics = [
            ('Median_activity_duration_s',  'activity_duration_s', 'Activity_fraction', 'Activity'),
            ('Median_freezing_duration_s',  'freezing_duration_s', 'Freezing_fraction', 'Freezing'),
            ('Median_tigmotaxis_duration_s','tigmotaxis_duration_s', 'Tigmotaxis_fraction', 'Tigmotaxis'),
            ('Median_frantic_duration_s',   'frantic_duration_s', 'frantic_fraction', 'Frantic'),
            ('Median_boldness_duration_s',  'boldness_duration_s', 'boldness_fraction', 'Boldness'),
            ('Median_stress_duration_s',    'stress_duration_s', 'stress_fraction', 'Stress')
        ]

        # Create a figure with subplots for bout metrics and fractions
        fig, axes = plt.subplots(3, len(metrics), figsize=(24, 12))
        fig.tight_layout(pad=4)

        for i, (duration_col, total_dur_col, fraction_col, title_prefix) in enumerate(metrics):

            # Plot total_duration
            axes[0, i].plot(days, self.result_df[total_dur_col], marker='o')
            axes[0, i].set_xlabel('Day number')
            axes[0, i].set_ylabel(f'{title_prefix.lower()} total duration (s)')
            axes[0, i].set_title(f'{title_prefix} Total Duration over Days')

            # Plot median durations
            axes[1, i].plot(days, self.result_df[duration_col], marker='o')
            axes[1, i].set_xlabel('Day number')
            axes[1, i].set_ylabel(f'Median {title_prefix.lower()} bout duration (s)')
            axes[1, i].set_title(f'Median {title_prefix} Bout Duration over Days')

            # Plot fractions
            axes[2, i].plot(days, self.result_df[fraction_col], marker='o')
            axes[2, i].set_xlabel('Day number')
            axes[2, i].set_ylabel(f'{title_prefix.lower()} fraction')
            axes[2, i].set_title(f'{title_prefix} Fraction over Days')

        return fig




    def plot_velocity_metrics(self):
        """
        Plots velocity metrics, including median and gross velocity, and distance travelled.

        Returns
        -------
        matplotlib.figure.Figure
            A figure containing the subplots of velocity metrics.
        """
        # Extract the necessary data from the self.result_df
        days = self.result_df['Day_number']
        metrics = [
            ('Median_speed_cmPs', 'Gross_speed_cmPs', 'Velocity (cm/s)'),
            ('Distance_travelled_cm', '', 'Distance travelled (cm)'),
        ]

        # Create a figure with subplots for velocity metrics
        fig, axes = plt.subplots(len(metrics), 1, figsize=(8, 12))
        fig.tight_layout(pad=4)

        for i, (metric_col1, metric_col2, ylabel) in enumerate(metrics):
            if metric_col2 != '':
                # Plot metric data with two series in the same axis
                axes[i].plot(days, self.result_df[metric_col1], marker='o', label='Median')
                axes[i].plot(days, self.result_df[metric_col2], marker='o', label='Gross')
                axes[i].legend()
            else:
                # Plot metric data with a single series
                axes[i].plot(days, self.result_df[metric_col1], marker='o')
            
            axes[i].set_xlabel('Day number')
            axes[i].set_ylabel(ylabel)
            axes[i].set_title(f'{ylabel} over Days')

        return fig
    def plot_bout_and_transition_metrics(self):
        """
        Plots bout and transition metrics for top and bottom fractions, durations, and tigmotaxis transitions.

        Returns
        -------
        matplotlib.figure.Figure
            A figure containing the subplots of bout and transition metrics.
        """
        # Extract the necessary data from the self.result_df
        days = self.result_df['Day_number']
        metrics = [
            ('top_duration_s', 'total top duration (s)'),
            ('Median_top_duration_s', 'top bout duration (s)'),
            ('Top_fraction', 'Top fraction'),
            ('bottom_duration_s', 'total bottom duration (s)'),
            ('Median_bottom_duration_s', 'bottom bout duration (s)'),
            ('Bottom_fraction', 'Bottom fraction'),
            ('Latency_to_top_s', 'Latency to top (s)'),
            ('top_zone_entries', 'entries into top zone'),
            ('Tigmotaxis_transition_freq', 'Tigmotaxis transition frequency, Hz')
        ]

        # Create a figure with subplots for bout and transition metrics
        fig, axes = plt.subplots(int(len(metrics)/3), 3, figsize=(18, 18))
        axes = axes.flatten()
        fig.tight_layout(pad=4)

        for i, (metric_col, ylabel) in enumerate(metrics):
            # Plot metric data
            axes[i].plot(days, self.result_df[metric_col], marker='o')
            axes[i].set_xlabel('Day number')
            axes[i].set_ylabel(ylabel)

        return fig

    def plot_normalized_histograms(self):
        """
        Plots the normalized histograms of fish positions for each day.

        Returns
        -------
        matplotlib.figure.Figure
            A figure containing the subplots of normalized histograms of fish positions.
        """
        num_days = self.histograms.shape[0]
        x_bins = np.linspace(0, self.tank_width, self.histograms.shape[1] + 1)
        y_bins = np.linspace(0, self.tank_height, self.histograms.shape[2] + 1)

        num_rows = int(math.ceil(math.sqrt(num_days)))
        num_cols = int(math.ceil(num_days / num_rows))

        fig, axes = plt.subplots(num_rows, num_cols, figsize=(18, 6 * num_rows), sharex=True, sharey=True)
        fig.tight_layout(pad=2)

        # Normalize the histograms
        normalized_histograms = self.histograms / self.histograms.sum(axis=(1, 2), keepdims=True)

        # Flatten axes array for easy indexing
        axes_flat = axes.flatten()

        for i, ax in enumerate(axes_flat[:num_days]):
            im = ax.imshow(
                normalized_histograms[i].T,
                origin='lower',
                extent=[x_bins[0], x_bins[-1], y_bins[0], y_bins[-1]],
                aspect='equal',
                cmap='plasma',
                norm=LogNorm(vmin=1e-5, vmax=1),  # Logarithmic normalization
            )
            ax.set_xlabel('Tank width (cm)')
            ax.set_title(f'Day {i + 1}')

        axes_flat[0].set_ylabel('Tank height (cm)')

        # Remove extra subplots if any
        for ax in axes_flat[num_days:]:
            ax.remove()

        # Add a colorbar
        cbar_ax = fig.add_axes([0.93, 0.15, 0.01, 0.7])
        fig.colorbar(im, cax=cbar_ax, label='Normalized frequency')

        return fig
    
    def plot_stress_score(self):
        days = self.result_df['Day_number']
        fig, axes = plt.subplots(figsize=(10, 6))
        axes.plot(days, self.result_df.stress_score, marker='o',label='stress score')
        axes.axhline(0, color='red', linestyle='--',label='chance level')  # Add a horizontal line at y=0
        axes.set_xlabel('Day number')
        axes.set_ylabel(f'stress score')
        axes.set_title(f'Stress score defined as (s-b)/(s+b)')
        axes.legend(loc='best')
        return fig


    def report(self):
        """
        Generates all the plots and returns the figure handles.

        Returns
        -------
        tuple
            A tuple containing the figure handles for the bout metrics, velocity metrics,
            bout and transition metrics, and normalized histograms plots.
        """
        f1 = self.plot_bout_metrics()
        f2 = self.plot_velocity_metrics()
        f3 = self.plot_bout_and_transition_metrics()
        f4 = self.plot_normalized_histograms()
        f5 = self.plot_stress_score()

        return f1, f2, f3, f4, f5