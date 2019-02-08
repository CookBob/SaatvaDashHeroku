import math
from bokeh.io import curdoc

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

from bokeh.models.widgets import RangeSlider, Button, DataTable, TableColumn, NumberFormatter

from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable
from bokeh.models.widgets import CheckboxButtonGroup

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.models.widgets import Div

def histogram_tab(saatva):
    impressions_log_df = saatva[['Device','Impressions']]
    impressions_log_df['LogImp'] = (1+impressions_log_df['Impressions']).apply(math.log10)
    
    available_devices = list(impressions_log_df['Device'].unique())
    device_selection = available_devices
    src = ColumnDataSource(data=dict())

    def make_dataset(device_list, range_start = 0, range_end = 8, bin_width = .5):

        # Check to make sure the start is less than the end!
        assert range_start < range_end, "Start must be less than end"
        
        by_device = pd.DataFrame(columns=['left', 'right', 'count', 'name', 'color'])
        range_extent = range_end - range_start
        
        # Iterate through all the devices
        for i, device_name in enumerate(device_list):

            # Subset to the carrier
            subset = impressions_log_df[impressions_log_df['Device'] == device_name]

            # Create a histogram with specified bins and range
            bucket_vals, edges = np.histogram(subset['LogImp'], 
                                        bins = int(range_extent / bin_width), 
                                        range = [range_start, range_end])

            imp_df = pd.DataFrame({'count': bucket_vals, 'left': edges[:-1], 'right': edges[1:] })
            imp_df['name'] = device_name
            imp_df['color'] = Category20_16[i]

            # Add to the overall dataframe
            by_device = by_device.append(imp_df)

        # Overall dataframe
        by_device = by_device.sort_values(['name', 'left'])
        
        return ColumnDataSource(by_device)

    def update():
        device_list = [device_selection.labels[i] for i in device_selection.active]
        new_src = make_dataset(device_list)
        src.data.update(new_src.data)

    device_selection = CheckboxButtonGroup(labels=available_devices, active=[0,1])
    device_selection.on_change('active', lambda attr, old, new: update())

    src = make_dataset(device_list=['Tablet', 'Mobile'])

    p = figure(title='Histogram: Number of Impressions by Device', tools='',
            x_axis_label = 'Log (Number of Impressions)', y_axis_label = 'Count',
            background_fill_color="#fafafa")
    p.quad(source = src, top='count', bottom=0, left='left', right='right',
            color='color', line_color="white", alpha=0.5, legend='name')
    p.legend.click_policy = 'hide'
    p.title.align='center'; p.title.text_font_size='16pt'

    instructs = Div(text='Use the buttons to select which Devices are included in the Histogram:')

    controls = column(instructs, device_selection)
    #update()
    layout = row(controls, p)
    tab = Panel(child=layout, title='Impressions by Device')
    return tab