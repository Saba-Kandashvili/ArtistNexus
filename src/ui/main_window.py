# src/ui/main_window.py (Advanced UI Version)

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.data_analyzer import DataAnalyzer
from core.plotter import Plotter


class AppGUI(tk.Tk):
    def __init__(self, db_path):
        super().__init__()
        self.analyzer = DataAnalyzer(db_path)
        self.title("ArtistNexus: Global Music Analyzer")
        self.geometry("1200x800")
        self.create_widgets()

    def create_widgets(self):
        # --- Main Layout Frames ---
        controls_frame = ttk.Frame(self, width=250, padding="10")
        controls_frame.pack(side="left", fill="y")
        self.plot_frame = ttk.Frame(self, padding="10")
        self.plot_frame.pack(side="right", expand=True, fill="both")
        status_bar_frame = ttk.Frame(self, relief="sunken", padding=(5, 2))
        status_bar_frame.pack(side="bottom", fill="x")

        self.status_label = ttk.Label(status_bar_frame, text="Welcome to ArtistNexus!")
        self.status_label.pack(side="left")

        # --- Controls in the Sidebar ---
        ttk.Label(controls_frame, text="Select Analysis Type:", font="-weight bold").pack(anchor="w", pady=5)

        self.analysis_var = tk.StringVar(value="followers_by_country")

        # Using Radiobuttons for a clearer choice
        ttk.Radiobutton(controls_frame, text="Top Countries by Followers", variable=self.analysis_var,
                        value="followers_by_country").pack(anchor="w")
        ttk.Radiobutton(controls_frame, text="Top Countries by Avg Popularity", variable=self.analysis_var,
                        value="popularity_by_country").pack(anchor="w")
        ttk.Radiobutton(controls_frame, text="Genre Distribution by Country", variable=self.analysis_var,
                        value="genre_distribution").pack(anchor="w")
        ttk.Radiobutton(controls_frame, text="Popularity vs. Followers", variable=self.analysis_var,
                        value="pop_vs_followers").pack(anchor="w")
        ttk.Radiobutton(controls_frame, text="Overall Popularity Distribution", variable=self.analysis_var,
                        value="popularity_histogram").pack(anchor="w")

        # --- Dynamic Parameter Controls ---
        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(controls_frame, text="Analysis Parameters:", font="-weight bold").pack(anchor="w", pady=5)

        # Country selector
        ttk.Label(controls_frame, text="Select Country:").pack(anchor="w")
        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(controls_frame, textvariable=self.country_var,
                                             values=self.analyzer.get_available_countries(), state="readonly")
        self.country_dropdown.pack(anchor="w", fill="x")
        self.country_dropdown.set("United States")  # Default value

        # 'Top N' selector
        ttk.Label(controls_frame, text="Number of results (N):").pack(anchor="w", pady=(10, 0))
        self.n_var = tk.IntVar(value=15)
        ttk.Spinbox(controls_frame, from_=5, to=30, textvariable=self.n_var).pack(anchor="w", fill="x")

        # --- The Main Button ---
        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=20)
        analyze_button = ttk.Button(controls_frame, text="Generate Plot", command=self._on_analyze_button_click)
        analyze_button.pack(anchor="w", fill="x", ipady=5)

        self.canvas = None

    def _on_analyze_button_click(self):
        analysis_type = self.analysis_var.get()
        n = self.n_var.get()
        country = self.country_var.get()

        self.status_label.config(text=f"Generating plot for {analysis_type}...")
        self.update_idletasks()  # Force UI update

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        fig, ax = Plotter.create_figure()

        if analysis_type == "followers_by_country":
            data = self.analyzer.get_top_n_countries_by_followers(n)
            Plotter.plot_bar_chart(ax, data, f"Top {n} Countries by Followers", "Country", "Total Followers")
        elif analysis_type == "popularity_by_country":
            data = self.analyzer.get_top_n_countries_by_avg_popularity(n)
            Plotter.plot_bar_chart(ax, data, f"Top {n} Countries by Avg Popularity", "Country", "Avg Popularity Score")
        elif analysis_type == "genre_distribution":
            data = self.analyzer.get_genre_distribution_for_country(country, n)
            Plotter.plot_pie_chart(ax, data, f"Top {n} Genres in {country}")
        elif analysis_type == "pop_vs_followers":
            x_data, y_data = self.analyzer.get_popularity_vs_followers(country)
            Plotter.plot_scatter_plot(ax, x_data, y_data, f"Popularity vs Followers in {country}",
                                      "Followers (log scale)", "Popularity Score")
        elif analysis_type == "popularity_histogram":
            data = self.analyzer.get_popularity_distribution()
            Plotter.plot_histogram(ax, data, "Overall Artist Popularity Distribution", "Popularity Score")

        fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.status_label.config(text="Plot generated successfully.")