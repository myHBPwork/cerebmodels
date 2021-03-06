# Bokeh basics
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

from bokeh.models.widgets import Panel#, Tabs
from bokeh.plotting import figure#, curdoc

import os, sys
#sys.path.append(os.path.dirname(os.getcwd())) # for running it from ~/managers
sys.path.append(os.getcwd()) # for running it from ~/cerebmodels
#print os.getcwd()
#print sys.path
#
from managers.operatorsVisualize.tabModels import TabModels
from managers.operatorsVisualize.tabModelResponses import TabModelResponses


tab1 = TabModels()
tab2 = TabModelResponses()

# Put all the tabs into one application
tabs = Tabs(tabs=[ tab1, tab2 ])

# Put the tabs in the current document for display
curdoc().add_root(tabs)
