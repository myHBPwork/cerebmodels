# ~/executive.py
import importlib

from utilities import UsefulUtils as uu
from managers.managerAccount import AccountManager

class ExecutiveControl(object):

    def __init__(self):
        self.am = AccountManager()
        self.modelscale = None
        self.modelname = None

    def list_modelscales(self):
        return self.am.available_modelscales()

    def list_models(self, modelscale=None):
        return self.am.modelscale_inventory(model_scale=modelscale)

    def choose_model(self, modelscale=None, modelname=None):
        modelmodule = importlib.import_module("models."+modelscale+"."+"model"+modelname)
        self.chosenmodel = getattr(modelmodule, uu.classesinmodule(modelmodule)[0].__name__)
        return self.chosenmodel