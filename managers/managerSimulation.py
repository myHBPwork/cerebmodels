# ../managers/managerSimulation.py
import os
import time

from managers.operatorsSimaudit.inspector import SimInspector
from managers.operatorsSimaudit.hardware import HardwareConfigurator
from managers.operatorsSimaudit.assembler import SimAssembler
from managers.operatorsSimaudit.stimulator import Stimulator

from neuron import h

class SimulationManager(object):
    """Manager working under ExecutiveControl.

    Available methods:
    prepare_model_NEURON
    stimulate_model_NEURON
    trigger_NEURON

    """

    def __init__(self):
        self.si = SimInspector()
        self.hc = HardwareConfigurator()
        self.sa = SimAssembler()
        self.st = Stimulator()

    def prepare_model_NEURON(self, parameters, chosenmodel, modelcapability = None,
                      cerebunitcapability = None):
        """method that checks for compiled nmodl and optionally for capability.

        Argument (mandatory):
        instantiated NEURON based model
        parameters -- dictionary with keys: dt, celsius, tstop, v_init

        Keyword arguments (optional):
        modelcapability -- string; eg "produces_spike_train"
        cerebunitcapability -- imported class, for eg., ProducesSpikeTrain

        Returned value:
        nothing is returned

        NOTE:
            - although not manadatory it is recommended to use the keyword arguments
            - also modelcapability and cerebunitcapability is recommended especially
              if you want to use CerebUnit

        Use case:
        modelmodule = importlib.import_module("models.cells.modelPC2015Masoli")
        pickedmodel = getattr(modelmodule, uu.classesinmodule(modelmodule)[0].__name__)
        chosenmodel = pickedmodel()
        parameters = {"dt": 0.01, "celsius": 30, "tstop": 100, "v_init": 65}
        sm = SimulationManager()
        sm.prepare_model_NEURON(parameters, chosenmodel)

        """

        self.si.lock_and_load_nmodl(modelscale = chosenmodel.modelscale,
                                    modelname = chosenmodel.modelname)
        self.si.check_compatibility(capability_name = modelcapability,
                                    CerebUnit_capability = cerebunitcapability)
        self.hc.activate_cores()
        self.sa.set_runtime_NEURON(parameters = parameters)
        return "NEURON model is ready" # for managerSimulationTest.py

    def stimulate_model_NEURON(self, stimparameters=None, modelsite=None):
        """method that stimulates the prepared model but before locking & loading the capability or before engaging the simulator.

        Keyword Arguments (optional):
        stimparameters -- dictionary with keys "type" and "stimlist" where
                          "type": 2 element list of strings
                                  <stimulus category> <specific type of that category>
                                  NOTE: First element is ALWAYS <stimulus category>
                          Eg: for current inject on cellular model
                              ["current", "IClamp"]
                          "stimlist": is a list with elements as dictionary; like [ {}, {}, ... ]
                          Eg: [ {"amp": 0.5, "dur": 100.0, "delay": 10.0},
                                {"amp": 1.0, "dur": 50.0, "delay": 10.0+100.0} ]
                          Eg: [ {"amp_initial": 0.0, "amp_final": 0.5, "dur": 5.0, "delay": 5.0},
                                {"amp_initial": 0.5, "amp_final": 1.0, "dur": 5.0, "delay": 10.0},
                                {"amp_initial": 1.0, "amp_final": 0.5, "dur": 5.0, "delay": 15.0},
                                {"amp_initial": 0.5, "amp_final": 0.0, "dur": 5.0, "delay": 20.0},

        modelsite -- section of the instantiated NEURON based model where you want to stimulate. For eg. chosenmodel.cell.soma

        Returned value:
        if stimparameters are given
        stimuli_list -- each element is hoc object
                        For current inject it is h.IClamp or h.IRamp depending on currenttype.
        if no argument is given
        string -- "Model is not stimulated"

        NOTE:
            - even if the stimulation does not involve stimulation it is recommended to evoke this function
            - in such case just evoke stimulate_model_NEURON without arguments
            - the returned value will be "Model is not stimulated"

        Use case:
        modelmodule = importlib.import_module("models.cells.modelPC2015Masoli")
        pickedmodel = getattr(modelmodule, uu.classesinmodule(modelmodule)[0].__name__)
        chosenmodel = pickedmodel()
        runparameters = {"dt": 0.01, "celsius": 30, "tstop": 100, "v_init": 65}
        currparameters = {"type": ["current", "IClamp"],
                          "stimlist": [ {"amp": 0.5, "dur": 100.0, "delay": 10.0},
                                        {"amp": 1.0, "dur": 50.0, "delay": 10.0+100.0} ]}
        sm = SimulationManager()
        sm.prepare_model_NEURON(runparameters, chosenmodel)
        sm.stimulate_model_NEURON(stimparameters = currparamters,
                                  modelsite=chosenmodel.cell.soma)

        """
        if stimparameters is None or modelsite is None:
            return "Model is not stimulated"
        elif ( "type" not in stimparameters or
             "stimlist" not in stimparameters or
             len(stimparameters["type"]) != 2 ):
            raise ValueError("stimparameters should be a dictionary with " 
                             "keys 'type' and 'stimlist' where" 
                             "'type': 2 element list of strings"
                                     "<stimulus category> <specific type of that category>" 
                                     "Eg: for current inject on cellular model" 
                                         "['current', 'IClamp']" 
                             "'stimlist': is a list with elements as dictionary"
                             "Eg: [ {'amp': 0.5, 'dur': 100.0, 'delay': 10.0}," 
                                   "{'amp': 1.0, 'dur': 50.0, 'delay': 10.0+100.0} ]")
        else:
            if stimparameters["type"][0] is "current":
                stimuli_list = self.st.inject_current_NEURON(
                                           currenttype = stimparameters["type"][1],
                                           injparameters = stimparameters["stimlist"],
                                           neuronsection = modelsite) 
                return stimuli_list

    @staticmethod
    def lock_and_load_capability(chosenmodel, modelcapability):
        """static method loads model capability hence running the simulation

        Argument (mandatory):
        instantiated model

        Keyword arguments (mandatory):
        modelcapability -- string; eg "produces_spike_train"

        Returned value:
        nothing is returned

        Use case:
        modelmodule = importlib.import_module("models.cells.modelPC2015Masoli")
        pickedmodel = getattr(modelmodule, uu.classesinmodule(modelmodule)[0].__name__)
        chosenmodel = pickedmodel()
        sm = SimulationManager()
        sm.lock_and_load_capability(chosenmodel, modelcapability="produce_spike_train")

        """
        run_model = getattr(chosenmodel, modelcapability)
        return run_model()

    @staticmethod
    def engage_NEURON():
        """static method for running a NEURON based model WITHOUT implementing capability

        """
        h.finitialize()
        h.run()
        #print(str(h.dt) + " " + str(h.tstop))

    @classmethod
    def trigger_NEURON(cls, chosenmodel, modelcapability=None):
        """f
        """
        if modelcapability is not None:
            start_time = time.clock()
            cls.lock_and_load_capability( chosenmodel,
                                          modelcapability = modelcapability )
        else:
            start_time = time.clock()
            cls.engage_NEURON()
        print("--- %s seconds ---" % (time.clock() - start_time))
        return "model was successfully triggered via NEURON" # for managerSimulationTest.py
