# ~/managers/operatorsTranscribe/metadata_timeseriesgenerator.py
#import numpy.core.defchararray as npd
import re

from managers.operatorsYield.regionparser import RegionParser as rp

class TimeseriesGenerator(object):
    """
    **Available Methods:**

    +--------------------------------------------------+-------------------------+
    | Method name                                      | Method type             |
    +==================================================+=========================+
    | :py:meth:`.forcellrecording`                     | class method            |
    +--------------------------------------------------+-------------------------+
    | :py:meth:`.forrecording`                         | class method            |
    +--------------------------------------------------+-------------------------+
    | :py:meth:`.cellrecordings_response_regionbodies` | static method           |
    +--------------------------------------------------+-------------------------+
    | :py:meth:`.cellrecordings_response_components`   | static method           |
    +--------------------------------------------------+-------------------------+
    | :py:meth:`.recordings_cell_stimulus`             | static method           |
    +--------------------------------------------------+-------------------------+

    """
    @staticmethod
    def cellrecordings_response_regionbodies( model, recordings, stimtype, parameters):
        """Creates a generic time-series (response) metadata for cells. This method is called by :py:meth:`.forcellrecordings_nostimulus` and :py:meth:`.forcellrecordings_stimulus`.

        **Arguments:**

        +---------------+--------------------------------------------------------------+
        | Arguments     | Value type                                                   |
        +===============+==============================================================+
        | first         | instantiated model                                           |
        +---------------+--------------------------------------------------------------+
        | second        | string for cellregion; "soma", "axon", etc ...               |
        +---------------+--------------------------------------------------------------+
        | third         | array; eg: recordings["time"] = rec_t                        |
        +---------------+--------------------------------------------------------------+
        | fourth        | array; eg: recordings["response"][cellregion] = rec_response |
        +---------------+--------------------------------------------------------------+
        | fifth         | - string "not stimulated" or                                 |
        |               | - array; eg: recordings["stimulus"] = rec_stim               |
        +---------------+--------------------------------------------------------------+
        | sixth         | - None or string; eg: stimparameters["type"]                 |
        |               | - stimparameters["type"] = ["current", "IClamp"]             |
        |               | - stimparameters["type"] = ["voltage", "SEClamp"]            |
        +---------------+--------------------------------------------------------------+
        | seventh       | - dictionary for runtime parameters                          |
        |               | - keys: ``"dt"``, ``"celsius"``, ``"tstop"``, ``"v_init"``   |
        +---------------+--------------------------------------------------------------+

        **Returned value:** Is is a dictionary of the form

        ::

           { "name":         string,
             "data":         array,
             "unit":         string,
             "resolution":   float,
             "conversion":   float,
             "timestamps":   array,
             "comments":      string,
             "description":  string }

        *NOTE:*

        * ``recordings["stimulus"] = ``"Model is not stimulated"`` ``!= specific_rec_stim``
        * but ``recordings["stimulus"]`` = ``array`` = ``specific_rec_stim``

        """
        response_type = lambda unit: "voltage" if unit=="mV" else "current"
        comments = lambda unit, stimulus,  stimtype: \
                     response_type(unit) +" response without stimulation" \
                     if ( (type(stimulus) is str) and
                          (stimulus=="Model is not stimulated") ) \
                     else response_type(unit) +" response with "+ stimtype[1]
        description = lambda unit, region_name, model: \
                     "whole single array of "+ response_type(unit) + " response from " + region_name + " of " + model.modelname
        #
        resolution = float( parameters["dt"] )
        conversion = 1000.0
        timestamps = recordings["time"]
        #
        regionlist = rp.get_regionlist(model)
        #
        regions_md_dict = {}
        #
        for a_region_name in regionlist:
            no_of_rec = len(model.regions[a_region_name])
            md_list = []
            for i in range(no_of_rec):
                rec_of = model.regions[a_region_name][i]
                unit = model.recordingunits[rec_of]
                md_list.append(
                   {"name": model.modelname+"_"+a_region_name+"_"+rec_of,
                    "data": recordings["response"][a_region_name][i],
                    "unit": unit,        "resolution": resolution,
              "conversion": conversion,  "timestamps": timestamps,
                #"rate": 1/parameters["dt"], # NWB suggests using Hz but frequency != rate
                "comments": comments(unit, recordings["stimulus"],  stimtype),
             "description": description(unit, a_region_name, model) } )
            regions_md_dict.update( {a_region_name: md_list} )
        return regions_md_dict

    @staticmethod
    def cellrecordings_response_components( model, recordings, stimtype, parameters):
        response_type = lambda unit: "voltage" if unit=="mV" else "current"
        comments = lambda unit, stimulus,  stimtype: \
                     response_type(unit) +" response without stimulation" \
                     if ( (type(stimulus) is str) and
                          (stimulus=="Model is not stimulated") ) \
                     else response_type(unit) +" response with "+ stimtype[1]
        description = lambda unit, compgroup_name, region_name, comp_name, model: \
                     "whole single array of "+ response_type(unit) + " response from the " + compgroup_name + ", " + comp_name + " of the "+ region_name + " of " + model.modelname
        #
        resolution = float( parameters["dt"] )
        conversion = 1000.0
        timestamps = recordings["time"]
        #
        componentgrouplist = rp.get_componentgrouplist(model)
        #
        components_md_dict = {}
        #
        for compgroup_name in componentgrouplist:
            its_regionlist = rp.get_regionlist_of_componentgroup(model, compgroup_name)
            ans2 = {}
            for a_region_name in its_regionlist:
                complist = rp.get_componentlist(model, compgroup_name, a_region_name)
                ans1 = {}
                for a_comp_name in complist:
                    no_of_rec = \
                        len(model.regions[compgroup_name][a_region_name][a_comp_name])
                    md_list = []
                    for i in range(no_of_rec):
                        rec_of = model.regions[compgroup_name][a_region_name][a_comp_name][i]
                        unit = model.recordingunits[rec_of]
                        md_list.append(
                          {"name": model.modelname+"_"+a_region_name+"_" \
                                                      +a_comp_name+"_"+rec_of,
                           "data": recordings["response"][compgroup_name]\
                                             [a_region_name][a_comp_name][i],
                           "unit": unit,        "resolution": resolution,
                     "conversion": conversion,  "timestamps": timestamps,
                #"rate": 1/parameters["dt"], # NWB suggests using Hz but frequency != rate
                       "comments": comments(unit, recordings["stimulus"],  stimtype),
                    "description": description(unit, compgroup_name, a_region_name,
                                               a_comp_name, model) } )
                    ans1.update( {a_comp_name: md_list} )
                ans2.update( {a_region_name: ans1} )
            components_md_dict.update( {compgroup_name: ans2} )
        return components_md_dict

    @staticmethod
    def recordings_cell_stimulus(model, recordings, parameters, stimparameters):
        """Creates a time-series (response) metadata for stimulated cells. This method is called by :py:meth`.recordings_cellstimulus`.

        **Arguments:**

        +-------------+------------------------------------------------------------------+
        | Argument    | Value type                                                       |
        +=============+==================================================================+
        | first       | instantiated model                                               |
        +-------------+------------------------------------------------------------------+
        | second      | array; eg: recordings["time"] = rec_t                            |
        +-------------+------------------------------------------------------------------+
        | third       | array; eg: recordings["stimulus"] = rec_stim                     |
        +-------------+------------------------------------------------------------------+
        | fourth      | - dictionary for runtime parameters                              |
        |             | - keys ``"dt"``, ``"celsius"``, ``"tstop"``, ``"v_init"``        |
        +-------------+------------------------------------------------------------------+
        | fifth       | - dictionary for stimulation parameters                          |
        |             | - keys ``"type"``, ``"stimlist"`` and ``"tstop"``                |
        |             | - value for ``"type"`` is a two element list of strings of       |
        |             |the form <stimulus category> <specific type of that category>     |
        |             | - the first element is ALWAYS ``<stimulus category>``            |
        |             | -  Eg: current inject on a cell ``["current", "IClamp"]``        |
        |             | - value for ``"stimlist"`` is a list with elements as dictionary |
        |             |of the form [ {}, {}, ... ]                                       |
        |             | - Eg1: [ {"amp": 0.5, "dur": 100.0, "delay": 10.0},              |
        |             |          {"amp": 1.0, "dur": 50.0, "delay": 10.0+100.0} ]        |
        |             | - Eg2: [ {"amp_initial": 0.0, "amp_final": 0.5, "dur": 5.0,      |
        |             |                                                 "delay": 5.0},   |
        |             |          {"amp_initial": 0.5, "amp_final": 1.0, "dur": 5.0,      |
        |             |                                                 "delay": 10.0},  |
        |             |          {"amp_initial": 1.0, "amp_final": 0.5, "dur": 5.0,      |
        |             |                                                 "delay": 15.0},  |
        |             |          {"amp_initial": 0.5, "amp_final": 0.0, "dur": 5.0,      |
        |             |                                                 "delay": 20.0} ] |
        |             | - value for ``"tstop"`` is a number, time for generating the last|
        |             |epoch. Therefore, ``"tstop": parameters["tstop"]``.               |
        +-------------+------------------------------------------------------------------+

        **Returned value:** Is is a dictionary of the form

        ::

           { "name":         string,
             "data":         array,
             "unit":         string,
             "resolution":   float,
             "conversion":   float,
             "timestamps":   array,
             "comments":      string,
             "description":  string }

        *NOTE:*

        * prior to calling this method weed out recordings["stimulus"]="Model is not stimulated"
        * this method only accepts arrays

        """
        unit = lambda stimtype: "nA" if stimtype=="current" else "mV" 
        return {"name": model.modelname+"_stimulus",
                #"source": stimparameters["type"][1], # No longer used in NWB2.0
                "data": recordings["stimulus"], "unit": unit(stimparameters["type"][0]),
                "resolution": float(parameters["dt"]), "conversion": 1000.0, #1000=>1ms
                "timestamps": recordings["time"], #"starting_time": 0.0,
                #"rate": 1/parameters["dt"], # NWB suggests using Hz but frequency != rate
                "comments": stimparameters["type"][0] +" injection, "+stimparameters["type"][1],
                "description": "whole single array of stimulus"}

    @classmethod
    def forcellrecording( cls, chosenmodel=None, recordings=None,
                          runtimeparameters=None, stimparameters=None ):
        """Creates the `NWB <https://www.nwb.org/>`_ formatted time-series metadata for cells. This is normally not called by the :ref:`TranscribeManager`, instead it is called by :py:meth:`.forrecording`.

        **Keyword Arguments:**

        +---------------------+----------------------------------------------------------------+
        | Key                 | Value type                                                     |
        +=====================+================================================================+
        |``chosenmodel``      | instantiated model                                             |
        +---------------------+----------------------------------------------------------------+
        |``recordings``       | - dictionary with keys: ``"time"``, ``"response"`` and         |
        |                     |                                             ``"stimulus"``     |
        |                     | - Eg: {"time": array, "response": {cellregion_a: array,        |
        |                     |                                      cellregion_b: array},     |
        |                     |       "stimulus": str("Model is not stimulated") or array}     |
        +---------------------+----------------------------------------------------------------+
        |``runtimeparameters``| - dictionary with keys ``"dt"``, ``"celsius"``, ``"tstop"`` and|
        |                     |                                                   ``"v_init"`` |
        |                     | - - Eg: {"dt": 0.01, "celsius": 30, "tstop": 100, "v_init": 65}|
        +---------------------+----------------------------------------------------------------+
        |``stimparameters``   | - dictionary with keys ``"type"``, ``"stimlist"`` and          |
        |                     |                                                ``"tstop"``     |
        |                     | - value for ``"type"`` is a two element list of strings of     |
        |                     |the form <stimulus category> <specific type of that category>   |
        |                     | - the first element is ALWAYS ``<stimulus category>``          |
        |                     | -  Eg: current inject on a cell ``["current", "IClamp"]``      |
        |                     | - value for ``"stimlist"`` is list with elements as dictionary |
        |                     |of the form [ {}, {}, ... ]                                     |
        |                     | - Eg1: [ {"amp": 0.5, "dur": 100.0, "delay": 10.0},            |
        |                     |          {"amp": 1.0, "dur": 50.0, "delay": 10.0+100.0} ]      |
        |                     | - Eg2: [ {"amp_initial": 0.0, "amp_final": 0.5, "dur": 5.0,    |
        |                     |                                                 "delay": 5.0}, |
        |                     |          {"amp_initial": 0.5, "amp_final": 1.0, "dur": 5.0,    |
        |                     |                                                 "delay": 10.0},|
        |                     |          {"amp_initial": 1.0, "amp_final": 0.5, "dur": 5.0,    |
        |                     |                                                 "delay": 15.0},|
        |                     |          {"amp_initial": 0.5, "amp_final": 0.0, "dur": 5.0,    |
        |                     |                                                 "delay": 20.0}]|
        |                     | - value for ``"tstop"`` is a number, time for generating the   |
        |                     |last epoch. Therefore, ``"tstop": parameters["tstop"]``.        |
        +---------------------+----------------------------------------------------------------+

        **Returned value:** Dictionary whose elements themselves are dictionaries. If there was not stimulus the length of the root dictionary is qual tot he number of cell regions, say, a soma and a dendrite. Their key values are themselves dictionaries, see :py:meth:`.cellrecordings_response`. On the other hand if there was a stimulus the length of the root dictionary is equal to 1 + the number of cell regions, say, a soma and an axon. Their key values are also dictionaries, see :py:meth:`.cellrecordings_response`.

        **Use case:**

        ``>> tg = TimeseriesGenerator()``

        Get the model

        ``>> from models.cells.modelDummyTest import DummyCell``

        ``>> model = DummyCell()``

        ``>> runtimeparam = {"dt": 0.01, "celsius": 30, "tstop": 100, "v_init": 65}``

        Generate model response

        ``>> rec_t = [ t*runtimeparam["dt"] for t in range( int( runtimeparam["tstop"]/runtimeparam["dt"] ) ) ]``

        ``>> rec_i = numpy.random.rand(1,len(rec_t))[0] # stimulus``

        ``>> rec_v = numpy.random.rand(2,len(rec_t))    # response``

        This model has, ``model.regions = {'soma':0.0, 'axon':0.0}``

        For simulation without stimulation

        ``>> recordings = {"time": rec_t, "response": {"soma": rec_v[0], "axon": rec_v[1]}, "stimulus": "Model is not stimulated"}``

        ``>> respmd = tg.forcellrecording(chosenmodel = model, recordings = recordings, parameters = runtimeparam)``

        For simulation with stimulation

        ``>> stimparameters = {"type": ["current", "IClamp"], "stimlist": [ {"amp": 0.5, "dur": 100.0, "delay": 10.0}, {"amp": 1.0, "dur": 50.0, "delay": 10.0+100.0} ], "tstop": parameters["tstop"]}``

        ``>> recordings = {"time": rec_t, "response": {"soma": rec_v[0], "axon": rec_v[1]}, "stimulus": rec_i}``

        ``>> respmd = tg.forcellrecording(chosenmodel = model, recordings = recordings, parameters = runtimeparam, stimparameters = stimparameters)``

        *NOTE:*

        * if there is NO stimulation and ``chosenmodel.regions={"soma": 0.0, "axon": 0.0}` then ``len(respmd) = 2`` since there are two cell regions
        * also, this means ``respmd_soma = respmd["soma"]`` and ``respmd_axon = respmd["axon"]``
        * however, with stimulation there is an additional "stimulus" key ``stimulmd = respmmd["stimulus"]``

        """
        #y = {}
        #update_y = \
        #  lambda y, chosenmodel, recordings, stimtype, runtimeparameters: \
        #     [ y.update( {region: cls.cellrecordings_response( chosenmodel, region,
        #                               recordings, stimtype, runtimeparameters)})
        #       for region in recordings["regions"] ]
        #
        #if npd.equal(recordings["stimulus"], "Model is not stimulated").item((0)):
        # str because recordings has numpy array as dictionary values resulting in
        # numpy FutureWarning bug as it expects this to be an array as well
        # https://stackoverflow.com/questions/40659212/futurewarning-elementwise-comparison-failed-returning-scalar-but-in-the-futur
        if str(recordings["stimulus"])=="Model is not stimulated":
            #y.update( cls.forcellrecordings_nostimulus( chosenmodel, recordings,
            #                                            runtimeparameters ) )
            stimtype = stimparameters # None
            #update_y( y, chosenmodel, recordings, stimtype, runtimeparameters )
            recordings_md = {} 
        else: # for stimulus
            stimtype = stimparameters["type"]
            #update_y( y, chosenmodel, recordings, stimtype, runtimeparameters )
            recordings_md = { "stimulus":
                              cls.recordings_cell_stimulus( chosenmodel, recordings,
                                                runtimeparameters, stimparameters) }
        recordings_md.update( cls.cellrecordings_response_regionbodies( chosenmodel,
                                      recordings, stimtype, runtimeparameters ) )
        recordings_md.update( cls.cellrecordings_response_components( chosenmodel,
                                      recordings, stimtype, runtimeparameters ) )
        return recordings_md

    @classmethod
    def forrecording( cls, chosenmodel=None, recordings=None,
                      runtimeparameters=None, stimparameters=None ):
        """Creates the `NWB <https://www.nwb.org/>`_ formatted time-series metadata.

        **Keyword Arguments:**

        +---------------------+----------------------------------------------------------------+
        | Key                 | Value type                                                     |
        +=====================+================================================================+
        |``chosenmodel``      | instantiated model                                             |
        +---------------------+----------------------------------------------------------------+
        |``recordings``       | - dictionary with keys: ``"time"``, ``"response"`` and         |
        |                     |                                             ``"stimulus"``     |
        |                     | - Eg: {"time": array, "response": {cellregion_a: array,        |
        |                     |                                      cellregion_b: array},     |
        |                     |       "stimulus": str("Model is not stimulated") or array}     |
        +---------------------+----------------------------------------------------------------+
        |``runtimeparameters``| - dictionary with keys ``"dt"``, ``"celsius"``, ``"tstop"`` and|
        |                     |                                                   ``"v_init"`` |
        |                     | - Eg: {"dt": 0.01, "celsius": 30, "tstop": 100, "v_init": 65}  |
        +---------------------+----------------------------------------------------------------+
        |    (optional)       | - dictionary with keys ``"type"``, ``"stimlist"`` and          |
        |``stimparameters``   |                                                ``"tstop"``     |
        |                     | - value for ``"type"`` is a two element list of strings of     |
        |                     |the form <stimulus category> <specific type of that category>   |
        |                     | - the first element is ALWAYS ``<stimulus category>``          |
        |                     | -  Eg: current inject on a cell ``["current", "IClamp"]``      |
        |                     | - value for ``"stimlist"`` is list with elements as dictionary |
        |                     |of the form [ {}, {}, ... ]                                     |
        |                     | - Eg1: [ {"amp": 0.5, "dur": 100.0, "delay": 10.0},            |
        |                     |          {"amp": 1.0, "dur": 50.0, "delay": 10.0+100.0} ]      |
        |                     | - Eg2: [ {"amp_initial": 0.0, "amp_final": 0.5, "dur": 5.0,    |
        |                     |                                                 "delay": 5.0}, |
        |                     |          {"amp_initial": 0.5, "amp_final": 1.0, "dur": 5.0,    |
        |                     |                                                 "delay": 10.0},|
        |                     |          {"amp_initial": 1.0, "amp_final": 0.5, "dur": 5.0,    |
        |                     |                                                 "delay": 15.0},|
        |                     |          {"amp_initial": 0.5, "amp_final": 0.0, "dur": 5.0,    |
        |                     |                                                 "delay": 20.0}]|
        |                     | - value for ``"tstop"`` is a number, time for generating the   |
        |                     |last epoch. Therefore, ``"tstop": parameters["tstop"]``.        |
        +---------------------+----------------------------------------------------------------+

        **Returned value:** Dictionary whose elements themselves are dictionaries. If there was not stimulus the length of the root dictionary is qual tot he number of cell regions, say, a soma and a dendrite. On the other hand if there was a stimulus the length of the root dictionary is equal to 1 + the number of cell regions, say, a soma and an axon. The key values are themselves dictionaries, see :py:meth:`.forcellrecording`.

        **Use case:** For ``modelscale="cells"``

        ``>> tg = TimeseriesGenerator()``

        Get dummy model

        ``>> from models.cells.modelDummyTest import DummyCell``

        ``>> model = DummyCell()``

        ``>> runtimeparam = {"dt": 0.01, "celsius": 30, "tstop": 100, "v_init": 65}``

        Generate model response

        ``>> rec_t = [ t*runtimeparam["dt"] for t in range( int( runtimeparam["tstop"]/runtimeparam["dt"] ) ) ]``

        ``>> rec_i = numpy.random.rand(1,len(rec_t))[0] # stimulus``

        ``>> rec_v = numpy.random.rand(2,len(rec_t))    # response``

        This model has ``model.regions = {'soma':0.0, 'axon':0.0}``

        For simulation without stimulation

        ``>> recordings = {"time": rec_t, "response": {"soma": rec_v[0], "axon": rec_v[1]}, "stimulus": "Model is not stimulated"}``

        ``>> respmd = tg.forcellrecording(chosenmodel = model, recordings = recordings, parameters = runtimeparam)``

        Simulation with stimulation

        ``>> stimparameters = {"type": ["current", "IClamp"], "stimlist": [ {"amp": 0.5, "dur": 100.0, "delay": 10.0}, {"amp": 1.0, "dur": 50.0, "delay": 10.0+100.0} ], "tstop": runtimeparam["tstop"]}``
        ``>> recordings = {"time": rec_t, "response": {"soma": rec_v[0], "axon": rec_v[1]}, "stimulus": rec_i}``

        ``>> respmd = tg.forcellrecording(chosenmodel = model, recordings = recordings, parameters = runtimeparam, stimparameters = stimparameters)``

        *NOTE:*

        * if there is NO stimulation and ``chosenmodel.regions={"soma": 0.0, "axon": 0.0}`` then ``len(respmd) = 2`` since there are two cell regions
        * also, this means ``respmd_soma = respmd["soma"]`` and ``respmd_axon = respmd["axon"]``
        * however, with stimulation there is an additional "stimulus" key ``stimulmd = respmmd["stimulus"]``

        """
        if (chosenmodel is None) or (recordings is None) or (runtimeparameters is None):
            raise ValueError("passing an instantiated chosenmodel, the recordings (dictionary) and runtimeparameters are  mandatory")
        elif chosenmodel.modelscale == "cells":
            return cls.forcellrecording( chosenmodel=chosenmodel,
                                          recordings=recordings,
                                          runtimeparameters=runtimeparameters,
                                          stimparameters=stimparameters )
