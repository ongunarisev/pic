# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
from ipkiss.process.layer_map import GenericGdsiiPPLayerOutputMap
from bond_pads import BondPad, Heater, pplayer_map, wire_template


class RingResonatorThermo(i3.Circuit):

    bend_radius = i3.PositiveNumberProperty(default=5.0, doc="Bend radius of the waveguides")
    fgc = i3.ChildCellProperty(doc="PCell for the fiber grating coupler")
    ring = i3.ChildCellProperty(doc="Ring resonator")
    fgc_spacing_y = i3.PositiveNumberProperty(default=127.0, doc="Fiber separation")
    measurement_label_position = i3.Coord2Property(doc="Placement of automated measurement label")
    measurement_label_pretext = "opt_in_TE_1550_device_Vesnog_"
    elec_meas_label_position = i3.Coord2Property(doc="Placement of automated measurement label for electrical interface")
    bond_pad_spacing_y = i3.PositiveNumberProperty(default=125.0, doc="Electrical bond pad separation")
    bond_pad_GC_dist = i3.PositiveNumberProperty(default=350.0, doc="Bond pad GC distance")
    bond_pad1 = BondPad(name="Bond_Pad_1")
    bond_pad2 = BondPad(name="Bond_Pad_2")
    bond_pad3 = BondPad(name="Bond_Pad_3")
    bond_pad4 = BondPad(name="Bond_Pad_4")
    ring_radius = i3.PositiveNumberProperty(default=20.0, doc="Ring resonator radius")
    coupler_length = i3.PositiveNumberProperty(default=0.5, doc="Coupling length")
    heater = Heater(name="Heater")

    def _default_elec_meas_label_position(self):
        return self.bond_pad2.measurement_label_position + (self.bond_pad_GC_dist, self.bond_pad_spacing_y)

    def _default_measurement_label_position(self):
        return 0.0, 2*self.fgc_spacing_y

    def _default_fgc(self):
        return pdk.EbeamGCTE1550()

    def _default_splitter(self):
        return pdk.EbeamY1550()

    def _default_dir_coupler(self):
        return pdk.EbeamBDCTE1550()

    def _default_ring(self):
        return pdk.EbeamAddDropSymmStraight(radius=self.ring_radius, coupler_length=self.coupler_length)

    def _default_insts(self):
        insts = {
            "fgc_1": self.fgc,
            "fgc_2": self.fgc,
            "fgc_3": self.fgc,
            "fgc_4": self.fgc,
            "rr": self.ring,
            "bp_1": self.bond_pad1,
            "bp_2": self.bond_pad2,
            "bp_3": self.bond_pad3,
            "bp_4": self.bond_pad4,
            "heater": self.heater,
        }
        return insts

    def _default_specs(self):
        size_info = self.ring.Layout().size_info()
        rel_y_place = -(self.fgc_spacing_y - size_info.width) / 2
        hl = self.heater.Layout(radius=self.ring_radius)
        rr_ly = self.ring.Layout()
        width = rr_ly.ports[2].y
        height = rr_ly.ports[3].x
        specs = [
            i3.Place("fgc_1:opt1", (0, 0)),
            i3.PlaceRelative("fgc_2:opt1", "fgc_1:opt1", (0.0, self.fgc_spacing_y)),
            i3.PlaceRelative("fgc_3:opt1", "fgc_2:opt1", (0.0, self.fgc_spacing_y)),
            i3.PlaceRelative("fgc_4:opt1", "fgc_3:opt1", (0.0, self.fgc_spacing_y)),
            i3.PlaceRelative("rr:pin1", "fgc_3:opt1", (8.0, rel_y_place), angle=90),
            i3.Place("bp_1", (self.bond_pad_GC_dist, 0)),
            i3.Place("bp_2", (self.bond_pad_GC_dist, self.bond_pad_spacing_y)),
            i3.Place("bp_3", (self.bond_pad_GC_dist, 2 * self.bond_pad_spacing_y)),
            i3.Place("bp_4", (self.bond_pad_GC_dist, 3 * self.bond_pad_spacing_y)),
            i3.PlaceRelative("heater", "rr:pin4", (width / 2, height / 2)),
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
            i3.ConnectManhattan("bp_1:e_out", "heater:e_in1", rounding_algorithm=None,
                                trace_template=wire_template, control_points=[i3.V(195)]),
            i3.ConnectManhattan("bp_2:e_out", "heater:e_in2", rounding_algorithm=None,
                                trace_template=wire_template, control_points=[i3.V(225)]),
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
    ring_resonator = RingResonatorThermo(
        name="RR",
        bend_radius=5.0,
    )
    rr_layout = ring_resonator.Layout()
    rr_layout.visualize(annotate=True)
    rr_layout.visualize_2d()
    output_layer_map = GenericGdsiiPPLayerOutputMap(pplayer_map=pplayer_map)
    rr_layout.write_gdsii("ring_resonator.gds", layer_map=output_layer_map)

    # # Circuit model
    # my_circuit_cm = ring_resonator.CircuitModel()
    # wavelengths = np.linspace(1.52, 1.58, 4001)
    # S_total = my_circuit_cm.get_smatrix(wavelengths=wavelengths)
    #
    # # Plotting
    # plt.plot(wavelengths, i3.signal_power_dB(S_total["pass:0", "in:0"]), "-", linewidth=2.2, label="Pass")
    # plt.plot(wavelengths, i3.signal_power_dB(S_total["drop:0", "in:0"]), "-", linewidth=2.2, label="Drop")
    # plt.plot(wavelengths, i3.signal_power_dB(S_total["add:0", "in:0"]), "-", linewidth=2.2, label="Add")
    # plt.xlabel("Wavelength [um]", fontsize=16)
    # plt.ylabel("Transmission [dB]", fontsize=16)
    # plt.legend(fontsize=14, loc=4)
    # plt.show()
