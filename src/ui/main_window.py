# src/ui/main_window.py (Final Polished Version)

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# New imports for image handling and web browsing
import requests
from PIL import Image, ImageTk
from io import BytesIO
import webbrowser

from core.data_analyzer import DataAnalyzer
from core.plotter import Plotter


class AppGUI(tk.Tk):
    def __init__(self, db_path):
        super().__init__()
        self.analyzer = DataAnalyzer(db_path)
        self.title("ArtistNexus: Global Music Analyzer")
        self.geometry("1200x800")

        # --- NEW ROBUSTNESS CHECK ---
        if self.analyzer.df is None or self.analyzer.df.empty:
            # If no data was loaded, show an error and don't create the controls.
            error_label = ttk.Label(self, text="FATAL ERROR: Could not load data from database.\n"
                                               "Please ensure artist_data.db exists and is not corrupted.",
                                    font=("-size", 14), foreground="red", justify="center")
            error_label.pack(expand=True, padx=20, pady=20)
        else:
            # Only create the widgets if data loading was successful
            self.create_widgets()

    def create_widgets(self):
        # --- Layout Frames ---
        controls_frame = ttk.Frame(self, width=300, padding="10")
        controls_frame.pack(side="left", fill="y")

        main_content_frame = ttk.Frame(self, padding="10")
        main_content_frame.pack(side="right", expand=True, fill="both")

        self.info_label = ttk.Label(main_content_frame,
                                    text="Select an analysis from the left panel and click 'Generate Plot'.",
                                    wraplength=800, justify="center", font=("-size", 12))
        self.info_label.pack(side="top", fill="x", pady=10)

        self.plot_frame = ttk.Frame(main_content_frame)
        self.plot_frame.pack(expand=True, fill="both")

        # --- Sidebar Controls ---
        # ... (same as before) ...
        ttk.Label(controls_frame, text="Select Analysis Type:", font="-weight bold").pack(anchor="w", pady=5)
        self.analysis_var = tk.StringVar(value="followers_by_country")
        analysis_types = [
            ("Top Countries by Followers", "followers_by_country"),
            ("Top Countries by Avg Popularity", "popularity_by_country"),
            ("Genre Distribution by Country", "genre_distribution"),
            ("Popularity vs. Followers", "pop_vs_followers"),
            ("Overall Popularity Distribution", "popularity_histogram")
        ]
        for text, value in analysis_types:
            ttk.Radiobutton(controls_frame, text=text, variable=self.analysis_var, value=value,
                            command=self._on_analysis_type_change).pack(anchor="w")

        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(controls_frame, text="Analysis Parameters:", font="-weight bold").pack(anchor="w", pady=5)

        self.country_label = ttk.Label(controls_frame, text="Select Country:")
        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(controls_frame, textvariable=self.country_var,
                                             values=self.analyzer.get_available_countries(), state="readonly")
        self.country_dropdown.set("United States")

        self.n_label = ttk.Label(controls_frame, text="Number of results (N):")
        self.n_var = tk.IntVar(value=10)  # Default to 10 for pie chart readability
        self.n_spinbox = ttk.Spinbox(controls_frame, from_=5, to=30, textvariable=self.n_var)

        # --- NEW: Artist Info Panel ---
        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=10)
        self.artist_info_frame = ttk.LabelFrame(controls_frame, text="Artist Spotlight", padding=10)
        self.artist_info_frame.pack(fill='x', pady=10)
        self.artist_image_label = ttk.Label(self.artist_info_frame)
        self.artist_name_label = ttk.Label(self.artist_info_frame, text="", font="-weight bold")
        self.artist_link_label = ttk.Label(self.artist_info_frame, text="", foreground="blue", cursor="hand2")

        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=20)
        analyze_button = ttk.Button(controls_frame, text="Generate Plot", command=self._on_analyze_button_click)
        analyze_button.pack(anchor="w", fill="x", ipady=5)

        self.canvas = None
        self._on_analysis_type_change()  # Call once to set initial UI state

    def _on_analysis_type_change(self):
        """Shows/hides parameter controls based on analysis type."""
        analysis_type = self.analysis_var.get()
        # Hide all parameter widgets initially
        self.country_label.pack_forget()
        self.country_dropdown.pack_forget()
        self.n_label.pack_forget()
        self.n_spinbox.pack_forget()

        # Show widgets based on selection
        if analysis_type in ["followers_by_country", "popularity_by_country"]:
            self.n_label.pack(anchor="w", pady=(10, 0))
            self.n_spinbox.pack(anchor="w", fill="x")
        elif analysis_type in ["genre_distribution", "pop_vs_followers"]:
            self.country_label.pack(anchor="w")
            self.country_dropdown.pack(anchor="w", fill="x")
            if analysis_type == "genre_distribution":
                self.n_label.pack(anchor="w", pady=(10, 0))
                self.n_spinbox.pack(anchor="w", fill="x")

    def _update_artist_spotlight(self, country):
        """Fetches the most popular artist from a country and displays their info."""
        artist_info = self.analyzer.get_most_popular_artist_in_country(country)
        if not artist_info: return

        self.artist_name_label.config(text=artist_info['artist_name'])
        self.artist_link_label.config(text="View on Spotify")
        self.artist_link_label.bind("<Button-1>", lambda e: webbrowser.open(artist_info['spotify_url']))

        self.artist_name_label.pack()
        self.artist_link_label.pack()

        # Image loading
        if artist_info['image_url']:
            try:
                response = requests.get(artist_info['image_url'])
                response.raise_for_status()  # Raise an exception for bad status codes
                img_data = response.content
                img = Image.open(BytesIO(img_data))
                img.thumbnail((200, 200))  # Resize image to fit panel
                self.photo_image = ImageTk.PhotoImage(img)
                self.artist_image_label.config(image=self.photo_image)
                self.artist_image_label.pack()
            except requests.exceptions.RequestException as e:
                self.artist_image_label.pack_forget()  # Hide if image fails to load
                print(f"Error loading image: {e}")

    def _on_analyze_button_click(self):
        analysis_type = self.analysis_var.get()
        n = self.n_var.get()
        country = self.country_var.get()

        if self.canvas: self.canvas.get_tk_widget().destroy()
        fig, ax = Plotter.create_figure()

        description = ""
        # Hide artist spotlight by default, show it only when relevant
        self.artist_info_frame.pack_forget()

        if analysis_type == "followers_by_country":
            data = self.analyzer.get_top_n_countries_by_followers(n)
            Plotter.plot_bar_chart(ax, data, "", "Country", "Total Followers (Log Scale)")
            ax.set_yscale('log')  # Use log scale for better visualization of wide-ranging data
            description = f"This bar chart displays the top {n} countries ranked by the total combined Spotify followers of all their artists in the dataset. A logarithmic scale is used on the Y-axis to better visualize the vast differences between countries."
        elif analysis_type == "popularity_by_country":
            data = self.analyzer.get_top_n_countries_by_avg_popularity(n)
            Plotter.plot_bar_chart(ax, data, "", "Country", "Average Popularity Score")
            description = f"This chart shows the top {n} countries ranked by the average Spotify Popularity Score of their artists. This metric highlights countries that produce artists who are, on average, highly popular right now."
        elif analysis_type == "genre_distribution":
            data = self.analyzer.get_genre_distribution_for_country(country, n)
            Plotter.plot_pie_chart(ax, data, "")
            description = f"This pie chart shows the breakdown of the top {n} most common music genres for artists from {country}. It provides a snapshot of the country's musical identity."
            self.artist_info_frame.pack(fill='x', pady=10)  # Show the artist frame
            self._update_artist_spotlight(country)
        elif analysis_type == "pop_vs_followers":
            x_data, y_data = self.analyzer.get_popularity_vs_followers(country)
            Plotter.plot_scatter_plot(ax, x_data, y_data, "", "Followers (log scale)", "Popularity Score")
            description = f"This scatter plot explores the relationship between an artist's long-term fanbase (followers) and their current relevance (popularity) in {country}. Each dot represents an artist."
            self.artist_info_frame.pack(fill='x', pady=10)
            self._update_artist_spotlight(country)
        elif analysis_type == "popularity_histogram":
            data = self.analyzer.get_popularity_distribution()
            Plotter.plot_histogram(ax, data, "", "Popularity Score")
            description = "This histogram shows the overall distribution of artist popularity scores across the entire dataset. It reveals that most artists have a moderate popularity score, with true superstars being relatively rare."

        self.info_label.config(text=description)
        fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)