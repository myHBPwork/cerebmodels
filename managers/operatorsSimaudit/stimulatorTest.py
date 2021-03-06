# ~/managers/operatorsSimaudit/stimulatorTest.py
import unittest
import shutil
import os
import sys
# import modules from other directories
# set to ~/cerebmodels
sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))
# this is required for
#from models.cells.modelDummyTest import DummyCell

# because IRamp is not by default its nmodl files need to be loaded
# testing for inject_IRamp requires SimInspector
#from managers.operatorsSimaudit.inspector import SimInspector as si
from inspector import SimInspector as si
#from managers.managerSimulation import SimulationManager

pwd = os.getcwd()
os.chdir("..") # this moves you up to ~/managers
os.chdir("..") # you are now in parent /cerebmodels
rootwd = os.getcwd()
from models.cells.modelDummyTest import DummyCell
os.chdir(pwd)

from stimulator import Stimulator

from neuron import h
h.load_file("stdrun.hoc")

class StimulatorTest(unittest.TestCase):

    def setUp(self):
        self.st = Stimulator()
        os.chdir(rootwd)
        self.chosenmodel = DummyCell()
        os.chdir(pwd)
        #self.sm = SimulationManager()

    #@unittest.skip("reason for skipping")
    def test_1_inject_IClamp_wrong_key_in_parameter(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        #parameters = {"dt": 0.1, "celsius": 20, "tstop": 15, "v_init": 65}
        #injparam = [ {"amp": 0.5, "dur": 5.0, "delay": 5.0},
        #             {"amp": 1.0, "dur": 5.0, "delay": parameters["tstop"]-5.0} ]
        #                    this last duration is subtracted from tstop
        #self.sm.prepare_model_NEURON(parameters, self.chosenmodel)
        injparam = [ {"amplitude": 0.5, "dur": 5.0, "delay": 5.0},
                     {"amp": 1.0, "dur": 5.0, "delay": 10.0} ]
        self.assertRaises( AttributeError,
                           self.st.inject_IClamp,
                           injparam,
                           self.chosenmodel.cell.soma )
        #os.chdir(pwd) # reset to the location of this stimulatorTest.py

    #@unittest.skip("reason for skipping")
    def test_2_inject_IClamp(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        injparam = [ {"amp": 0.5, "dur": 5.0, "delay": 5.0},
                     {"amp": 1.0, "dur": 5.0, "delay": 10.0} ]
        curr_stimuli = self.st.inject_IClamp(injparam, self.chosenmodel.cell.soma)
        self.assertEqual( len(curr_stimuli ), len(injparam) )
        #os.chdir(pwd) # reset to the location of this stimulatorTest.py

    #@unittest.skip("reason for skipping")
    def test_3_inject_IRamp(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        # load nmodl file for using the custom IRamp
        os.chdir(rootwd)
        si.lock_and_load_nmodl(modelscale="cells", modelname="DummyTest")
        #
        injparam = [ {"amp_initial": 0.0, "amp_final": 0.5, "dur": 5.0, "delay": 5.0},
                     {"amp_initial": 0.5, "amp_final": 1.0, "dur": 5.0, "delay": 10.0},
                     {"amp_initial": 1.0, "amp_final": 0.5, "dur": 5.0, "delay": 15.0},
                     {"amp_initial": 0.5, "amp_final": 0.0, "dur": 5.0, "delay": 20.0} ]
        curr_stimuli = self.st.inject_IRamp(injparam, self.chosenmodel.cell.soma)
        # here based on the injparm
        # increasing ramp is from injparam[0] to injparam[1] while
        # decreading ramp if from injparam[2] to injparam[3]. Thus,
        slopes = [ 0.5, 0.5, -0.5, -0.5 ]
        # NOTE: the magnitude for each slope is |amp_final - amp_initial| respectively.
        #
        curr_slopes = []
        for i in range(len(curr_stimuli)):
            curr_slopes.append( curr_stimuli[i].amp_final )
        #
        self.assertEqual( curr_slopes, slopes )
        os.chdir(pwd) # reset to the location of this stimulatorTest.py

    #@unittest.skip("reason for skipping")
    def test_4_inject_current_NEURON_without_currenttype(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        os.chdir(rootwd)
        injparam = [ {"amp": 0.5, "dur": 5.0, "delay": 5.0},
                     {"amp": 1.0, "dur": 5.0, "delay": 10.0} ]
        self.assertRaises( ValueError,
                           self.st.inject_current_NEURON,
                           injparameters = injparam,
                           neuronsection = self.chosenmodel.cell.soma )
        os.chdir(pwd) # reset to the location of this stimulatorTest.py

    #@unittest.skip("reason for skipping")
    def test_5_inject_current_NEURON_wrong_currenttype(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        os.chdir(rootwd)
        injparam = [ {"amp": 0.5, "dur": 5.0, "delay": 5.0},
                     {"amp": 1.0, "dur": 5.0, "delay": 10.0} ]
        self.assertRaises( ValueError,
                           self.st.inject_current_NEURON,
                           currenttype = "xyz",
                           injparameters = injparam,
                           neuronsection = self.chosenmodel.cell.soma )
        os.chdir(pwd) # reset to the location of this stimulatorTest.py

    #@unittest.skip("reason for skipping")
    def test_6_inject_current_NEURON_IClamp(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        os.chdir(rootwd)
        injparam = [ {"amp": 0.5, "dur": 5.0, "delay": 5.0},
                     {"amp": 1.0, "dur": 5.0, "delay": 10.0} ]
        self.assertEqual( len( self.st.inject_current_NEURON(
                                       currenttype = "IClamp",
                                       injparameters = injparam,
                                       neuronsection = self.chosenmodel.cell.soma)),
                          len(injparam) )
        os.chdir(pwd) # reset to the location of this stimulatorTest.py

    #@unittest.skip("reason for skipping")
    def test_7_inject_current_NEURON_IRamp(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        os.chdir(rootwd)
        # load nmodl file for using the custom IRamp
        si.lock_and_load_nmodl(modelscale="cells", modelname="DummyTest")
        #
        injparam = [ {"amp_initial": 0.0, "amp_final": 0.5, "dur": 5.0, "delay": 5.0},
                     {"amp_initial": 0.5, "amp_final": 1.0, "dur": 5.0, "delay": 10.0},
                     {"amp_initial": 1.0, "amp_final": 0.5, "dur": 5.0, "delay": 15.0},
                     {"amp_initial": 0.5, "amp_final": 0.0, "dur": 5.0, "delay": 20.0} ]
        curr_stimuli = self.st.inject_current_NEURON(
                                       currenttype = "IRamp",
                                       injparameters = injparam,
                                       neuronsection = self.chosenmodel.cell.soma)
        self.assertEqual( len(curr_stimuli ), len(injparam) )
        os.chdir(pwd) # reset to the location of this stimulatorTest.py
        #shutil.rmtree("x86_64") # remove created directory ~/operatorsSimaudit/x86_64

    #@unittest.skip("reason for skipping")
    def test_8_inject_SEClamp(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        injparam = [ {"amp1": 0.0, "dur1": 50.0, "rs": 0.01},
                     {"amp2": -70., "dur2": 100.},
                     {"amp3": 50.0, "dur3": 150.0} ]
        voltg_stimuli = self.st.inject_SEClamp(injparam, self.chosenmodel.cell.soma)
        self.assertEqual( [voltg_stimuli.amp1, voltg_stimuli.dur2, voltg_stimuli.dur3],
                          [injparam[0]["amp1"], injparam[1]["dur2"], injparam[2]["dur3"]] )
        #os.chdir(pwd) # reset to the location of this stimulatorTest.py

    #@unittest.skip("reason for skipping")
    def test_9_inject_VClamp(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        injparam = [ {"amp": 0.0, "dur": 50.0},
                     {"amp": -70., "dur": 100.},
                     {"amp": 50.0, "dur": 150.0} ]
        voltg_stimuli = self.st.inject_VClamp(injparam, self.chosenmodel.cell.soma)
        self.assertEqual( [voltg_stimuli.amp[0], voltg_stimuli.dur[1], voltg_stimuli.dur[2]],
                          [injparam[0]["amp"], injparam[1]["dur"], injparam[2]["dur"]] )
        #os.chdir(pwd) # reset to the location of this stimulatorTest.py

    #@unittest.skip("reason for skipping")
    def test_10_inject_voltage_NEURON_SEClamp(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        os.chdir(rootwd)
        injparam = [ {"amp1": 0.0, "dur1": 50.0},
                     {"amp2": -70., "dur2": 100.},
                     {"amp3": 50.0, "dur3": 150.0} ]
        voltg_stimuli = self.st.inject_voltage_NEURON(
                                       voltagetype = "SEClamp",
                                       injparameters = injparam,
                                       neuronsection = self.chosenmodel.cell.soma)
        self.assertEqual( [voltg_stimuli.amp1, voltg_stimuli.dur2, voltg_stimuli.dur3],
                          [injparam[0]["amp1"], injparam[1]["dur2"], injparam[2]["dur3"]] )
        os.chdir(pwd) # reset to the location of this stimulatorTest.py

    #@unittest.skip("reason for skipping")
    def test_11_inject_voltage_NEURON_VClamp(self):
        #os.chdir("..") # this moves you up to ~/managers
        #os.chdir("..") # you are now in parent /cerebmodels
        os.chdir(rootwd)
        injparam = [ {"amp": 0.0, "dur": 50.0, "tau1": 5},
                     {"amp": -70., "dur": 100.},
                     {"amp": 50.0, "dur": 150.0} ]
        voltg_stimuli = self.st.inject_voltage_NEURON(
                                       voltagetype = "VClamp",
                                       injparameters = injparam,
                                       neuronsection = self.chosenmodel.cell.soma)
        self.assertEqual( [voltg_stimuli.amp[0], voltg_stimuli.dur[1], voltg_stimuli.tau1],
                          [injparam[0]["amp"], injparam[1]["dur"], injparam[0]["tau1"]] )
        os.chdir(pwd) # reset to the location of this stimulatorTest.py

if __name__ == '__main__':
    unittest.main()
