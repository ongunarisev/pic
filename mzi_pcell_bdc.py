# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
from ipkiss.technology import get_technology
import pylab as plt
import numpy as np

TECH = get_technology()


class MZI_BDC(i3.Circuit):

    control_point = i3.Coord2Property(doc="Point that the longer arm of the MZI has to go through")
    bend_radius = i3.PositiveNumberProperty(default=5.0, doc="Bend radius of the waveguides")

    fgc = i3.ChildCellProperty(doc="PCell for the fiber grating coupler")
    splitter = i3.ChildCellProperty(doc="PCell for the Y-Branch")
    dir_coupler = i3.ChildCellProperty(doc="PCell for the directional coupler")
    fgc_spacing_y = i3.PositiveNumberProperty(default=127.0, doc="Fiber separation")
    measurement_label_position = i3.Coord2Property(doc="Placement of automated measurement label")
    measurement_label_pretext = "opt_in_TE_1550_device_Vesnog_"

    def _default_measurement_label_position(self):
        return 0.0, self.fgc_spacing_y

    def _default_control_point(self):
        return [(100.0, 220.0)]

    def _default_fgc(self):
        return pdk.EbeamGCTE1550()

    def _default_splitter(self):
        return pdk.EbeamY1550()

    def _default_dir_coupler(self):
        return pdk.EbeamBDCTE1550()

    def _default_insts(self):
        insts = {
            "fgc_1": self.fgc,
            "fgc_2": self.fgc,
            "fgc_3": self.fgc,
            "yb": self.splitter,
            "dc": self.dir_coupler,
        }
        return insts

    def _default_specs(self):
        # fgc_spacing_y = 127.0
        specs = [
            i3.Place("fgc_1:opt1", (0, 0)),
            i3.PlaceRelative("fgc_2:opt1", "fgc_1:opt1", (0.0, self.fgc_spacing_y)),
            i3.PlaceRelative("fgc_3:opt1", "fgc_2:opt1", (0.0, self.fgc_spacing_y)),
            i3.PlaceRelative("dc:opt1", "yb:opt2", (20.0, -40.0), angle=90),
            i3.Join("fgc_3:opt1", "yb:opt1"),
        ]

        specs += [
            i3.ConnectManhattan(
                [
                    ("yb:opt3", "dc:opt2", "yb_opt3_to_dc_opt2"),
                    ("dc:opt4", "fgc_2:opt1", "dc_opt4_to_fgc_2_opt1"),
                    ("dc:opt3", "fgc_1:opt1", "dc_opt3_to_fgc_1_opt1"),
                ]
            ),
            i3.ConnectManhattan("yb:opt2", "dc:opt1", "yb_opt2_to_dc_opt1", control_points=[self.control_point]),
        ]
        return specs

    def get_connector_instances(self):
        lv_instances = self.get_default_view(i3.LayoutView).instances
        return [
            lv_instances["yb_opt3_to_dc_opt2"],
            lv_instances["yb_opt2_to_dc_opt1"],
            lv_instances["dc_opt4_to_fgc_2_opt1"],
            lv_instances["dc_opt3_to_fgc_1_opt1"],
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
    mzi = MZI_BDC(
        name="MZI",
        control_point=(100.0, 240.0),
        bend_radius=5.0,
    )
    mzi_layout = mzi.Layout()
    mzi_layout.visualize(annotate=True)
    mzi_layout.visualize_2d()
    mzi_layout.write_gdsii("mzi.gds")

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
