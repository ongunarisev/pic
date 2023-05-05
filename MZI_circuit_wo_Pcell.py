# Copyright (C) 2020 Luceda Photonics
# Modified by Ongun Arisev (ongunarisev@gmail.com)

from siepic import all as pdk
from ipkiss3 import all as i3
import pylab as plt

# The fiber spacing
f_spacing = 127  # microns
n_instances = 3  # We use a total of 3 fibers
input_port = 2  # Where is the input port

# We instantiate the fiber grating coupler.
fgc = pdk.EbeamGCTE1550()
# fgc.Layout().visualize(annotate=True)

# How many instances we are going to have
insts = {"{0}_{1:02d}".format(name, i): fgc for i, name in enumerate(n_instances * ["fgc"], start=1)}

# 5. We define specs, containing all the transformations that apply to each component.
specs = [i3.Place("{}:opt1".format(key), (0, 0 + i * f_spacing)) for i, key in enumerate(insts.keys())]

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
    "grating_array":  fgcirc
}

specs = [
    i3.Join("grating_array:gc_02", "yb_1:opt1"),
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

# Now moving onto the third stage which is adding two interferometers
insts = {
    "fgcirc_y": fgcirc_y,
    "yb_2": y_branch,
    "yb_3": y_branch,
}

specs = [
    # i3.PlaceRelative("yb_2:opt1", "fgcirc_y:yb1_1", (5, 10), angle=90),
    # i3.PlaceRelative("yb_3:opt1", "fgcirc_y:yb1_2", (5, -10), angle=-90),
    i3.Join("fgcirc_y:yb1_1", "yb_2:opt1"),
    i3.Join("fgcirc_y:yb1_2", "yb_3:opt1"),
    # i3.Place("yb_2:opt1", (20, 100)),
    # i3.Place("yb_3:opt1", (20, 160)),
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