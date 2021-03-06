#Template of the Purkinje cell model connected to CF and PF, Zang et al. 2018
#Templating by Lungsi 2019 based on ~/CFPCnPFPC2018Zang/purkinje.hoc
#purkinje.hoc has been converted from original purkinje_demo and using readme.html as a guide
from neuron import h
#from pdb import set_trace as breakpoint

class CFPFtoPurkinje(object):
    """Multi-compartment cell connected to CF and PF
    """
    def __init__(self):
        h.xopen("purkinje.hoc")

        # There are 1088 compartments and the following are chosen as
        # attributes to this python class for potential recording
        self.soma = h.somaA
        self.ais = h.AIS
        # Based on last 50 or so lines of Purkinje19b972-1.nrn
        self.dend_root = h.dendA1_0 # see Fig.2A of paper
        # Reverse eng. from Purkinje19b972-1.nrn and dendv_arnd21.ses
        self.dend_sm = [ sec for sec in h.maindend ] # len(dend_sm) -> 30
        self.dend_sp = [ sec for sec in h.spinydend ] # len(dend_sp) -> 1105
        # note that for either self.dend_sm or self.dend_sp
        # the first element of its list is a dendrite section closest to soma
        # and last element is the dendrite section farthest away.
        # also potentially
        self.cf = [ sec for sec in h.cf ] # for climbing fibre
        self.pf = [ sec for sec in h.pf ] # for parallel fibre
        self.bs_cf = [ sec for sec in h.bs ] # for branch-specific climbing fibre

