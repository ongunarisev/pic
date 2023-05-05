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
exposed_port_names = {f"{key}:opt1": f"gc_{i:02d}" for i, key in enumerate(insts.keys(), start=1)}

# We instantiate Y-branch
y_branch = pdk.EbeamY1550()
# y_branch.Layout().visualize(annotate=True)

# Create the floor plan
floorplan = pdk.FloorPlan(name="FLOORPLAN", size=(605.0, 410.0))

# Connect the Y-branch to the input grating
insts.update({
    "yb_1": y_branch,
    "yb_2": y_branch,
    "yb_3": y_branch,
    "yb_4": y_branch,
    "yb_5": y_branch,
})

specs.extend([
    i3.Join(f"fgc_{input_port:02d}:opt1", "yb_1:opt1"),
    i3.ConnectManhattan("yb_1:opt2", "yb_2:opt1"),
    i3.ConnectManhattan("yb_1:opt3", "yb_3:opt1"),
    i3.PlaceRelative("yb_1:opt2", "yb_2:opt1", (-x_spacing, -y_spacing)),
    i3.PlaceRelative("yb_1:opt3", "yb_3:opt1", (-x_spacing, y_spacing)),
    i3.ConnectManhattan("yb_2:opt2", "yb_4:opt3"),
    i3.ConnectManhattan("yb_2:opt3", "yb_4:opt2"),
    i3.ConnectManhattan("yb_3:opt2", "yb_5:opt3"),
    i3.ConnectManhattan("yb_3:opt3", "yb_5:opt2"),
    i3.PlaceRelative("yb_2:opt2", "yb_4:opt1", (-2.5 * x_spacing, -y_spacing * 3)),
    i3.PlaceRelative("yb_3:opt3", "yb_5:opt1", (-2.5 * x_spacing, y_spacing * 3)),
    i3.ConnectManhattan("yb_4:opt1", "fgc_03:opt1"),
    i3.ConnectManhattan("yb_5:opt1", "fgc_01:opt1")]
)

# Add the floorplan to the instances dict and place it at (0.0, 0.0)
insts["floorplan"] = floorplan
specs.append(i3.Place("floorplan", (0.0, 0.0)))

# Form the circuit now

fgcirc = i3.Circuit(
    name="MZI_double_final",
    insts=insts,
    specs=specs,
    exposed_ports=exposed_port_names,
)

# This is the fourth stage of the circuit
fgcirc_layout = fgcirc.Layout()
fgcirc_layout.visualize(annotate=True)
fgcirc_layout.write_gdsii("GC_TE_couplers_w_MZI_1550nm.gds")
