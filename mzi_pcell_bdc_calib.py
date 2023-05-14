# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
import pylab as plt
import numpy as np



class MZI_BDC_calib(i3.Circuit):

    bend_radius = i3.PositiveNumberProperty(default=5.0, doc="Bend radius of the waveguides")

    fgc = i3.ChildCellProperty(doc="PCell for the fiber grating coupler")
    fgc_spacing_y = i3.PositiveNumberProperty(default=127.0, doc="Fiber separation")
    measurement_label_position = i3.Coord2Property(doc="Placement of automated measurement label")
    measurement_label_pretext = "opt_in_TE_1550_device_Vesnog_"

    def _default_measurement_label_position(self):
        return 0.0, 0.0

    def _default_fgc(self):
        return pdk.EbeamGCTE1550()

    def _default_insts(self):
        insts = {
            "fgc_1": self.fgc,
            "fgc_2": self.fgc,
        }
        return insts

    def _default_specs(self):
        # fgc_spacing_y = 127.0
        specs = [
            i3.Place("fgc_1:opt1", (0, 0)),
            i3.PlaceRelative("fgc_2:opt1", "fgc_1:opt1", (0.0, self.fgc_spacing_y)),
        ]
        x_add = pdk.EbeamY1550().Layout().size_info().width
        specs += [
            i3.ConnectManhattan("fgc_1:opt1", "fgc_2:opt1", control_points=[i3.V(20.0+x_add)]),
        ]
        return specs

    def _default_exposed_ports(self):
        exposed_ports = {
            "fgc_2:fib1": "out1",
            "fgc_1:fib1": "in",
        }
        return exposed_ports


if __name__ == "__main__":

    # Layout
    mzi = MZI_BDC_calib(
        name="MZI",
        bend_radius=5.0,
    )
    mzi_layout = mzi.Layout()
    mzi_layout.visualize(annotate=True)
    mzi_layout.visualize_2d()
    # mzi_layout.write_gdsii("mzi.gds")
