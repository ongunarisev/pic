# Copyright (C) 2020 Luceda Photonics
# Modified by Ongun Arisev (ongunarisev@gmail.com)

from siepic import all as pdk
from ipkiss3 import all as i3
import pylab as plt

### PARAMETERS

# Location of the bottom left grating
x_gc = 50
y_gc = 20

# The fiber spacing
f_spacing = 127  # microns
n_instances = 3  # We use a total of 3 fibers
input_port = 2  # Where is the input port

# The spacing between the first and second stage splitter
x_spacing = 15
y_spacing = 15


# We instantiate the fiber grating coupler.
fgc = pdk.EbeamGCTE1550()
# fgc.Layout().visualize(annotate=True)

# How many instances we are going to have
insts = {"{0}_{1:02d}".format(name, i): fgc for i, name in enumerate(n_instances * ["fgc"], start=1)}

# 5. We define specs, containing all the transformations that apply to each component.
specs = [i3.Place("{}:opt1".format(key), (x_gc, y_gc + i * f_spacing)) for i, key in enumerate(insts.keys())]

# 6. We define the names of the exposed ports that we want to access.
exposed_port_names = {f"{key}:opt1":f"gc_{i:02d}" for i, key in enumerate(insts.keys(), start=1)}

# We instantiate the i3.Circuit class to create the circuit, exposed ports are later used for other connectivity
fgcirc = i3.Circuit(
    name="GCs",
    insts=insts,
    specs=specs,
    exposed_ports=exposed_port_names,
)

# This is the first stage of the circuit
fgc_layout = fgcirc.Layout()
# fgc_layout.visualize(annotate=True)
# fgc_layout.write_gdsii("GC_TE_couplers_1550nm_array.gds")

# We instantiate Y-branch
y_branch = pdk.EbeamY1550()
# y_branch.Layout().visualize(annotate=True)

# Create the floor plan
floorplan = pdk.FloorPlan(name="FLOORPLAN", size=(605.0, 410.0))

# Connect the Y-branch to the input grating
insts = {
    "yb_1": y_branch,
    "fgcirc":  fgcirc
}

specs = [
    i3.Join(f"fgcirc:gc_{input_port:02d}", "yb_1:opt1"),
]


# Add the floorplan to the instances dict and place it at (0.0, 0.0)
insts["floorplan"] = floorplan
specs.append(i3.Place("floorplan", (0.0, 0.0)))

# Define the names of the exposed ports that we want to access.
exposed_port_names = {
    "yb_1:opt2": "yb1_1",
    "yb_1:opt3": "yb1_2",
}
#
fgcirc_y = i3.Circuit(
    name="GCs_ybranch",
    insts=insts,
    specs=specs,
    exposed_ports=exposed_port_names,
)

# This is the second stage of the circuit
fgcirc_y_layout = fgcirc_y.Layout()
fgcirc_y_layout.visualize(annotate=True)

# Now moving onto the third stage which is completing the circuit before MZI splitters

insts = {
    "fgcirc_y": fgcirc_y,
    "yb_2": y_branch,
    "yb_3": y_branch,
}

specs = [
    i3.ConnectManhattan("fgcirc_y:yb1_1", "yb_2:opt1"),
    i3.ConnectManhattan("fgcirc_y:yb1_2", "yb_3:opt1"),
    i3.PlaceRelative("fgcirc_y:yb1_1", "yb_2:opt1", (-x_spacing, -y_spacing)),
    i3.PlaceRelative("fgcirc_y:yb1_2", "yb_3:opt1", (-x_spacing, y_spacing)),

]


exposed_port_names ={
    "yb_2:opt2": "yb2_1",
    "yb_2:opt3": "yb2_2",
    "yb_3:opt2": "yb3_1",
    "yb_3:opt3": "yb3_2"
}

fgcirc_y2 = i3.Circuit(
    name="GCs_ybranch2",
    insts=insts,
    specs=specs,
    exposed_ports=exposed_port_names,
)

# This is the third stage of the circuit
fgcirc_y2_layout = fgcirc_y2.Layout()
fgcirc_y2_layout.visualize(annotate=True)

# Now moving onto the fourth stage putting the Y-branches acting as combiners and setting the path length difference
insts = {
    "fgcirc_y2": fgcirc_y2,
    "yb_4": y_branch,
    "yb_5": y_branch,
}

specs = [
    i3.ConnectManhattan("fgcirc_y2:yb2_1", "yb_4:opt3"),
    i3.ConnectManhattan("fgcirc_y2:yb2_2", "yb_4:opt2"),
    i3.ConnectManhattan("fgcirc_y2:yb3_1", "yb_5:opt3"),
    i3.ConnectManhattan("fgcirc_y2:yb3_2", "yb_5:opt2"),
    i3.PlaceRelative("fgcirc_y2:yb2_1", "yb_4:opt1", (-2.5 * x_spacing, -y_spacing*3)),
    i3.PlaceRelative("fgcirc_y2:yb3_2", "yb_5:opt1", (-2.5 * x_spacing, y_spacing*3)),
    # i3.FlipH("yb_4"),
    # i3.FlipH("yb_5")
]

exposed_port_names = {
    "yb_4:opt1": "out_mzi_1",
    "yb_5:opt1": "out_mzi_2"
}

fgcirc_y3 = i3.Circuit(
    name="GCs_ybranch3",
    insts=insts,
    specs=specs,
    exposed_ports=exposed_port_names,
)

# This is the fourth stage of the circuit
fgcirc_y3_layout = fgcirc_y3.Layout()
fgcirc_y3_layout.visualize(annotate=True)

# Moving onto the fifth and last stage of the circuit

insts = {
    "fgcirc_y3": fgcirc_y3,
    "fgcirc": fgcirc
}

specs = [
    i3.ConnectManhattan("fgcirc_y3:out_mzi_1", "fgcirc:gc_03"),
    i3.ConnectManhattan("fgcirc_y3:out_mzi_2", "fgcirc:gc_01"),
]

exposed_port_names = {}

fgcirc_y4 = i3.Circuit(
    name="GCs_ybranch_final",
    insts=insts,
    specs=specs,
    exposed_ports=exposed_port_names,
)

# This is the fourth stage of the circuit
fgcirc_y4_layout = fgcirc_y4.Layout()
fgcirc_y4_layout.visualize(annotate=True)
fgcirc_y4_layout.write_gdsii("GC_TE_couplers_w_MZI_1550nm.gds")
