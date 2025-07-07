from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
from datetime import datetime
import pandas as pd
from time import sleep
from threading import Thread
import os
from random import randint

# Initial configuration
BASE_PRICE = 10

# Pricing logic: price increases linearly with occupancy
def baseline_price(prev_price, occupancy, capacity, alpha=1.0):
    if capacity == 0:
        return prev_price
    return prev_price + alpha * (occupancy / capacity)

# Set up the data source and initial dummy point to ensure plot starts with data
source = ColumnDataSource(data=dict(time=[], price=[]))
source.stream(dict(time=[datetime.now()], price=[randint(10, 50)]))

# Create the figure
p = figure(x_axis_type='datetime',
           title="Real-Time Parking Price",
           height=400,
           sizing_mode='stretch_width')

# Add line and scatter points
p.line(x='time', y='price', source=source, line_width=2, color='blue')
p.scatter(x='time', y='price', source=source, size=6, color='red')

# Configure axes
p.yaxis.axis_label = "Price ($)"
p.xaxis.axis_label = "Time"
p.y_range.start = 0
p.y_range.end = 100

# Streaming function that runs in the background
def stream_data():
    try:
        # Load dataset
        csv_path = os.path.join(os.path.dirname(__file__), "../data/dataset.csv")
        df = pd.read_csv(os.path.abspath(csv_path))
        print("CSV loaded successfully. Number of rows:", len(df))
    except Exception as e:
        print("Error loading CSV file:", e)
        return

    current_price = BASE_PRICE

    for index, row in df.iterrows():
        try:
            occupancy = row['Occupancy']
            capacity = row['Capacity']
            current_price = baseline_price(current_price, occupancy, capacity)
            now = datetime.now()

            def update_plot():
                source.stream(dict(time=[now], price=[current_price]), rollover=100)

            curdoc().add_next_tick_callback(update_plot)
            print(f"Row {index + 1}: Occupancy {occupancy}/{capacity} → Price: ${current_price:.2f}")
            sleep(1)

        except Exception as e:
            print("Error processing row", index, ":", e)

# Start the data stream in a separate thread
Thread(target=stream_data, daemon=True).start()

# Add the plot to the Bokeh document
curdoc().add_root(column(p))
