# Copyright (C) 2020 Luceda Photonics

"""This file contains the PCell of the full circuit that makes the WBG functional for temperature sensing.
It not only includes the WBG, but also the splitter, I/O grating couplers and connecting waveguides.
"""

import siepic.all as pdk
import ipkiss3.all as i3


class WBGCircuit(i3.Circuit):
    wbg = i3.PCellProperty(doc="Unit cell of the WBG")
    fiber_coupler_pitch = i3.PositiveNumberProperty(doc="Distance between fiber grating couplers", default=127.0)
    bend_radius = i3.PositiveNumberProperty(doc="Bend radius of the connecting waveguides", default=10.0)
    measurement_label_position = i3.Coord2Property(doc="Placement of automated measurement label")
    measurement_label_pretext = "opt_in_TE_1550_device_Vesnog_"

    def _default_measurement_label_position(self):
        return 0.0, 2*127

    def _default_insts(self):
        fc = pdk.EbeamGCTE1550()
        return {
            "wbg": self.wbg,
            "fib_in": fc,
            "fib_out_wbg_t": fc,
            "fib_out_ref": fc,
            "fib_out_wbg_r": fc,
            "splitter": pdk.EbeamAdiabaticTE1550(),
        }

    def _default_specs(self):
        br = self.bend_radius
        fcp = self.fiber_coupler_pitch
        wbg_cell = self.insts["wbg"]
        wbg_length = wbg_cell.Layout().ports["out"].x - wbg_cell.Layout().ports["in"].x
        wbg_y_offset = (1.5 * fcp - wbg_length) / 2.0
        fc_names = ["fib_out_ref", "fib_out_wbg_r", "fib_in", "fib_out_wbg_t"]
        specs = [i3.Place("{}:opt1".format(fc), (0, cnt * fcp)) for cnt, fc in enumerate(fc_names)]
        specs.append(i3.PlaceRelative("splitter", "fib_in:opt1", (2 * br, -fcp / 2.0)))  # noqa
        specs.append(i3.PlaceRelative("wbg:in", "splitter:opt3", (br, wbg_y_offset), angle=-90))  # noqa

        specs.append(
            i3.ConnectManhattan(
                [
                    ("fib_in:opt1", "splitter:opt1"),
                    ("splitter:opt3", "wbg:in"),
                    ("wbg:out", "fib_out_wbg_t:opt1"),
                    ("splitter:opt4", "fib_out_ref:opt1"),
                    ("splitter:opt2", "fib_out_wbg_r:opt1"),
                ],
                bend_radius=self.bend_radius,
                min_straight=0,
            )
        )

        return specs

    def _default_exposed_ports(self):
        return {
            "fib_in:fib1": "in",
            "fib_out_wbg_t:fib1": "wbg_t",
            "fib_out_wbg_r:fib1": "wbg_r",
            "fib_out_ref:fib1": "ref",
        }
