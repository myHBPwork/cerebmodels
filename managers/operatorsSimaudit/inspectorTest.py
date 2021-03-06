# ~/managers/operatorsSimaudit/inspectorTest.py
import unittest
import os
import shutil
import sys

# import modules form other directories
# set to ~/cerebmodels
sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))
# this is required for 
# from managers.operatorsFiling.pathspawner import PathSpawner
# called in inspector.py

from inspector import SimInspector as si

from cerebunit.capabilities.cells.response import ProducesElectricalResponse

class SimInspectorTest(unittest.TestCase):

    def setUp(self):
        #self.si = SimInspector() # instance for non: static & class methods
        self.pwd = os.getcwd()

    #@unittest.skip("reason for skipping")
    def test_1_lock_and_load_nmodl_compile_libnrnmech(self):
        modelscale = "cells"
        modelname = "DummyTest"
        os.chdir("..") # this moves you up to ~/managers
        os.chdir("..") # you are now in parent /cerebmodels
        compile_path = os.getcwd() + os.sep + "models" + os.sep + modelscale + os.sep + modelname
        try:
            # try deleting previous compiled files
            shutil.rmtree(compile_path + os.sep + "x86_64")
        except:
            pass
        self.assertEqual( si.lock_and_load_nmodl(modelscale=modelscale,
                                                 modelname=modelname),
                          "nmodl has just been compiled")
        os.chdir(self.pwd) # reset to the location of this inspectorTest.py

    #@unittest.skip("reason for skipping")
    def test_2_lock_and_load_nmodl_alreadycompiled(self):
        modelscale = "cells"
        modelname = "DummyTest"
        os.chdir("..") # this moves you up to ~/managers
        os.chdir("..") # you are now in parent /cerebmodels
        compile_path = os.getcwd() + os.sep + "models" + os.sep + modelscale + os.sep + modelname
        self.assertEqual( si.lock_and_load_nmodl(modelscale=modelscale,
                                                 modelname=modelname),
                          "nmodl was already compiled")
        os.chdir(self.pwd) # reset to the location of this inspectorTest.py

    #@unittest.skip("reason for skipping")
    def test_3_check_compatibility_modelcapability_notin_cerebunit(self):
        modelscale = "cells"
        modelname = "DummyTest"
        os.chdir("..") # this moves you up to ~/managers
        os.chdir("..") # you are now in parent /cerebmodels
        compile_path = os.getcwd() + os.sep + "models" + os.sep + modelscale + os.sep + modelname
        self.assertRaises( AttributeError,
                           si.check_compatibility,
                           capability_name = "produce_bogus_response",
                           CerebUnit_capability = ProducesElectricalResponse )
        os.chdir(self.pwd) # reset to the location of this inspectorTest.py

    #@unittest.skip("reason for skipping")
    def test_4_check_compatibility_modelcapability_in_cerebunit(self):
        modelscale = "cells"
        modelname = "DummyTest"
        os.chdir("..") # this moves you up to ~/managers
        os.chdir("..") # you are now in parent /cerebmodels
        compile_path = os.getcwd() + os.sep + "models" + os.sep + modelscale + os.sep + modelname
        self.assertEqual( si.check_compatibility(
                                   capability_name = "produce_voltage_response",
                                   CerebUnit_capability = ProducesElectricalResponse ),
                          "ProducesElectricalResponse has the method produce_voltage_response" )
        os.chdir(self.pwd) # reset to the location of this inspectorTest.py

if __name__ == '__main__':
    unittest.main()
