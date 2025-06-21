# src/core/plotter.py (Upgraded Version)

import matplotlib.pyplot as plt
import pandas as pd

class Plotter:
    """
    Handles the creation of plots using Matplotlib.
    Contains static methods for generating different chart types.
    """

    @staticmethod
    def create_figure():
        """Creates a standard matplotlib figure and axes."""
        plt.style.use('fivethirtyeight')
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        return fig, ax

    @staticmethod
    def plot_bar_chart(ax, series: pd.Series, title: str, xlabel: str, ylabel: str):
        if series is None or series.empty: return
        series.plot(kind='bar', ax=ax)
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.figure.autofmt_xdate(rotation=45, ha='right')

    # --- NEW PLOTTING METHODS ---

    @staticmethod
    def plot_pie_chart(ax, series: pd.Series, title: str):
        if series is None or series.empty: return
        ax.pie(series, labels=series.index, autopct='%1.1f%%', startangle=90)
        ax.set_title(title, fontsize=16)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    @staticmethod
    def plot_scatter_plot(ax, x_data, y_data, title: str, xlabel: str, ylabel: str):
        if x_data is None or y_data is None: return
        ax.scatter(x_data, y_data, alpha=0.5)
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xscale('log') # Use a log scale for followers, as values can vary wildly

    @staticmethod
    def plot_histogram(ax, data, title: str, xlabel: str, bins=30):
        if data is None: return
        ax.hist(data, bins=bins, edgecolor='black')
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Number of Artists', fontsize=12)