# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
from ipkiss.technology import get_technology
import pylab as plt
import numpy as np

TECH = get_technology()


class MZI(i3.Circuit):

    control_point = i3.Coord2Property(doc="Point that the longer arm of the MZI has to go through")
    bend_radius = i3.PositiveNumberProperty(default=5.0, doc="Bend radius of the waveguides")

    fgc = i3.ChildCellProperty(doc="PCell for the fiber grating coupler")
    splitter = i3.ChildCellProperty(doc="PCell for the Y-Branch")

    def _default_control_point(self):
        return [(100.0, 220.0)]

    def _default_fgc(self):
        return pdk.EbeamGCTE1550()

    def _default_splitter(self):
        return pdk.EbeamY1550()

    def _default_insts(self):
        insts = {
            "fgc_1": self.fgc,
            "fgc_2": self.fgc,
            "fgc_3": self.fgc,
            "yb_s": self.splitter,
            "yb_s1": self.splitter,
            "yb_s2": self.splitter,
            "yb_c1": self.splitter,
            "yb_c2": self.splitter,
        }
        return insts

    def _default_specs(self):
        fgc_spacing_y = 127.0
        specs = [
            i3.Place("fgc_1:opt1", (0, 0)),
            i3.PlaceRelative("fgc_2:opt1", "fgc_1:opt1", (0.0, fgc_spacing_y)),
            i3.PlaceRelative("fgc_3:opt1", "fgc_2:opt1", (0.0, fgc_spacing_y)),
            i3.PlaceRelative("yb_s1:opt1", "yb_s:opt3", (20.0, -fgc_spacing_y / 8), angle=90),
            i3.PlaceRelative("yb_s2:opt1", "yb_s:opt2", (20.0, fgc_spacing_y / 8), angle=-90),
            i3.PlaceRelative("yb_c1:opt1", "yb_s:opt3", (20.0, -7*fgc_spacing_y / 8), angle=-90),
            i3.PlaceRelative("yb_c2:opt1", "yb_s:opt2", (20.0, 7*fgc_spacing_y / 8), angle=90),
            i3.Join("fgc_2:opt1", "yb_s:opt1"),
        ]

        specs += [
            i3.ConnectManhattan(
                [
                    ("yb_s:opt3", "yb_s1:opt1", "yb_s_opt3_to_yb_s1_opt1"),
                    ("yb_s:opt2", "yb_s2:opt1", "yb_s_opt3_to_yb_s2_opt1"),
                    ("yb_c1:opt1", "fgc_1:opt1", "yb_c1_opt1_to_fgc_1_opt1"),
                    ("yb_c2:opt1", "fgc_3:opt1", "yb_c2_opt1_to_fgc_1_opt1"),
                    ("yb_s2:opt2", "yb_c2:opt3", "yb_s2_opt2_to_yb_c2_opt3"),
                    ("yb_s1:opt3", "yb_c1:opt2", "yb_s1_opt2_to_yb_c1_opt2"),
                ]
            ),
            i3.ConnectManhattan("yb_s1:opt2", "yb_c1:opt3", "yb_s1_opt2_to_yb_c1_opt3"), #, control_points=[self.control_point]),
            i3.ConnectManhattan("yb_s2:opt3", "yb_c2:opt2", "yb_s2_opt3_to_yb_c2_opt3") #, control_points=[self.control_point]),
        ]
        return specs

    def get_connector_instances(self):
        lv_instances = self.get_default_view(i3.LayoutView).instances
        return [
            lv_instances["ybs_opt3_to_ybc_opt2"],
            lv_instances["ybc_opt1_to_fgc_2_opt1"],
            lv_instances["ybs_opt2_to_ybc_opt3"],
        ]

    def _default_exposed_ports(self):
        exposed_ports = {
            "fgc_3:fib1": "out1",
            "fgc_2:fib1": "in",
            "fgc_1:fib1": "out2",
        }
        return exposed_ports


if __name__ == "__main__":

    # Layout
    mzi = MZI(
        name="MZI",
        control_point=(100.0, 240.0),
        bend_radius=5.0,
    )
    mzi_layout = mzi.Layout()
    mzi_layout.visualize(annotate=True)
    # mzi_layout.visualize_2d()
    # mzi_layout.write_gdsii("mzi.gds")

    # Circuit model
    my_circuit_cm = mzi.CircuitModel()
    wavelengths = np.linspace(1.52, 1.58, 4001)
    S_total = my_circuit_cm.get_smatrix(wavelengths=wavelengths)

    # Plotting
    plt.plot(wavelengths, i3.signal_power_dB(S_total["out1:0", "in:0"]), "-", linewidth=2.2, label="TE-out1")
    plt.plot(wavelengths, i3.signal_power_dB(S_total["out2:0", "in:0"]), "-", linewidth=2.2, label="TE-out2")
    plt.xlabel("Wavelength [um]", fontsize=16)
    plt.ylabel("Transmission [dB]", fontsize=16)
    plt.legend(fontsize=14, loc=4)
    plt.show()
