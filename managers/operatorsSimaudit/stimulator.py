# ~/managers/operatorsSimaudit/stimulator.py
import os
import sys

from neuron import h

# import modules from other directories
# set to ~/cerebmodels
sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))
#
from utilities import UsefulUtils as uu

class Stimulator(object):
    """
    **Available methods:**

    +----------------------------------+------------------+
    | Method name                      | Method type      |
    +==================================+==================+
    | :py:meth:`.inject_IClamp`        | static method    |
    +----------------------------------+------------------+
    | :py:meth:`.inject_IRamp`         | static method    |
    +----------------------------------+------------------+
    | :py:meth:`.inject_GrC_Sine`      | static method    |
    +----------------------------------+------------------+
    | :py:meth:`inject_current_NEURON` | class method     |
    +----------------------------------+------------------+

    *NOTE:*

    * ``inject_IClamp``  returns list_of_currents where each element is ``hoc`` object ``h.IClamp``
    * ``inject_IRamp``  returns list_of_currents where each element is ``hoc`` object ``h.IRamp``
    * ``inject_current_NEURON`` returns stimuli_list where each element is ``hoc`` object ``h.IClamp`` or ``h.IRamp` depending on current type.

    Notice that ``h.IClamp`` is a default object in `NEURON <https://neuron.yale.edu/neuron/>`_ but ``h.IRamp`` and ``h.GrC_Sine`` are custom built objects. The former is built here in ``DummyModel`` of a cell which will get compiled. The later is build in the ``GrC2001Egidio`` model, a sinusoidal current injection for the Granule cell. However, ``h.IRamp`` is for injecting ramping current of the form "/" (up ramp), "\" (down ramp) or a combination ("/\").

    """

    def __init__(self):
        #self.h = neuron_dot_h
        pass

    @staticmethod
    def inject_IClamp(parameters, injectsite):
        """Injects IClamp for `NEURON <https://neuron.yale.edu/neuron/>`_

        **Keyword Arguments:**

        +----------------+--------------------------------------------------------------+
        | Keys           | Value type                                                   |
        +================+==============================================================+
        | ``parameters`` | - list such that each element is a dictionary [ {}, {}, {} ] |
        |                | - Eg: [ {"amp": 0.5, "dur": 100.0, "delay": 10.0},           |
        |                |         {"amp": 1.0, "dur": 50.0, "delay": 10.0+100.0} ]     |
        +----------------+--------------------------------------------------------------+
        | ``injectsite`` | ``neuron`` ``section``, for e.g., ``cell.soma``              |
        +----------------+--------------------------------------------------------------+

        **Returned values:** list of currents where each element is a ``hoc`` object ``h.IClamp``.

        **NOTE:** The ``h.IClamp`` function is available in `NEURON <https://neuron.yale.edu/neuron/>`_ by default. 

        """
        no_of_currents = len(parameters) # number of currents
        list_of_currents = []
        for i in range(no_of_currents):
            list_of_currents.append( h.IClamp(0.5, sec=injectsite) )
            for key, value in parameters[i].items():
                if key in list_of_currents[i].__dict__:
                    setattr(list_of_currents[i], key, value)
                else:
                    raise AttributeError( key + " is not an attribute in h.IClamp." )
        return list_of_currents

    @staticmethod
    def inject_IRamp(parameters, injectsite):
        """Injects ``IRamp`` for `NEURON <https://neuron.yale.edu/neuron/>`_

        **Keyword Arguments:**

        +----------------+--------------------------------------------------------------+
        | Keys           | Value type                                                   |
        +================+==============================================================+
        | ``parameters`` | - list such that each element is a dictionary [ {}, {}, {} ] |
        |                | - Eg: [ {"amp_initial": 0.0, "amp_final": 1.0, "dur": 100.0, |
        |                |                                              "delay": 10.0}, |
        |                |         {"amp_initial"": 1.0, "amp_final": 0.0, "dur": 100.0,|
        |                |                                       "delay": 10.0+100.0} ] |
        +----------------+--------------------------------------------------------------+
        | ``injectsite`` | ``neuron`` ``section``, for e.g., ``cell.soma``              |
        +----------------+--------------------------------------------------------------+

        **Returned values:** list of currents where each element is a ``hoc`` object ``h.IRamp``.

        *NOTE:* The ``h.IRamp`` function is available in ``~/cerebmodels/models/cells/DummyModel/mod_files/CurrentRamp.mod``.

        """
        no_of_currents = len(parameters) # number of currents
        list_of_currents = []
        for i in range(no_of_currents):
            list_of_currents.append( h.IRamp(0.5, sec=injectsite) )
            for key, value in parameters[i].items():
                if key not in list_of_currents[i].__dict__:
                    raise AttributeError( key + " is not an attribute in h.IRamp." )
                else:
                    if key=="amp_final":
                        adjusted_value = value - parameters[i]["amp_initial"]
                        setattr(list_of_currents[i], key, adjusted_value)
                    else:
                        setattr(list_of_currents[i], key, value)
        return list_of_currents

    @staticmethod
    def inject_GrC_Sine(parameters, injecsite):
        """Injects ``GrC_Sine`` for `NEURON <https://neuron.yale.edu/neuron/>`_ 

        **Keyword Arguments:**

        +----------------+--------------------------------------------------------------+
        | Keys           | Value type                                                   |
        +================+==============================================================+
        | ``parameters`` | - list such that each element is a dictionary [ {}, {}, {} ] |
        |                | - Eg: [ {"amp": 0.006, "dur": 800.0, "delay": 100.0,         |
        |                |                                  "freq": 4.0, "phase": 0.0}, |
        |                |         {"amp": 0.006, "dur": 400.0, "delay": 100.0+800.0,   |
        |                |                                 "freq": 8.0, "phase": 0.0} ] |
        +----------------+--------------------------------------------------------------+
        | ``injectsite`` | ``neuron`` ``section``, for e.g., ``cell.soma``              |
        +----------------+--------------------------------------------------------------+

        **Returned values:** list of currents where each element is a ``hoc`` object ``h.GrC_Sine``.

        *NOTE:* This function is available in ``~/cerebmodels/models/cells/GrC2001Dangelo/mod_files/Grc_sine.mod``.

        """
        no_of_sinucurrents = len(parameters)
        list_of_sinucurrents = []
        for i in range(no_of_sinucurrents):
            list_of_sinucurrents.append( h.GrC_Sine(0.5, sec=injecsite) )
            for key, value in parameters[i].iteritems():
                if key in list_of_sinucurrents[i].__dict__:
                    setattr(list_of_sinucurrents[i], key, value)
                else:
                    raise AttributeError( key + " is not an attribute in h.GrC_Sine" )
        return list_of_sinucurrents

    def inject_current_NEURON(self, currenttype=None, injparameters=None, neuronsection=None):
        """Sets current injection parameters to either ``h.IClamp``, ``h.IRamp``, ``GrC_Sine``

        **Keyword Arguments:**

        +-------------------+--------------------------------------------------------------+
        | Keys              | Value type                                                   |
        +===================+==============================================================+
        | ``currenttype``   | string; ``"IClamp"``, ``"IRamp"``, or ``"GrC_Sine"``.        |
        +-------------------+--------------------------------------------------------------+
        | ``injparameters`` | - list such that each element is a dictionary [ {}, {}, {} ] |
        |                   | - for ``IClamp`` see :py:meth:`.inject_IClamp`.              |
        |                   | - for ``IRamp`` see :py:meth:`.inject_IRamp`.                |
        |                   | - for ``GrC_Sine`` see :py:meth:`.inject_GrC_Sine`.          |
        +-------------------+--------------------------------------------------------------+
        | ``neuronsection`` | ``neuron`` ``section``, for e.g., ``cell.soma``              |
        +-------------------+--------------------------------------------------------------+

        **Returned values:**Stimuli list where each element is ``hoc`` object ``h.IClamp``, ``h.IRamp`` or ``h.GrC_Sine``, depending on the given ``currenttype`` parameter.

        *NOTE:*

        * depending on the currenttype choice :py:meth:`.inject_IClamp`, :py:meth:`.inject_IRamp` or :py:meth:`.inject_GrC_Sine` is called
        * ``h.IClamp`` is available in NEURON by default
        * ``h.IRamp`` is custom available in ``~/cerebmodels/models/cells/DummyModel/mod_files/CurrentRamp.mod``
        * ``h.GrC_Sine`` is custom available in ``~/cerebmodels/models/cells/GrC2001DAngela/mod_files/Grc_sine.mod``
           
        """

        if currenttype is None or injparameters is None or neuronsection is None:
            raise ValueError("currenttype must be either 'IClamp' or 'IRamp'. injparameters must be a list such that its elements are dictionaries [ {}, {}, ... ]. neuronsection must be for eg cell.soma where cell = CellTemplate().")
        else:
            if currenttype is "IClamp" or \
               currenttype is "IRamp" or \
               currenttype is "GrC_Sine":
                desiredfunc = self.__getattribute__( "inject_"+currenttype )
                stimuli_list = desiredfunc( injparameters, neuronsection )
            else:
                raise ValueError("currenttype must be 'IClamp', 'IRamp','GrC_Sine'")
        return stimuli_list
