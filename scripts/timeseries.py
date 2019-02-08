import math
from bokeh.io import curdoc

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

from bokeh.models.widgets import RangeSlider, Button, DataTable, TableColumn, NumberFormatter
from bokeh.layouts import layout

from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application

from bokeh.layouts import column, row, WidgetBox
from bokeh.models.widgets import CheckboxGroup, CheckboxButtonGroup, Slider, RangeSlider, Tabs, TableColumn, NumberFormatter
from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.io import curdoc
from bokeh.models.widgets import Div

def timeseries_tab(saatva):
    saatva = saatva.sort_values('Day', ascending=True)
    saatva['LogImp'] = (1+saatva['Impressions']).apply(math.log10)
    saatva['LogClicks'] = (1+saatva['Clicks']).apply(math.log10)
    saatva['LogCost'] = (1+saatva['Cost']).apply(math.log10)
    saatva['LogConversions'] = (1+saatva['Conversions']).apply(math.log10)
    saatva['LogConvValue'] = (1+saatva['ConvValue']).apply(math.log10)
    window_size = 10
    by_day = saatva[['Day','Impressions','Clicks','Cost','Conversions','ConvValue',
                        'LogImp','LogClicks','LogCost','LogConversions','LogConvValue']]\
            .groupby('Day', as_index=False).sum()

    available_metrics = ['Impressions', 'Cost ($)', 'Clicks', 'Conv Value ($)', 'Conversions']
    
    def make_dataset(agg_df, days, metric_list):
        numMetrics = len(metric_list)
        slice_start = int(days/2.0)
        slice_end = len(agg_df) - int(days/2.0) - 1

        window = np.ones(days)/float(days)
        imp_avg = np.convolve(by_day['LogImp'].values, window, 'same')[slice_start:slice_end]
        click_avg = np.convolve(by_day['LogClicks'].values, window, 'same')[slice_start:slice_end]
        cost_avg = np.convolve(by_day['LogCost'].values, window, 'same')[slice_start:slice_end]
        conv_avg = np.convolve(by_day['LogConversions'].values, window, 'same')[slice_start:slice_end]
        convval_avg = np.convolve(by_day['LogConvValue'].values, window, 'same')[slice_start:slice_end]
        conv_df = pd.DataFrame({'Impressions':imp_avg, 'Cost ($)': cost_avg, 'Clicks':click_avg
                              ,'Conv Value ($)': convval_avg, 'Conversions':conv_avg})

        src_dict = {'Day':[by_day['Day'].values[slice_start:slice_end]]*numMetrics
                   ,'Names':[]
                   ,'Values':[]

                   ,'Colors':[]}
        for i, metric_name in enumerate(metric_list):
            src_dict['Names'].append(metric_name)
            src_dict['Values'].append(conv_df[metric_name].values)
            src_dict['Colors'].append(Category20_16[i])

        return ColumnDataSource(src_dict)

    src = make_dataset(by_day, window_size, metric_list=['Impressions', 'Cost ($)'])

    def update():
        metric_list = [checkbox.labels[i] for i in checkbox.active]
        new_src = make_dataset(by_day, slider.value, metric_list)
        src.data.update(new_src.data)
    
    # slider widget to control how many days the rolling average is:
    slider = Slider(title="Select Num. Days for Moving Average"
                        ,start = 1, end = 40
                        , value=10, step=1)
    slider.on_change('value', lambda attr, old, new: update())

    checkbox = CheckboxButtonGroup(labels=available_metrics, active=[0,1])
    checkbox.on_change('active', lambda attr, old, new: update())

    p = figure(x_axis_type="datetime", title= 'Moving Average Chart'
              ,plot_width=int(500*1.618), plot_height=500, y_range=(0,3500))
    p.grid.grid_line_alpha = 0
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Log (Metric Value)'
    p.ygrid.band_fill_color = "olive"
    p.ygrid.band_fill_alpha = 0.1

    p.multi_line(source=src, xs='Day', ys='Values', line_color='Colors', legend='Names')

    p.legend.location = "top_left"
    p.title.align='center'; p.title.text_font_size='16pt'

    instructs = Div(text='Use the buttons to select which metrics are included in the chart:')

    controls = column(instructs, checkbox, slider)
    layout = row(controls, p)
    #l = layout([[WidgetBox(checkbox), WidgetBox(slider)],[p]])

    tab = Panel(child=layout, title='Time Series')

    return tab