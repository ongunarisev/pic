# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
import pylab as plt
import numpy as np


class MZI_YB(i3.Circuit):
    fgc_spacing_y = 127.0
    control_point1 = i3.Coord2Property(doc="Point that the longer arm of the MZI has to go through")
    control_point2 = i3.Coord2Property(doc="Point that the longer arm of the MZI has to go through")
    control_point3 = i3.Coord2Property(doc="Point that the longer arm of the MZI has to go through")
    bend_radius = i3.PositiveNumberProperty(default=5.0, doc="Bend radius of the waveguides")

    fgc = i3.ChildCellProperty(doc="PCell for the fiber grating coupler")
    splitter = i3.ChildCellProperty(doc="PCell for the Y-Branch")

    def _default_control_point1(self):
        return -100.0, 3/2 * self.fgc_spacing_y

    def _default_control_point2(self):
        return -100.0, 5/2 * self.fgc_spacing_y

    def _default_control_point3(self):
        return -100.0, 1/2 * self.fgc_spacing_y

    def _default_fgc(self):
        return pdk.EbeamGCTE1550()

    def _default_splitter(self):
        return pdk.EbeamY1550()

    def _default_insts(self):
        insts = {
            "fgc_1": self.fgc,
            "fgc_2": self.fgc,
            "fgc_3": self.fgc,
            "fgc_4": self.fgc,
            "yb_s": self.splitter,
            "yb_ss": self.splitter,
            "yb_s1": self.splitter,
            "yb_s2": self.splitter,
            "yb_s3": self.splitter,
            "yb_c1": self.splitter,
            "yb_c2": self.splitter,
            "yb_c3": self.splitter,
        }
        return insts

    def _default_specs(self):
        fgc_spacing_y = self.fgc_spacing_y
        specs = [
            i3.Place("fgc_1:opt1", (0, 0)),
            i3.PlaceRelative("fgc_2:opt1", "fgc_1:opt1", (0.0, fgc_spacing_y)),
            i3.PlaceRelative("fgc_3:opt1", "fgc_2:opt1", (0.0, fgc_spacing_y)),
            i3.PlaceRelative("fgc_4:opt1", "fgc_3:opt1", (0.0, fgc_spacing_y)),
            i3.PlaceRelative("yb_ss:opt1", "yb_s:opt3", (10.0, -8.0), angle=90),
            i3.PlaceRelative("yb_s2:opt1", "yb_s:opt2", (10.0, 8.0), angle=-90),
            i3.PlaceRelative("yb_c1:opt1", "yb_s1:opt1", (0.0, -90), angle=-90),
            i3.Join("yb_ss:opt3", "yb_s1:opt1"),
            i3.PlaceRelative("yb_s3:opt1", "yb_ss:opt2", (15, -15.0), angle=90),
            i3.PlaceRelative("yb_c2:opt1", "yb_s:opt2", (10.0, fgc_spacing_y - 10.0), angle=90),
            i3.PlaceRelative("yb_c3:opt1", "yb_s3:opt1", (0.0,  - 205), angle=-90),
            i3.Join("fgc_3:opt1", "yb_s:opt1"),
        ]

        specs += [
            i3.ConnectManhattan(
                [
                    ("yb_s:opt3", "yb_ss:opt1"),
                    ("yb_s:opt2", "yb_s2:opt1"),
                    ("yb_c1:opt1", "fgc_2:opt1"),
                    ("yb_c2:opt1", "fgc_4:opt1"),
                    ("yb_s2:opt3", "yb_c2:opt2"),
                    ("yb_c3:opt1", "fgc_1:opt1"),
                    ("yb_ss:opt2", "yb_s3:opt1"),
                    ("yb_s3:opt2", "yb_c3:opt3"),
                    ("yb_s1:opt2", "yb_c1:opt3"),
                ]
            ),
            i3.ConnectManhattan("yb_s1:opt3", "yb_c1:opt2", control_points=[self.control_point1]),
            i3.ConnectManhattan("yb_s2:opt2", "yb_c2:opt3", control_points=[self.control_point2]),
            i3.ConnectManhattan("yb_s3:opt3", "yb_c3:opt2", control_points=[self.control_point3]),
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
            "fgc_4:fib1": "out2",
            "fgc_3:fib1": "in",
            "fgc_2:fib1": "out1",
            "fgc_1:fib1": "out3",
        }
        return exposed_ports


if __name__ == "__main__":

    # Layout
    mzi = MZI_YB(
        name="MZI",
        bend_radius=5.0,
    )
    mzi_layout = mzi.Layout()
    fig = mzi_layout.visualize(annotate=True)
    fig.axes[0].scatter(mzi.control_point1.x, mzi.control_point1.y, color='m')
    fig.axes[0].scatter(mzi.control_point2.x, mzi.control_point2.y, color='m')
    mzi_layout.write_gdsii("mzi_pcell_ybranch.gds")

    # Circuit model
    my_circuit_cm = mzi.CircuitModel()
    wavelengths = np.linspace(1.52, 1.58, 4001)
    S_total = my_circuit_cm.get_smatrix(wavelengths=wavelengths)

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(wavelengths, i3.signal_power_dB(S_total["out1:0", "in:0"]), "-", linewidth=2.2, label="TE-out1")
    ax.plot(wavelengths, i3.signal_power_dB(S_total["out2:0", "in:0"]), "-", linewidth=2.2, label="TE-out2")
    ax.plot(wavelengths, i3.signal_power_dB(S_total["out3:0", "in:0"]), "-", linewidth=2.2, label="TE-out3")
    ax.set_xlabel("Wavelength [um]", fontsize=16)
    ax.set_ylabel("Transmission [dB]", fontsize=16)
    ax.legend(fontsize=14, loc=4)
    plt.show()