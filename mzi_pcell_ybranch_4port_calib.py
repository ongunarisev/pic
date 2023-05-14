# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
import pylab as plt
import numpy as np


class MZI_YB_4port_calib(i3.Circuit):
    fgc_spacing_y = 127.0
    control_point1 = i3.NumberProperty(doc="Point that the longer arm of the MZI has to go through")
    control_point2 = i3.NumberProperty(doc="Point that the longer arm of the MZI has to go through")
    control_point3 = i3.NumberProperty(doc="Point that the longer arm of the MZI has to go through")
    bend_radius = i3.PositiveNumberProperty(default=5.0, doc="Bend radius of the waveguides")

    fgc = i3.ChildCellProperty(doc="PCell for the fiber grating coupler")
    splitter = i3.ChildCellProperty(doc="PCell for the Y-Branch")
    fgc_spacing_y = i3.PositiveNumberProperty(default=127.0, doc="Fiber separation")
    measurement_label_position = i3.Coord2Property(doc="Placement of automated measurement label")
    measurement_label_pretext = "opt_in_TE_1550_device_Vesnog_"

    def _default_measurement_label_position(self):
        return 0.0, 2*self.fgc_spacing_y

    def _default_control_point1(self):
        return -100.0

    def _default_control_point2(self):
        return -100.0

    def _default_control_point3(self):
        return -100.0

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
            i3.Join("fgc_3:opt1", "yb_s:opt1"),
        ]

        specs += [
            i3.ConnectManhattan(
                [
                    ("yb_ss:opt3", "fgc_2:opt1"),
                    ("yb_ss:opt2", "fgc_1:opt1"),
                    ("yb_s:opt3", "yb_ss:opt1"),
                ]
            ),
            i3.ConnectManhattan("yb_s:opt2", "fgc_4:opt1", control_points=[i3.V(10.0 + self.splitter.Layout().size_info().width)]
)
        ]
        return specs

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
    mzi = MZI_YB_4port_calib(
        name="MZI",
        bend_radius=5.0,
    )
    mzi_layout = mzi.Layout()
    fig = mzi_layout.visualize(annotate=True)
    # fig.axes[0].scatter(mzi.control_point1.x, mzi.control_point1.y, color='m')
    # fig.axes[0].scatter(mzi.control_point2.x, mzi.control_point2.y, color='m')
    # mzi_layout.write_gdsii("mzi_pcell_ybranch.gds")
