import numpy as np
import pandas as pd
from bokeh.browserlib import view
from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.models.glyphs import Circle
from bokeh.plotting import figure, show, output_file
from bokeh.models import (
    GMapPlot, Range1d, ColumnDataSource, LinearAxis,
    PanTool, WheelZoomTool, BoxSelectTool,
    BoxSelectionOverlay, GMapOptions,
    NumeralTickFormatter, PrintfTickFormatter,HoverTool, TapTool, OpenURL,)
from bokeh.resources import INLINE

x_range = Range1d()
y_range = Range1d()

# JSON style string taken from: https://snazzymaps.com/style/1/pale-dawn
map_options = GMapOptions(lat=39, lng=-98, map_type="roadmap", zoom=5, styles="""
[{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"on"},{"lightness":33}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2e5d4"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#c5dac6"}]},{"featureType":"poi.park","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":20}]},{"featureType":"road","elementType":"all","stylers":[{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#c5c6c6"}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#e4d7c6"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#fbfaf7"}]},{"featureType":"water","elementType":"all","stylers":[{"visibility":"on"},{"color":"#acbcc9"}]}]
""")

plot = GMapPlot(
    x_range=x_range, y_range=y_range,
    map_options=map_options,
    title = "NIST LODD Study Map",plot_width=1400, plot_height=1000
)

data = pd.read_csv('study_data.csv')

source = ColumnDataSource({'lat':data['Latitude'],'lon':data['Longitude'],'studys': data['Study'],'report': data['Report']})
circle = Circle(x="lon",y="lat",size=15, fill_color="navy")
plot.add_glyph(source, circle)

pan = PanTool()
wheel_zoom = WheelZoomTool()
hover = HoverTool()
tap = TapTool()
HoverTool.tooltips = [('Study Title','@studys')]
url = "http://dx.doi.org/10.6028/@report"
TapTool.callback = OpenURL(url=url)

plot.add_tools(pan,wheel_zoom,hover,tap)

doc = Document()
doc.add(plot)

if __name__ == "__main__":
    filename = "maps.html"
    with open(filename, "w") as f:
        f.write(file_html(doc, INLINE, "NIST LODD Study Map"))
    print("Wrote %s" % filename)
    view(filename)

