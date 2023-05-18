from siepic import all as pdk
from ipkiss3 import all as i3
# https://docs.lucedaphotonics.com/guides/technology/
# The PDK does not have these layers, so I add them manually
i3.TECH.PROCESS.M1 = i3.ProcessLayer("Metal1", "M1")
i3.TECH.PROCESS.M2 = i3.ProcessLayer("Metal2", "M2")
# We make a copy of the layer dictionary to freely modify it
pplayer_map = dict(i3.TECH.GDSII.LAYERTABLE)
pplayer_map[i3.TECH.PROCESS.M1, i3.TECH.PURPOSE.DRAWING] = (11, 0)
pplayer_map[i3.TECH.PROCESS.M2, i3.TECH.PURPOSE.DRAWING] = (12, 0)
pplayer_m2 = i3.ProcessPurposeLayer(process=i3.TECH.PROCESS.M2, purpose=i3.TECH.PURPOSE.DRAWING)
pplayer_m1 = i3.ProcessPurposeLayer(process=i3.TECH.PROCESS.M1, purpose=i3.TECH.PURPOSE.DRAWING)


class BondPad(i3.PCell):
    class Layout(i3.LayoutView):
        size = i3.Size2Property(default=(75.0, 75.0), doc="Size of the bondpad")
        metal_layer = i3.LayerProperty(default=i3.ProcessPurposeLayer(process=i3.TECH.PROCESS.M2, purpose=i3.TECH.PURPOSE.DRAWING), doc="Metal used for the bondpad")

        def _generate_elements(self, elems):
            elems += i3.Rectangle(layer=self.metal_layer, box_size=self.size)
            return elems

        def _generate_ports(self, ports):
            ports += i3.ElectricalPort(
                name="m1",
                position=(0.0, 0.0),
                shape=self.size,
                process=self.metal_layer.process,
                angle=0,  # adding dummy angles so that the connector functions work
            )
            return ports
