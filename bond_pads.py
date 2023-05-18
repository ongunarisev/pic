from siepic import all as pdk
from ipkiss3 import all as i3
# https://docs.lucedaphotonics.com/guides/technology/
# The PDK does not have these layers, so I add them manually
i3.TECH.PROCESS.M1 = i3.ProcessLayer("Router", "M1")
i3.TECH.PROCESS.M2 = i3.ProcessLayer("Heater", "M2")
i3.TECH.PROCESS.M_open = i3.ProcessLayer("Bond Pad", "M_open")
# We make a copy of the layer dictionary to freely modify it
pplayer_map = dict(i3.TECH.GDSII.LAYERTABLE)
# Add the metal layers Proces Purpose layer
pplayer_map[i3.TECH.PROCESS.M1, i3.TECH.PURPOSE.DRAWING] = (11, 0)
pplayer_map[i3.TECH.PROCESS.M2, i3.TECH.PURPOSE.DRAWING] = (12, 0)
pplayer_map[i3.TECH.PROCESS.M_open, i3.TECH.PURPOSE.DRAWING] = (13, 0)
pplayer_m_open = i3.ProcessPurposeLayer(process=i3.TECH.PROCESS.M_open, purpose=i3.TECH.PURPOSE.DRAWING)
pplayer_m2 = i3.ProcessPurposeLayer(process=i3.TECH.PROCESS.M2, purpose=i3.TECH.PURPOSE.DRAWING)
pplayer_m1 = i3.ProcessPurposeLayer(process=i3.TECH.PROCESS.M1, purpose=i3.TECH.PURPOSE.DRAWING)

# Generate the wires for interconnects. These can be used with ConnectManhattan with rounding_algorithm set to None
wire_thickness = 10  # Wire thickness in microns
wire_template = i3.ElectricalWireTemplate()
wire_template.Layout(width=wire_thickness, layer=pplayer_m2)


class BondPad(i3.PCell):
    """200 nm TiW + 500 nm A,l bulk resistivity 0.04 uOhm*m, sheet resistance 0.07 Ohm / sq"""
    measurement_label_position = i3.Coord2Property(default=(0, 0), doc="Placement of automated measurement label")
    measurement_label_pretext = "elec_device_Vesnog_"
    class Layout(i3.LayoutView):
        size = i3.Size2Property(default=(75.0, 75.0), doc="Size of the bondpad")
        metal_layer = i3.LayerProperty(default=pplayer_m2, doc="Metal used for the bondpad")
        bond_pad_open_layer = i3.LayerProperty(default=pplayer_m_open, doc="Metal open used for the bondpad")

        def _generate_elements(self, elems):
            elems += i3.Rectangle(layer=self.metal_layer, box_size=self.size)
            elems += i3.Rectangle(layer=self.bond_pad_open_layer, box_size=self.size-(2.0, 2.0))
            return elems

        def _generate_ports(self, ports):
            ports += i3.ElectricalPort(
                name="e_out",
                position=(-self.size.x/2, 0.0),
                shape=(0, wire_thickness),
                process=self.metal_layer.process,
                angle=180,  # adding dummy angles so that the connector functions work
            )
            return ports


class Heater(i3.PCell):
    """200 nm TiW thickness, bulk resistivity 0.61 uOhm*m, sheet resistance 3.04 Ohm / sq"""
    class Layout(i3.LayoutView):
        size = i3.Size2Property(default=(4.0, 100.0), doc="Size of the heater")
        metal_layer = i3.LayerProperty(default=pplayer_m1, doc="Metal used for the heater")

        def _generate_elements(self, elems):
            elems += i3.Rectangle(layer=self.metal_layer, box_size=self.size)
            return elems

        def _generate_ports(self, ports):
            ports += i3.ElectricalPort(
                name="e_in2",
                position=(-self.size.x/2, self.size.y/2 - wire_thickness/2),
                shape=(0, 10),
                process=self.metal_layer.process,
                angle=0,  # adding dummy angles so that the connector functions work
            )
            ports += i3.ElectricalPort(
                name="e_in1",
                position=(-self.size.x/2, -self.size.y/2 + wire_thickness/2),
                shape=(0, 10),
                process=self.metal_layer.process,
                angle=0,  # adding dummy angles so that the connector functions work
            )
            return ports