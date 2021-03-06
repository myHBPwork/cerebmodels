# ../managers/operatorsSignaling/converter.py
import numpy as np
from neo.core import IrregularlySampledSignal as iss
from elephant.spike_train_generation import peak_detection as pd
from quantities import mV

class Converter(object):
    """
    **Available methods:**

    +-------------------------------------------------+--------------------+
    | Method name                                     | Method type        |
    +-------------------------------------------------+--------------------+
    | :py:meth:`.determine_signalsign_from_threshold` | static method      |
    +-------------------------------------------------+--------------------+
    | :py:meth:`.voltage_to_spiketrain`               | class method       |
    +-------------------------------------------------+--------------------+

    *NOTE:*

    * ``determine_signalsign_from_threshold`` returns "+" or "-"
    * ``voltage_to_spiketrain`` returns array of times when spikes occured

    """
    @staticmethod
    def determine_signalsign_from_threshold(thresh):
        """Returns signal sign "+" or "-" given a threshold number value.
        """
        signal_sign = ["above" if ((np.sign(x)==1) or (np.sign(x)==0))
                               else "below"
                               for x in [int(thresh)] ]
        return signal_sign[0]

    @classmethod
    def voltage_to_spiketrain(cls, model, recordings):
        """Transforms voltage recordings into spikes.

        **Arguments:**

        +-----------------------+--------------------+
        | Ordered argument      | Value type         |
        +=======================+====================+
        | 1. model instance     | instantiated model |
        +-----------------------+--------------------+
        | 2. response recording | dictionary         |
        +-----------------------+--------------------+

        *NOTE:*

        * the model has the attribute 'regions'
        * recordings is a product after running the model

        **Use case:**

        First we set up as follows

        ``>> sm = SimulationManager()``

        ``>> rm = RecordManager()``

        ``>> rec = {"time": None, "response": None, "stimulus": None}``

        ``>> par = {"dt": 0.1, "celsius": 30, "tstop": 10, "v_init": 65}``

        ``>> sm.prepare_model_NEURON(parameters=par, chosenmodel=chosenmodel)``

        ``>> rec["time"], rec["response"], rec["stimulus"] = rm.prepare_recording_NEURON(chosenmodel)``

        ``>> sm.engage_NEURON``

        ``>> co = Converter()``

        Then,

        ``>> spikes = co.voltage_to_spiketrain(chosenmodel, rec)``

        """
        spikes = {}
        for cell_region, with_thresh in model.regions.items():
            # convert voltage recordings to an analog signal
            analog = iss( recordings["time"], recordings["response"][cell_region],
                          time_units='ms', units='mV' )
            # determine signal sign from analog signal based on thresh
            analog_sign = cls.determine_signalsign_from_threshold(with_thresh)
            # extract spikes from analog based on signal sign
            spike_train = pd( analog,
                              threshold = np.array(with_thresh)*mV,
                              sign = analog_sign,
                              format = None )
            # record the spike train
            spikes.update( {cell_region: spike_train} )
        return spikes
