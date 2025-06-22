# src/ui/main_window.py (Final Version with Threaded Export)

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import requests
from PIL import Image, ImageTk
from io import BytesIO
import webbrowser
import threading
import os
import time  # Needed for unique filenames

from core.data_analyzer import DataAnalyzer
from core.plotter import Plotter


class AppGUI(tk.Tk):
    def __init__(self, db_path):
        super().__init__()
        self.analyzer = DataAnalyzer(db_path)
        self.title("ArtistNexus: Global Music Analyzer")
        self.geometry("1200x800")

        self.current_figure = None

        if self.analyzer.df is None or self.analyzer.df.empty:
            error_label = ttk.Label(self, text="FATAL ERROR: Could not load data from database.\n"
                                               "Please ensure artist_data.db exists and is not corrupted.",
                                    font=("-size", 14), foreground="red", justify="center")
            error_label.pack(expand=True, padx=20, pady=20)
        else:
            self.create_widgets()

    def create_widgets(self):
        # laout
        controls_frame = ttk.Frame(self, width=300, padding="10")
        controls_frame.pack(side="left", fill="y")

        main_content_frame = ttk.Frame(self, padding="10")
        main_content_frame.pack(side="right", expand=True, fill="both")

        # status bar (looks ugly might delete)
        status_bar_frame = ttk.Frame(self, relief="sunken", padding=(5, 2))
        status_bar_frame.pack(side="bottom", fill="x")
        self.status_label = ttk.Label(status_bar_frame, text="Welcome to ArtistNexus! Select an analysis to begin.")
        self.status_label.pack(side="left")

        # main content
        self.info_label = ttk.Label(main_content_frame,
                                    text="Select an analysis from the left panel and click 'Generate Plot'.",
                                    wraplength=800, justify="center", font=("-size", 12))
        self.info_label.pack(side="top", fill="x", pady=10)

        self.plot_frame = ttk.Frame(main_content_frame)
        self.plot_frame.pack(expand=True, fill="both")

        # sidebar
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
        self.n_var = tk.IntVar(value=10)
        self.n_spinbox = ttk.Spinbox(controls_frame, from_=5, to=30, textvariable=self.n_var)

        # artist panel
        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=10)
        self.artist_info_frame = ttk.LabelFrame(controls_frame, text="Artist Spotlight", padding=10)
        self.artist_info_frame.pack(fill='x', pady=10)
        self.artist_image_label = ttk.Label(self.artist_info_frame)
        self.artist_name_label = ttk.Label(self.artist_info_frame, text="", font="-weight bold")
        self.artist_link_label = ttk.Label(self.artist_info_frame, text="", foreground="blue", cursor="hand2")

        # buttoons
        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=20)
        analyze_button = ttk.Button(controls_frame, text="Generate Plot", command=self._on_analyze_button_click)
        analyze_button.pack(anchor="w", fill="x", ipady=5)

        # export as png
        self.export_button = ttk.Button(controls_frame, text="Export Plot as PNG",
                                        command=self._on_export_button_click, state="disabled")
        self.export_button.pack(anchor="w", fill="x", ipady=5, pady=5)

        self.canvas = None
        self._on_analysis_type_change()

    def _on_analysis_type_change(self):
        analysis_type = self.analysis_var.get()
        self.country_label.pack_forget()
        self.country_dropdown.pack_forget()
        self.n_label.pack_forget()
        self.n_spinbox.pack_forget()

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
        artist_info = self.analyzer.get_most_popular_artist_in_country(country)
        if not artist_info:
            self.artist_name_label.config(text=f"No artist data for {country}.")
            self.artist_link_label.pack_forget()
            self.artist_image_label.pack_forget()
            self.artist_name_label.pack()
            return

        # artist name
        self.artist_name_label.config(text=artist_info.get('artist_name', 'Unknown Artist'))
        self.artist_name_label.pack()

        # spotify url might be null
        if artist_info.get('spotify_url'):
            self.artist_link_label.config(text="View on Spotify", foreground="blue", cursor="hand2")
            self.artist_link_label.bind("<Button-1>", lambda e: webbrowser.open(artist_info['spotify_url']))
            self.artist_link_label.pack()
        else:
            self.artist_link_label.config(text="No Spotify link available", foreground="gray", cursor="")
            self.artist_link_label.pack()

        # image url might be null
        self.artist_image_label.pack_forget()
        if artist_info.get('image_url'):
            try:
                response = requests.get(artist_info['image_url'])
                response.raise_for_status()
                img_data = response.content
                img = Image.open(BytesIO(img_data))
                img.thumbnail((200, 200))
                self.photo_image = ImageTk.PhotoImage(img)
                self.artist_image_label.config(image=self.photo_image)
                self.artist_image_label.pack()
            except requests.exceptions.RequestException as e:
                print(f"Error loading image: {e}")

    def _on_analyze_button_click(self):
        analysis_type = self.analysis_var.get()
        n = self.n_var.get()
        country = self.country_var.get()

        if self.canvas: self.canvas.get_tk_widget().destroy()

        fig, ax = Plotter.create_figure()
        self.current_figure = fig

        description = ""
        self.artist_info_frame.pack_forget()

        if analysis_type == "followers_by_country":
            data = self.analyzer.get_top_n_countries_by_followers(n)
            Plotter.plot_bar_chart(ax, data, "", "Country", "Total Followers (Log Scale)")
            ax.set_yscale('log')
            description = f"This bar chart displays the top {n} countries ranked by the total combined Spotify followers... (etc.)"
        elif analysis_type == "popularity_by_country":
            data = self.analyzer.get_top_n_countries_by_avg_popularity(n)
            Plotter.plot_bar_chart(ax, data, "", "Country", "Average Popularity Score")
            description = f"This chart shows the top {n} countries ranked by the average Spotify Popularity Score... (etc.)"
        elif analysis_type == "genre_distribution":
            data = self.analyzer.get_genre_distribution_for_country(country, n)
            Plotter.plot_pie_chart(ax, data, "")
            description = f"This pie chart shows the breakdown of the top {n} most common music genres for artists from {country}."
            self.artist_info_frame.pack(fill='x', pady=10)
            self._update_artist_spotlight(country)
        elif analysis_type == "pop_vs_followers":
            x_data, y_data = self.analyzer.get_popularity_vs_followers(country)
            Plotter.plot_scatter_plot(ax, x_data, y_data, "", "Followers (log scale)", "Popularity Score")
            description = f"This scatter plot explores the relationship between an artist's long-term fanbase (followers) and their current relevance (popularity) in {country}."
            self.artist_info_frame.pack(fill='x', pady=10)
            self._update_artist_spotlight(country)
        elif analysis_type == "popularity_histogram":
            data = self.analyzer.get_popularity_distribution()
            Plotter.plot_histogram(ax, data, "", "Popularity Score")
            description = "This histogram shows the overall distribution of artist popularity scores across the entire dataset."

        self.info_label.config(text=description)
        fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.export_button.config(state="normal")
        self.status_label.config(text="Plot generated successfully. Ready for next analysis.")

    def _on_export_button_click(self):
        if self.current_figure is None:
            return

        self.export_button.config(state="disabled")
        self.status_label.config(text="Exporting plot to PNG...")

        export_thread = threading.Thread(target=self._export_current_plot)
        export_thread.start()

    def _export_current_plot(self):
        try:
            if not os.path.exists('reports'):
                os.makedirs('reports')

            filename = f"chart_export_{int(time.time())}.png"
            filepath = os.path.join('reports', filename)

            self.current_figure.savefig(filepath, dpi=150, bbox_inches='tight')

            self.after(0, self.status_label.config, {'text': f"Successfully exported to {filepath}"})

        except Exception as e:
            self.after(0, self.status_label.config, {'text': f"Error exporting plot: {e}"})

        finally:
            self.after(0, self.export_button.config, {'state': "normal"})