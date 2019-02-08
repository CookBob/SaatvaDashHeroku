# In command line, tell bokeh to run the SaatvaDash directory

import pandas as pd
from os.path import dirname, join
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

from scripts.table import table_tab
from scripts.histogram import histogram_tab
from scripts.timeseries import timeseries_tab
from scripts.scatter import scatter_tab

saatva = pd.read_csv(join(dirname(__file__), 'data','DashboardExercise.csv'))

# Rename conversion value column
saatva = saatva.rename(columns={'Conv. value':'ConvValue'})

# Convert Day column from string to datetime
saatva['Day'] = pd.to_datetime(saatva['Day'])

# convert string-typed columns to floats where applicable:
cols_to_conv = ['Impressions','Clicks','Cost','ConvValue']
for col in cols_to_conv:
    saatva[col] = saatva[col].str.replace(',','').astype(float)

tab1 = scatter_tab(saatva)
tab2 = histogram_tab(saatva)
tab3 = timeseries_tab(saatva)
tab4 = table_tab(saatva)

tabs = Tabs(tabs = [tab1, tab2, tab3, tab4])
curdoc().add_root(tabs)