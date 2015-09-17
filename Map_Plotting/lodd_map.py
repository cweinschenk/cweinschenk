from __future__ import division
import os
import numpy as np
import pandas as pd
from collections import OrderedDict
from bokeh.sampledata import us_states
from bokeh.plotting import figure, show, output_file,ColumnDataSource
from bokeh.models import HoverTool

us_states = us_states.data.copy()
del us_states["HI"]
del us_states["AK"]

state_xs = [us_states[code]["lons"] for code in us_states]
state_ys = [us_states[code]["lats"] for code in us_states]

data = pd.read_csv('study_data.csv')


output_file("lodd_map.html", title="LODD Map")
TOOLS="pan,box_zoom,wheel_zoom,reset,resize,save,hover"
p = figure(title="NIST LODD/LODI Studies", toolbar_location="left",
    plot_width=1100, plot_height=700,tools=TOOLS)

p.patches(state_xs, state_ys, fill_alpha=0.0,
    line_color="#884444", line_width=2)

for i in range(0,len(data)):
    study_label = data['Study'][i]
    source = ColumnDataSource({'studys': study_label})
    x = data['Longitude'][i]
    y = data['Latitude'][i]

p.circle(x,y,source=source,size=10, color="navy", alpha=0.5)
hover = p.select(dict(type=HoverTool))
hover.tooltips = [('Study Title','@studys')]

show(p)