# This is an advanced example on how to build Virtual Fabrication Process Flows.
# It's meant for PDK and library builders who want to include this process information
# in their technology. This way users of the PDK can with little effort export their
# components to 3rd party solvers.

import ipkiss3.all as i3
from pysics.basics.material.material import Material
from pysics.basics.material.material_stack import MaterialStack
from ipkiss.visualisation.display_style import DisplayStyle
from ipkiss.visualisation import color

dummy_mat = Material(name="dummy0_mat", epsilon=1, display_style=DisplayStyle(color=color.COLOR_SANGRIA))

# We'll have 4 material stacks
dummy_mstack0 = MaterialStack(
    name="dummy0", materials_heights=[(dummy_mat, 1.0)], display_style=DisplayStyle(color=color.COLOR_CHERRY)
)

dummy_mstack1 = MaterialStack(
    name="dummy1", materials_heights=[(dummy_mat, 2.0)], display_style=DisplayStyle(color=color.COLOR_DARK_GREEN)
)

dummy_mstack2 = MaterialStack(
    name="dummy2", materials_heights=[(dummy_mat, 3.0)], display_style=DisplayStyle(color=color.COLOR_GRAY)
)

dummy_mstack3 = MaterialStack(
    name="dummy3", materials_heights=[(dummy_mat, 0.5)], display_style=DisplayStyle(color=color.COLOR_MAGENTA)
)


# We'll use 3 Layers in our test structure
LAY0 = i3.Layer(0)
LAY1 = i3.Layer(1)
LAY2 = i3.Layer(2)

# and our technology uses 3 processes
PROCESS1 = i3.ProcessLayer(extension="ext1", name="dummyproc1")
PROCESS2 = i3.ProcessLayer(extension="ext2", name="dummyproc2")
PROCESS3 = i3.ProcessLayer(extension="ext3", name="dummyproc3")

vfab_flow = i3.VFabricationProcessFlow(
    active_processes=[PROCESS1, PROCESS2, PROCESS3],
    process_layer_map={
        # any of LAY0, LAY1 or LAY2 :
        PROCESS1: LAY0 | LAY1 | LAY2,
        # everwhere LAY1 or LAY2 :
        PROCESS2: (LAY1 & LAY2) | (LAY1 & LAY0) | (LAY2 & LAY0),
        # only when all layers are present:
        PROCESS3: LAY0 & LAY1 & LAY2,
    },
    process_to_material_stack_map=[
        ((0, 0, 0), dummy_mstack2),
        ((1, 0, 0), dummy_mstack0),  # mstack 0 where only 1 layer is present
        ((1, 1, 0), dummy_mstack1),  # mstack 1 where any combination of 2 layers is present
        ((1, 1, 1), dummy_mstack3),  # mstack 3 where all layers are present
    ],
    is_lf_fabrication={
        PROCESS1: False,
        PROCESS2: False,
        PROCESS3: False,
    },
)

# We make a Venn - Diagram like teststructure
lay = i3.LayoutCell().Layout(
    elements=[
        i3.Circle(layer=LAY0, center=(-3, 0), radius=5.0),
        i3.Circle(layer=LAY1, center=(3, 0), radius=5.0),
        i3.Circle(layer=LAY2, center=(0, 5), radius=5.0),
    ]
)

# We visualize the layers
lay.visualize()

# visualize_2d displays a top down view of the fabricated layout
lay.visualize_2d(vfabrication_process_flow=vfab_flow)

# we can also calculate and visualize the cross_section
lay.cross_section(i3.Shape([(-9, 3), (9, 3)]), process_flow=vfab_flow).visualize()
