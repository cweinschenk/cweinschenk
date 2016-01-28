# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import numpy as np
import pandas as pd
from bokeh.util.browser import view
from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.models.glyphs import Circle
from bokeh.plotting import figure, show, output_file
from bokeh.models import (
    GMapPlot, Range1d, ColumnDataSource, LinearAxis,
    PanTool, WheelZoomTool, BoxSelectTool,HoverTool, TapTool, OpenURL)
from bokeh.resources import INLINE
from bokeh.sampledata import us_states

us_states = us_states.data.copy()
del us_states["HI"]
del us_states["AK"]

state_xs = [us_states[code]["lons"] for code in us_states]
state_ys = [us_states[code]["lats"] for code in us_states]

data = pd.read_csv('study_data.csv')

output_file("lodd_map.html", title="LODD Map")
TOOLS="pan,box_zoom,wheel_zoom,reset,resize,save,hover,tap"
plot = figure(title="NIST LODD/LODI Studies", toolbar_location="left",
    plot_width=1100, plot_height=700,tools=TOOLS)

p1 = plot.patches(state_xs, state_ys, fill_alpha=0.0,
    line_color="#884444", line_width=2)

source = ColumnDataSource({'lat':data['Latitude'],'lon':data['Longitude'],'studys': data['Study'],'report': data['Report'],'fill':data['Color'],'type':data['Type'],'date':data['Date']})
circle = Circle(x="lon",y="lat",size=15,fill_color="fill")
plot.add_glyph(source, circle)

pan = PanTool()
wheel_zoom = WheelZoomTool()
hover = HoverTool()
tap = TapTool()
hover.tooltips = [('Study Title','@studys'),('Date','@date'),('Type','@type')]
TapTool.callback = OpenURL(url="@report")

show(plot)