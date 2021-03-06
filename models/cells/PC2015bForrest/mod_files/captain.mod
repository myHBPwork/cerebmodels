: HH P-type Calcium current
: FORREST MD (2014) Two Compartment Model of the Cerebellar Purkinje Neuron

NEURON {
	SUFFIX captain
	USEION ca READ cai, cao WRITE ica
	RANGE pcabar
	GLOBAL minf,mtau
	GLOBAL monovalConc, monovalPerm
}

UNITS {
	(mV) = (millivolt)
	(mA) = (milliamp)
	(mM) = (milli/liter)
	F = 9.6485e4   (coul)
	R = 8.3145 (joule/degC)
}

PARAMETER {
	v (mV)

	pcabar = .00005	(cm/s)
	monovalConc = 140     (mM)
	monovalPerm = 0

	cai             (milli/liter)
	cao             (milli/liter)
Q10 = 3 (1) 
  Q10TEMP = 22 (degC) 
}

ASSIGNED {
	ica            (mA/cm2)
        minf
	mtau           (ms)
	T              (degC)
	E              (volts)
celsius (degC) 
  qt (1) 

}

STATE {
	m
}

INITIAL {
	rates(v)
	m = minf
: qt = Q10^((celsius-Q10TEMP)/10) 
qt = 1
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	ica = (1e3) * pcabar * m * ghk(v, cai, cao, 2)
}

DERIVATIVE states {
	rates(v)
	m' = (minf - m)/mtau
}

FUNCTION ghk( v(mV), ci(mM), co(mM), z)  (coul/cm3) { LOCAL Ci
	T = 22 + 273.19  : Kelvin
        E = (1e-3) * v
        Ci = ci + (monovalPerm) * (monovalConc)        : Monovalent permeability
	if (fabs(1-exp(-z*(F*E)/(R*T))) < 1e-6) { : denominator is small -> Taylor series
		ghk = (1e-6) * z * F * (Ci-co*exp(-z*(F*E)/(R*T)))*(1-(z*(F*E)/(R*T)))
	} else {
		ghk = (1e-6) * z^2*(E*F^2)/(R*T)*(Ci-co*exp(-z*(F*E)/(R*T)))/(1-exp(-z*(F*E)/(R*T)))
	}
}

PROCEDURE rates (v (mV)) {
        UNITSOFF
	minf = 1/(1+exp(-(v - (-19)) / 5.5))
	mtau = ((mtau_func(v)) * 1e3) / qt
        UNITSON
}

FUNCTION mtau_func( v (mV) ) (ms) {
        UNITSOFF
        if (v > -50) {
            mtau_func = .000191 + .00376*exp(-((v-(-41.9))/27.8)^2)
        } else {
            mtau_func = .00026367 + .1278 * exp(.10327*v)
        }
        UNITSON
}
