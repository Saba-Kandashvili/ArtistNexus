import matplotlib.pyplot as plt
import pandas as pd


class Plotter:
    @staticmethod
    def create_figure():
        plt.style.use('fivethirtyeight')
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        # prevent label overlap
        fig.subplots_adjust(bottom=0.2)
        return fig, ax

    @staticmethod
    def plot_bar_chart(ax, series, title, xlabel, ylabel):
        if series is None or series.empty: return
        series.plot(kind='bar', ax=ax)
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.figure.autofmt_xdate(rotation=45, ha='right')

    @staticmethod
    def plot_pie_chart(ax, series, title):
        if series is None or series.empty: return

        # if there are more than 10 slices, use a legend instead of labels (but if theres too many slices this breaks ¯\_( ͡° ͜ʖ ͡°)_/¯ )
        if len(series) > 10:
                # Calculate percentages for each slice
                total = series.sum()
                percentages = [(value / total) * 100 for value in series]

                # Create legend labels with percentages
                legend_labels = [f"{index} ({percentage:.1f}%)" for index, percentage in zip(series.index, percentages)]

                ax.pie(series, labels=None, startangle=90)
                ax.legend(legend_labels, title="Genres", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        else:
            ax.pie(series, labels=series.index, autopct='%1.1f%%', startangle=90)

        ax.set_title(title, fontsize=16)
        ax.axis('equal')

    @staticmethod
    def plot_scatter_plot(ax, x_data, y_data, title, xlabel, ylabel):
        if x_data is None or y_data is None: return
        ax.scatter(x_data, y_data, alpha=0.5)
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xscale('log')

    @staticmethod
    def plot_histogram(ax, data, title, xlabel, bins=30):
        if data is None: return
        ax.hist(data, bins=bins, edgecolor='black')
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Number of Artists', fontsize=12)