# ~/models/cells/DummyTest/Dummy.py

from neuron import h

class Dummy(object):
    def __init__(self):
        self.soma = h.Section(name='soma')
        
        ### ====== STANDARDIZED FOR cerebmodels =======
        ### ===== mandatory for all NEURON models =====
	self.rec_t = h.Vector()
	self.rec_t.record(h._ref_t)
        # ------- this will be the cell-regions -------
	self.vm_soma = h.Vector()
	self.vm_soma.record(self.soma(0.5)._ref_v)
