from technologies import silicon_photonics  # noqa: F401
from picazzo3.fibcoup.curved import FiberCouplerCurvedGrating
from ipkiss3 import all as i3
import matplotlib.pyplot as plt


class BondPad(i3.PCell):
    class Layout(i3.LayoutView):
        size = i3.Size2Property(default=(50.0, 50.0), doc="Size of the bondpad")
        metal_layer = i3.LayerProperty(default=i3.TECH.PPLAYER.M1.LINE, doc="Metal used for the bondpad")

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

# Placing the components in a circuit
bp = BondPad()
bp_layout = bp.Layout(size=(50, 50))
gr = FiberCouplerCurvedGrating()

control_points = [(-40, 20), (50, 0), (100, -50)]

wire_template = i3.ElectricalWireTemplate()
wire_template.Layout(width=5.0, layer=bp_layout.metal_layer)

circuit = i3.Circuit(
    insts={"gr": gr, "gr2": gr, "b1": bp, "b2": bp},
    specs=[
        i3.Place("gr", position=(0, 0)),
        i3.Place("gr2", position=(100, 0)),
        i3.Place("b1", position=(-75, 0)),
        i3.Place("b2", position=(+150, 0)),
        i3.ConnectManhattan(
            "b1:m1",
            "b2:m1",
            control_points=control_points,
            rounding_algorithm=None,
            trace_template=wire_template,
        ),
    ],
)

circuit_layout = circuit.Layout()
circuit_layout.visualize(show=False)
plt.scatter([cp[0] for cp in control_points], [cp[1] for cp in control_points], c="C1", s=80, marker="x")
plt.show()