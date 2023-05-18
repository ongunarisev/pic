# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
from ipkiss.process.layer_map import GenericGdsiiPPLayerOutputMap
from bond_pads import BondPad, pplayer_map
import pylab as plt
import numpy as np


class MZI_YB_thermo(i3.Circuit):
    bend_radius = i3.PositiveNumberProperty(default=5.0, doc="Bend radius of the waveguides")
    heater_width = i3.PositiveNumberProperty(default=4.0, doc="Heater width")
    heater_length = i3.PositiveNumberProperty(default=100.0, doc="Heater length in microns")
    arm_spacing = i3.PositiveNumberProperty(default=20, doc="MZI arms spacing")
    fgc = i3.ChildCellProperty(doc="PCell for the fiber grating coupler")
    splitter = i3.ChildCellProperty(doc="PCell for the Y-Branch")
    fgc_spacing_y = i3.PositiveNumberProperty(default=127.0, doc="Fiber separation")
    bond_pad_spacing_y = i3.PositiveNumberProperty(default=125.0, doc="Electrical bond pad separation")
    measurement_label_position = i3.Coord2Property(doc="Placement of automated measurement label")
    measurement_label_pretext = "opt_in_TE_1550_device_Vesnog_"
    bond_pad = BondPad(name="Metal Contact")

    def _default_measurement_label_position(self):
        return 0.0, self.fgc_spacing_y

    def _default_fgc(self):
        return pdk.EbeamGCTE1550()

    def _default_splitter(self):
        return pdk.EbeamY1550()

    def _default_insts(self):
        insts = {
            "fgc_1": self.fgc,
            "fgc_2": self.fgc,
            "yb_s1": self.splitter,
            "yb_c1": self.splitter,
            "bp_1": self.bond_pad,
            "bp_2": self.bond_pad,
            # "bp_3": self.bond_pad,
            # "bp_4": self.bond_pad,
        }
        return insts

    def _default_specs(self):
        fgc_spacing_y = self.fgc_spacing_y
        mzi_splitter_x = 150
        specs = [
            i3.Place("fgc_1:opt1", (0, 0)),
            i3.PlaceRelative("fgc_2:opt1", "fgc_1:opt1", (0.0, fgc_spacing_y)),
            # Adhere by the placement rules to avoid metal burning damaging the fiber array
            i3.PlaceRelative("yb_s1:opt1", "fgc_2:opt1", (mzi_splitter_x, 40.0), angle=90),
            i3.PlaceRelative("yb_c1:opt1", "fgc_1:opt1", (mzi_splitter_x, -40.0), angle=-90),
            i3.Place("bp_1", (350, 0)),
            i3.PlaceRelative("bp_2", "bp_1", (0, 125)),
        ]

        specs += [
            i3.ConnectManhattan("fgc_2:opt1", "yb_s1:opt1", control_points=[i3.V(15)]),
            i3.ConnectManhattan("yb_c1:opt1", "fgc_1:opt1", control_points=[i3.V(15)]),
            i3.ConnectManhattan("yb_s1:opt3", "yb_c1:opt2", control_points=[i3.V(mzi_splitter_x - self.arm_spacing/2)]),
            i3.ConnectManhattan("yb_s1:opt2", "yb_c1:opt3", control_points=[i3.V(mzi_splitter_x + self.arm_spacing/2)]),
        ]
        return specs

    def get_connector_instances(self):
        lv_instances = self.get_default_view(i3.LayoutView).instances
        return [
            lv_instances["yb_s1_opt2_to_yb_c1_opt3"],  # Long arm MZI 1
            lv_instances["yb_s1_opt3_to_yb_c1_opt2"],
            lv_instances["yb_s2_opt3_to_yb_c2_opt2"],  # Long arm MZI 2
            lv_instances["yb_s2_opt2_to_yb_c2_opt3"]
        ]

    def _default_exposed_ports(self):
        exposed_ports = {
            "fgc_2:fib1": "in",
            "fgc_1:fib1": "out",
        }
        return exposed_ports


if __name__ == "__main__":

    # Layout
    mzi = MZI_YB_thermo(
        name="MZI",
        bend_radius=5.0,
    )
    output_layer_map = GenericGdsiiPPLayerOutputMap(pplayer_map=pplayer_map)
    mzi_layout = mzi.Layout()
    fig = mzi_layout.visualize(annotate=True)
    mzi_layout.visualize_2d()
    mzi_layout.write_gdsii("mzi_heater.gds", layer_map=output_layer_map)

    # Circuit model
    my_circuit_cm = mzi.CircuitModel()
    wavelengths = np.linspace(1.52, 1.58, 4001)
    S_total = my_circuit_cm.get_smatrix(wavelengths=wavelengths)

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(wavelengths, i3.signal_power_dB(S_total["out:0", "in:0"]), "-", linewidth=2.2, label="TE-out1")
    ax.set_xlabel("Wavelength [um]", fontsize=16)
    ax.set_ylabel("Transmission [dB]", fontsize=16)
    ax.legend(fontsize=14, loc=4)
    plt.show()
