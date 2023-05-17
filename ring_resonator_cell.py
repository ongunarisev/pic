# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
import pylab as plt
import numpy as np


class RingResonator(i3.Circuit):

    bend_radius = i3.PositiveNumberProperty(default=5.0, doc="Bend radius of the waveguides")
    fgc = i3.ChildCellProperty(doc="PCell for the fiber grating coupler")
    ring = i3.ChildCellProperty(doc="Ring resonator")
    fgc_spacing_y = i3.PositiveNumberProperty(default=127.0, doc="Fiber separation")
    measurement_label_position = i3.Coord2Property(doc="Placement of automated measurement label")
    measurement_label_pretext = "opt_in_TE_1550_device_Vesnog_"

    def _default_measurement_label_position(self):
        return 0.0, 2*self.fgc_spacing_y

    def _default_fgc(self):
        return pdk.EbeamGCTE1550()

    def _default_splitter(self):
        return pdk.EbeamY1550()

    def _default_dir_coupler(self):
        return pdk.EbeamBDCTE1550()

    def _default_ring(self):
        return pdk.EbeamAddDropSymmStraight()


    def _default_insts(self):
        insts = {
            "fgc_1": self.fgc,
            "fgc_2": self.fgc,
            "fgc_3": self.fgc,
            "fgc_4": self.fgc,
            "rr": self.ring
        }
        return insts

    def _default_specs(self):
        size_info = self.ring.Layout().size_info()
        rel_y_place = -(self.fgc_spacing_y - size_info.width) / 2
        specs = [
            i3.Place("fgc_1:opt1", (0, 0)),
            i3.PlaceRelative("fgc_2:opt1", "fgc_1:opt1", (0.0, self.fgc_spacing_y)),
            i3.PlaceRelative("fgc_3:opt1", "fgc_2:opt1", (0.0, self.fgc_spacing_y)),
            i3.PlaceRelative("fgc_4:opt1", "fgc_3:opt1", (0.0, self.fgc_spacing_y)),
            i3.PlaceRelative("rr:pin1", "fgc_3:opt1", (8.0, rel_y_place), angle=90),
        ]

        specs += [
            i3.ConnectManhattan(
                [
                    ("fgc_3:opt1", "rr:pin1"),
                    ("rr:pin4", "fgc_2:opt1"),
                    ("rr:pin2", "fgc_4:opt1"),
                    ("rr:pin3", "fgc_1:opt1"),
                ]
            ),
        ]
        return specs

    def _default_exposed_ports(self):
        exposed_ports = {
            "fgc_4:fib1": "drop",
            "fgc_3:fib1": "in",
            "fgc_2:fib1": "pass",
            "fgc_1:fib1": "add",
        }
        return exposed_ports


if __name__ == "__main__":

    # Layout
    ring_resonator = RingResonator(
        name="RR",
        bend_radius=5.0,
    )
    rr_layout= ring_resonator.Layout()
    rr_layout.visualize(annotate=True)
    rr_layout.visualize_2d()
    rr_layout.write_gdsii("ring_resonator.gds")

    # Circuit model
    my_circuit_cm = ring_resonator.CircuitModel()
    wavelengths = np.linspace(1.52, 1.58, 4001)
    S_total = my_circuit_cm.get_smatrix(wavelengths=wavelengths)

    # Plotting
    plt.plot(wavelengths, i3.signal_power_dB(S_total["pass:0", "in:0"]), "-", linewidth=2.2, label="Pass")
    plt.plot(wavelengths, i3.signal_power_dB(S_total["drop:0", "in:0"]), "-", linewidth=2.2, label="Drop")
    plt.plot(wavelengths, i3.signal_power_dB(S_total["add:0", "in:0"]), "-", linewidth=2.2, label="Add")
    plt.xlabel("Wavelength [um]", fontsize=16)
    plt.ylabel("Transmission [dB]", fontsize=16)
    plt.legend(fontsize=14, loc=4)
    plt.show()
