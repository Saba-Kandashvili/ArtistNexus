# src/core/plotter.py

import matplotlib.pyplot as plt
import pandas as pd


class Plotter:
    """
    Handles the creation of plots using Matplotlib.

    This class contains static methods to generate different types of charts
    from Pandas Series or DataFrame objects.
    """

    @staticmethod
    def plot_bar_chart(series: pd.Series, title: str, xlabel: str, ylabel: str):
        """
        Generates and displays a bar chart from a Pandas Series.

        This method is designed for testing and direct visualization. It will
        open a window to show the plot.

        Args:
            series (pd.Series): The data to plot. The series index will be used
                                for the x-axis labels, and values for the bar heights.
            title (str): The title of the chart.
            xlabel (str): The label for the x-axis.
            ylabel (str): The label for the y-axis.
        """
        if series is None or series.empty:
            print("Cannot plot: The data series is empty or None.")
            return

        # Use a professional-looking style for the plot
        plt.style.use('fivethirtyeight')

        # Create a figure and an axes object. figsize is in inches.
        fig, ax = plt.subplots(figsize=(12, 8))

        # Create the bar plot on the specified axes
        series.plot(kind='bar', ax=ax)

        # --- Customize the plot for better readability ---
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)

        # Rotate the x-axis labels (e.g., country names) to prevent overlap
        plt.xticks(rotation=45, ha='right')

        # Ensure all plot elements fit nicely into the figure area
        plt.tight_layout()

        # Display the plot in a new window
        plt.show()