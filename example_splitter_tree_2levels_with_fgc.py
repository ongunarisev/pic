# Copyright (C) 2020 Luceda Photonics

"""SPLITTER TREE WITH 3 SPLITTERS AND 2 LEVELS WITH FIBER GRATING COUPLERS

In this file, we are going to create a splitter tree with 3 splitters and 2 levels - one splitter on the first level
and two splitters on the second level.
We add one input and four output fiber grating couplers to the splitter.

The simplest way of building circuits in IPKISS is to use 'i3.Circuit'. i3.Circuit allows you to easily
define connectivity between a number of cell "instances".
When placing these instances, i3.Circuit will then generate all the waveguides (as separate PCells) needed to connect
them together.
In order to create a i3.Circuit, we have to create a dictionary of:
- instances (insts)
- placement and routing specifications (specs)
- exposed_ports

"""
from si_fab import all as pdk
from ipkiss3 import all as i3
import pylab as plt
import numpy as np


class SplitterTree2Levels(i3.Circuit):

    # 1. We define the properties of the PCell.
    splitter = i3.ChildCellProperty()
    fgc = i3.ChildCellProperty()
    spacing_x = i3.PositiveNumberProperty(default=100.0)
    spacing_y = i3.PositiveNumberProperty(default=50.0)

    def _default_splitter(self):
        return pdk.MMI1x2Optimized1550()

    def _default_fgc(self):
        return pdk.FC_TE_1550()

    # 2. We define instances that make up our circuit.
    # We have 3 splitters, 1 for the first level and 2 for the second level.
    def _default_insts(self):
        insts = {
            "sp_0_0": self.splitter,
            "sp_1_0": self.splitter,
            "sp_1_1": self.splitter,
            "fgc_in": self.fgc,
            "fgc_out_0": self.fgc,
            "fgc_out_1": self.fgc,
            "fgc_out_2": self.fgc,
            "fgc_out_3": self.fgc,
        }
        return insts

    # 3. We define placement and routing specifications, containing all the transformations that apply
    # to each component, and connectors (list of connector object calls) and ports to be connected.
    # The algorithm to connect the ports (i3.SplineRoundingAlgorithm -> Bezier bend) is specified when
    # instantiating a Connector object.
    def _default_specs(self):
        sp_x = self.spacing_x
        sp_y = self.spacing_y

        specs = [
            i3.Place("sp_0_0:in1", (0, 0)),
            i3.PlaceRelative("fgc_in:out", "sp_0_0:in1", (-sp_x / 2, 0.0)),
            i3.PlaceRelative("sp_1_0:in1", "sp_0_0:out1", (sp_x, -sp_y / 2)),
            i3.PlaceRelative("sp_1_1:in1", "sp_0_0:out2", (sp_x, sp_y / 2)),
            i3.PlaceRelative("fgc_out_0:out", "sp_1_0:out1", (sp_x, -sp_y / 4), angle=180),
            i3.PlaceRelative("fgc_out_1:out", "sp_1_0:out2", (sp_x, sp_y / 4), angle=180),
            i3.PlaceRelative("fgc_out_2:out", "sp_1_1:out1", (sp_x, -sp_y / 4), angle=180),
            i3.PlaceRelative("fgc_out_3:out", "sp_1_1:out2", (sp_x, sp_y / 4), angle=180),
            i3.ConnectManhattan("fgc_in:out", "sp_0_0:in1"),
            i3.ConnectBend(
                [
                    ("sp_0_0:out1", "sp_1_0:in1"),
                    ("sp_0_0:out2", "sp_1_1:in1"),
                ],
                rounding_algorithm=i3.EulerRoundingAlgorithm(p=0.5),
                bend_radius=20,
            ),
            i3.ConnectBend(
                [
                    ("sp_1_0:out1", "fgc_out_0:out"),
                    ("sp_1_0:out2", "fgc_out_1:out"),
                    ("sp_1_1:out1", "fgc_out_2:out"),
                    ("sp_1_1:out2", "fgc_out_3:out"),
                ],
                rounding_algorithm=i3.SplineRoundingAlgorithm(adiabatic_angles=(15.0, 15.0)),
                bend_radius=50,
            ),
        ]
        return specs

    # 4. We define the names of the external ports.
    def _default_exposed_ports(self):
        exposed_ports = {
            "fgc_in:vertical_in": "in",
            "fgc_out_0:vertical_in": "out1",
            "fgc_out_1:vertical_in": "out2",
            "fgc_out_2:vertical_in": "out3",
            "fgc_out_3:vertical_in": "out4",
        }
        return exposed_ports


if __name__ == "__main__":
    # 1. We instantiate the optimized MMI and the fiber grating coupler from si_fab
    mmi = pdk.MMI1x2Optimized1550()
    fgc = pdk.FC_TE_1550()

    # 2. We instantiate the 2-level splitter tree and visualize it
    splitter_tree = SplitterTree2Levels(splitter=mmi, fgc=fgc)
    splitter_tree_layout = splitter_tree.Layout()
    splitter_tree_layout.visualize(annotate=True)

    # 3. We instantiate the Circuit Model
    splitter_tree_cm = splitter_tree.CircuitModel()
    wavelengths = np.linspace(1.5, 1.6, 501)
    S_total = splitter_tree_cm.get_smatrix(wavelengths=wavelengths)

    # 4. We plot the transmission
    plt.plot(wavelengths, i3.signal_power_dB(S_total["out1", "in"]), "-", linewidth=2.2, label="out1")
    plt.plot(wavelengths, i3.signal_power_dB(S_total["out2", "in"]), "-", linewidth=2.2, label="out2")
    plt.plot(wavelengths, i3.signal_power_dB(S_total["out3", "in"]), "-", linewidth=2.2, label="out3")
    plt.plot(wavelengths, i3.signal_power_dB(S_total["out4", "in"]), "-", linewidth=2.2, label="out4")
    plt.plot(wavelengths, i3.signal_power_dB(S_total["in", "in"]), "-", linewidth=2.2, label="in")
    plt.ylim(-130, 0)
    plt.xlabel("Wavelength [um]", fontsize=16)
    plt.ylabel("Transmission [dB]", fontsize=16)
    plt.legend(fontsize=14, loc=4)
    plt.show()
