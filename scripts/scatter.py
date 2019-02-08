from bokeh.io import curdoc
import math
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

from bokeh.plotting import figure, output_file, show
from bokeh.models.widgets import Div

def scatter_tab(saatva):
    campaign_df = saatva[['Campaign','Impressions','Clicks','Cost','Conversions','ConvValue']]\
                 .groupby('Campaign', as_index=False).sum()
    campaign_df['Days'] = saatva.groupby('Campaign', as_index=False).count()[['Campaign','Day']]\
                                .rename(columns={'Day':'Days'})['Days']
    campaign_df['LogImp'] = (1+campaign_df['Impressions']).apply(math.log10)
    campaign_df['LogClicks'] = (1+campaign_df['Clicks']).apply(math.log10)
    campaign_df['LogCost'] = (1+campaign_df['Cost']).apply(math.log10)
    campaign_df['LogConversions'] = (1+campaign_df['Conversions']).apply(math.log10)
    campaign_df['LogConvValue'] = (1+campaign_df['ConvValue']).apply(math.log10)
    campaign_df['adjDays'] = campaign_df['Days']/40.0

    def update():
        sliced_df = campaign_df[
            (campaign_df['Days']>=slider_days.value[0]) & (campaign_df['Days']<=slider_days.value[1]) \
            & (campaign_df['Cost']>=slider_cost.value[0]) & (campaign_df['Cost']<=slider_cost.value[1]) \
            & (campaign_df['ConvValue']>=slider_convvalue.value[0]) & (campaign_df['ConvValue']<=slider_convvalue.value[1])]
        src.data = sliced_df.to_dict('list')
    
    # Days slider:
    slider_days = RangeSlider(title="Total Campaign Days", start = min(campaign_df['Days']), end = max(campaign_df['Days'])
                             ,value=(min(campaign_df['Days']), max(campaign_df['Days'])), step=1)
    slider_days.on_change('value', lambda attr, old, new: update())

    # Cost slider:
    slider_cost = RangeSlider(title="Total Campaign Cost", start = min(campaign_df['Cost']), end = max(campaign_df['Cost'])
                             ,value=(min(campaign_df['Cost']), max(campaign_df['Cost'])), step=1, format="$0,0")
    slider_cost.on_change('value', lambda attr, old, new: update())

    # Conversion Value slider:
    slider_convvalue = RangeSlider(title="Total Campaign Conv. Value", start = min(campaign_df['ConvValue']), end = max(campaign_df['ConvValue'])
                             ,value=(min(campaign_df['ConvValue']), max(campaign_df['ConvValue'])), step=1, format="$0,0")
    slider_convvalue.on_change('value', lambda attr, old, new: update()) 

    src = ColumnDataSource(campaign_df)

    hover = HoverTool(tooltips=[
        ('Campaign', '@Campaign'),
        ('Total Cost', '@Cost{$0,0}'),
        ('Total Conv. Value', '@ConvValue{$0,0}'),
        ('Total Days', '@Days')
    ])
    p = figure(tools=[hover], plot_width=int(500*1.618), plot_height=500
              ,x_axis_label='Log (Total Cost)', y_axis_label = 'Log (Total Conversion Value)'
              ,x_range=(-0.2,6.2), y_range=(-0.2,6.8), title='Campaign Conversion Value vs. Cost')
    p.title.align='center'; p.title.text_font_size='16pt'

    # add a circle renderer with a size, color, and alpha
    p.circle(source=src, x='LogCost',y='LogConvValue'
            ,size='adjDays', color="navy",alpha=0.5)
    
    instructs1 = Div(text = 'Use the sliders to choose which campaigns are included in the scatterplot:')
    instructs2 = Div(text = '<br><br><br>  <b>Hover over a bubble to view details about that campaign.</b>')
    
    controls = column(instructs1, slider_days, slider_cost, slider_convvalue, instructs2)
    layout = row(controls, p)
    tab = Panel(child=layout, title='Campaign Effectiveness')

    return tab