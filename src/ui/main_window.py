# src/ui/main_window.py

import tkinter as tk
from tkinter import ttk  # Themed tkinter widgets for a more modern look

# Used to embed Matplotlib plots in tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Import our backend classes
from src.core.data_analyzer import DataAnalyzer
from src.core.plotter import Plotter




class AppGUI(tk.Tk):
    """
    The main Graphical User Interface for the ArtistNexus application.

    This class inherits from tk.Tk to become the main window and manages all
    the UI elements and their interactions with the backend.
    """

    def __init__(self, db_path):
        """
        Initializes the main application window.

        Args:
            db_path (str): Path to the application's database file.
        """
        super().__init__()  # Initialize the parent tk.Tk class

        # --- Backend Setup ---
        self.analyzer = DataAnalyzer(db_path)

        # --- Window Configuration ---
        self.title("ArtistNexus: Global Music Analyzer")
        self.geometry("1000x700")  # Set a default size

        # --- UI Components ---
        self.plot_frame = None
        self.canvas = None
        self.create_widgets()

    def create_widgets(self):
        """Creates and arranges all the UI widgets in the window."""

        # --- Create a main frame to hold all controls ---
        controls_frame = ttk.Frame(self, padding="10")
        controls_frame.pack(side="top", fill="x")

        # --- Analysis Type Dropdown ---
        ttk.Label(controls_frame, text="Select Analysis:").pack(side="left", padx=5)

        self.analysis_var = tk.StringVar()
        analysis_options = [
            "Top Countries by Total Followers",
            "Top Countries by Average Popularity"
        ]
        self.analysis_dropdown = ttk.Combobox(
            controls_frame,
            textvariable=self.analysis_var,
            values=analysis_options,
            state="readonly"  # Prevents user from typing a custom value
        )
        self.analysis_dropdown.pack(side="left", padx=5)
        self.analysis_dropdown.set(analysis_options[0])  # Set a default value

        # --- Analyze Button ---
        analyze_button = ttk.Button(controls_frame, text="Generate Plot", command=self._on_analyze_button_click)
        analyze_button.pack(side="left", padx=10)

        # --- Frame to hold the plot ---
        self.plot_frame = ttk.Frame(self, padding="10")
        self.plot_frame.pack(expand=True, fill="both")

    def _on_analyze_button_click(self):
        """Handles the event when the 'Generate Plot' button is clicked."""
        selected_analysis = self.analysis_var.get()

        # Call the correct analyzer method based on dropdown selection
        if selected_analysis == "Top Countries by Total Followers":
            data = self.analyzer.get_top_n_countries_by_followers()
            title = "Top 15 Countries by Combined Artist Followers"
            ylabel = "Total Followers (in Billions)"
        elif selected_analysis == "Top Countries by Average Popularity":
            data = self.analyzer.get_top_n_countries_by_avg_popularity()
            title = "Top 15 Countries by Average Artist Popularity"
            ylabel = "Average Popularity Score"
        else:
            return  # Should not happen

        # Update the plot with the new data
        self.embed_plot(data, title, "Country", ylabel)

    def embed_plot(self, series, title, xlabel, ylabel):
        """
        Clears the old plot and embeds a new Matplotlib plot in the GUI.
        """
        # If a canvas already exists, destroy it to make way for the new one
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        if series is None or series.empty:
            print("Cannot plot: The data series is empty or None.")
            return

        # --- Matplotlib Figure Creation ---
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Plot the data onto the axes
        series.plot(kind='bar', ax=ax, title=title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        # Customize for readability
        fig.autofmt_xdate(rotation=45, ha='right')
        fig.tight_layout()

        # --- Embedding in Tkinter ---
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        # The .get_tk_widget() method returns the tkinter-compatible widget
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)