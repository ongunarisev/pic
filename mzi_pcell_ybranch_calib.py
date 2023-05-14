# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
import pylab as plt
import numpy as np


class MZI_YB_calib(i3.Circuit):
    fgc_spacing_y = 127.0
    bend_radius = i3.PositiveNumberProperty(default=5.0, doc="Bend radius of the waveguides")

    fgc = i3.ChildCellProperty(doc="PCell for the fiber grating coupler")
    splitter = i3.ChildCellProperty(doc="PCell for the Y-Branch")
    fgc_spacing_y = i3.PositiveNumberProperty(default=127.0, doc="Fiber separation")
    measurement_label_position = i3.Coord2Property(doc="Placement of automated measurement label")
    measurement_label_pretext = "opt_in_TE_1550_device_Vesnog_"

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
            "fgc_3": self.fgc,
            "yb_s": self.splitter,
        }
        return insts

    def _default_specs(self):
        fgc_spacing_y = self.fgc_spacing_y
        specs = [
            i3.Place("fgc_1:opt1", (0, 0)),
            i3.PlaceRelative("fgc_2:opt1", "fgc_1:opt1", (0.0, fgc_spacing_y)),
            i3.PlaceRelative("fgc_3:opt1", "fgc_2:opt1", (0.0, fgc_spacing_y)),
            i3.Join("fgc_2:opt1", "yb_s:opt1"),
        ]

        specs += [
            i3.ConnectManhattan(
                [
                    ("yb_s:opt3", "fgc_1:opt1"),
                    ("yb_s:opt2", "fgc_3:opt1"),
                ],
                control_points=[i3.V(20.0+self.splitter.Layout().size_info().width)]
            ),

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
            "fgc_3:fib1": "out2",
            "fgc_2:fib1": "in",
            "fgc_1:fib1": "out1",
        }
        return exposed_ports


if __name__ == "__main__":

    # Layout
    mzi = MZI_YB_calib(
        name="MZI",
        bend_radius=5.0,
    )
    mzi_layout = mzi.Layout()
    fig = mzi_layout.visualize(annotate=True)
    # mzi_layout.write_gdsii("mzi.gds")
