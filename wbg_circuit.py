# Copyright (C) 2020 Luceda Photonics

"""This file will invoke the full circuit that makes WBG functional for temperature sensing.
It will calculate the relevant transmission spectra and finally export the .gds file of the circuit.
"""

import siepic.all as pdk
from pteam_library_siepic.all import UnitCellRectangular, UniformWBG
import ipkiss3.all as i3
from wbg_cell import WBGCircuit
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np


########################################################################################################################
# Set up the unit cell, WBG and then the full circuit.
########################################################################################################################

width = 0.5
deltawidth = 0.089
dc = 0.2
lambdab = 0.325

uc = UnitCellRectangular(
    width=width,
    deltawidth=deltawidth,
    length1=(1 - dc) * lambdab,
    length2=dc * lambdab,
)

wbg = UniformWBG(uc=uc, n_uc=300)

full_circuit = WBGCircuit(wbg=wbg)
full_circuit_lo = full_circuit.Layout()
full_circuit_lo.visualize(annotate=True)


########################################################################################################################
# Simulate the whole circuit
########################################################################################################################

temperatures = np.linspace(273, 373, 3)
wavelengths = np.arange(1.52, 1.58, 0.0001)

fig = plt.figure(constrained_layout=True)
gs = gridspec.GridSpec(1, 2, figure=fig)
axes_sparam = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]

axes_sparam[0].set_xlabel(r"Wavelength (nm)", fontsize=16)
axes_sparam[0].set_ylabel("WBG Reflection (a.u.)", fontsize=16)
axes_sparam[0].set_title("Raw data", fontsize=20)

axes_sparam[1].set_xlabel(r"Wavelength (nm)", fontsize=16)
axes_sparam[1].set_ylabel("WBG Reflection (a.u.)", fontsize=16)
axes_sparam[1].set_title("Normalised data", fontsize=20)

for temperature in temperatures:

    wbg.CircuitModel(temperature=temperature)
    full_circuit = WBGCircuit(wbg=wbg)

    full_circuit_cm = full_circuit.CircuitModel()
    full_circuit_Smatrix = full_circuit_cm.get_smatrix(wavelengths=wavelengths)
    reflection = i3.signal_power(full_circuit_Smatrix["in:0", "wbg_r:0"])
    transmission_ref = i3.signal_power(full_circuit_Smatrix["in:0", "ref:0"])

    axes_sparam[0].plot(
        wavelengths * 1000,
        reflection,
        "o-",
        linewidth=2.2,
        label=r"Reflection at " + str(int(temperature - 273)) + r" $^{\circ}C$",
    )
    axes_sparam[1].plot(
        wavelengths * 1000,
        reflection / transmission_ref,
        "o-",
        linewidth=2.2,
        label=r"Reflection at " + str(int(temperature - 273)) + r" $^{\circ}C$",
    )

axes_sparam[0].legend(fontsize=14, loc=6)
axes_sparam[1].legend(fontsize=14, loc=6)
axes_sparam[0].tick_params(which="both", labelsize=14)
axes_sparam[1].tick_params(which="both", labelsize=14)
plt.show()


########################################################################################################################
# Export the circuit to GDS
########################################################################################################################

full_circuit_lo.write_gdsii("full_circuit.gds")
