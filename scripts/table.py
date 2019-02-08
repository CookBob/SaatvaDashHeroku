from bokeh.io import curdoc

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

from bokeh.models.widgets import RangeSlider, Button, DataTable, TableColumn, NumberFormatter

from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable

from bokeh.layouts import column, row, WidgetBox

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.models.widgets import Div

def table_tab(saatva):
    def update():
        sliced_data = saatva[(saatva['Cost'] >= slider.value[0]) & (saatva['Cost'] <= slider.value[1])]
        agg_data = round(sliced_data[['Device','Impressions','Clicks','Cost','Conversions','ConvValue']]\
                                    .groupby(['Device'], as_index=False).mean()\
                        ,2)
        src.data = agg_data.to_dict('list')

    slider = RangeSlider(title="Cost Range", start = min(saatva['Cost']), end = max(saatva['Cost'])
                        ,value=(min(saatva['Cost']), max(saatva['Cost'])), step=50, format="$0,0")
    slider.on_change('value', lambda attr, old, new: update())

    start_data = round(saatva[['Device','Impressions','Clicks','Cost','Conversions','ConvValue']]\
                                .groupby(['Device'], as_index=False).mean()\
                      ,2)
    src = ColumnDataSource(start_data)

    columns = [
        TableColumn(field="Device", title="Device"),
        TableColumn(field="Impressions", title="Impressions"),
        TableColumn(field="Clicks", title="Clicks"),
        TableColumn(field="Cost", title="Cost", formatter=NumberFormatter(format="$0,0.00")),
        TableColumn(field="Conversions", title="Conversions"),
        TableColumn(field="ConvValue", title="ConvValue", formatter=NumberFormatter(format="$0,0.00"))
    ]

    data_table = DataTable(source=src, columns=columns, width=800, index_position=None, selectable=False)
    
    instructs = Div(text='Use the slider to filter which campaign days are included in the table:')

    controls = row(instructs, slider)
    layout = column(controls, data_table)
    tab = Panel(child=layout, title='Devices Summary')

    return tab