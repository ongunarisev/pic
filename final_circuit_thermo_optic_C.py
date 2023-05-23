# Copyright (C) 2020 Luceda Photonics
# Modified by Ongun Arisev to be used in the context of Silicon Photonics Design, Fabrication and Data Analysis EdX course

from siepic import all as pdk
from ipkiss3 import all as i3
from ipkiss3 import constants
from ipkiss.process.layer_map import GenericGdsiiPPLayerOutputMap
from ring_resonator_thermo_cell import RingResonatorThermo, pplayer_map
from datetime import datetime
import numpy as np
import pylab as plt

# Write the content to be written on WG_P6NM on Silicon layer directly
pplayer_map[i3.TECH.PROCESS.WG_P6NM, i3.TECH.PURPOSE.DRAWING] = pplayer_map[i3.TECH.PROCESS.WG, i3.TECH.PURPOSE.DRAWING]
output_layer_map = GenericGdsiiPPLayerOutputMap(pplayer_map=pplayer_map)

# Parameters for the MZI Y-branch sweep
parameters = [20.0, 50.0]
bend_radius = 5.0
x0 = 5.0
y0 = 2.5
x_spacing = 10
y_spacing = 10

insts = dict()
specs = []

# Create the floor plan for EdX design area
floorplan = pdk.FloorPlan(name="FLOORPLAN", size=(440.0, 470.0))

# Add the floor plan to the instances dict and place it at (0.0, 0.0)
insts["floorplan"] = floorplan
specs.append(i3.Place("floorplan", (0.0, 0.0)))
# Initialize the text label dictionary
text_label_dict = {}  # Text labels dictionary for automated measurement labels
circuit_cell_names = []  # Constituent circuit cell names list

# Create the ring resonator
rr_thermo = RingResonatorThermo(
    name="RR",
    bend_radius=5.0,
)

# Add the MZI to the instances dict and place it
rr_cell_name = "RRheater"
insts[rr_cell_name] = rr_thermo
size_info = rr_thermo.Layout().size_info()
x_pos = x0 + abs(size_info.west)
y_pos = y0 + abs(size_info.south)
specs.append(i3.Place(rr_cell_name, (x_pos, y_pos)))

# Put the measurement label for optical measurements
meas_label = f"{rr_thermo.measurement_label_pretext}{rr_cell_name}"
meas_label_coord = rr_thermo.measurement_label_position + (x_pos, y_pos)
text_label_dict[rr_cell_name] = [meas_label, meas_label_coord]
circuit_cell_names.append(rr_cell_name)

# Put the measurement label for electrical measurements
meas_label = f"{rr_thermo.bond_pad2.measurement_label_pretext}{rr_cell_name}_G"
meas_label_coord = rr_thermo.elec_meas_label_position + (x_pos, y_pos)
text_label_dict[f"{rr_cell_name}_e"] = [meas_label, meas_label_coord]

# # Place the next circuit to the right of GDS layout
# y0 += 250

# Create the final design with i3.Circuit
top_cell = i3.Circuit(
    name=f"EBeam_OngunArisev_thermo_C_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
    insts=insts,
    specs=specs,
)

# Bigger visualization
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['figure.dpi'] = 100


text_elems = []
# For the GDS text elements for automated measurement
for key, value in text_label_dict.items():
    text_label = value[0]
    text_label_coord = value[1]
    text_elems += i3.Label(layer=i3.TECH.PPLAYER.TEXT, text=text_label,
                          coordinate=text_label_coord,
                          alignment=(constants.TEXT.ALIGN.LEFT, constants.TEXT.ALIGN.BOTTOM), height=2)

# Layout
filename = "EBeam_heaters_Vesnog_C.gds"
cell_lv = top_cell.Layout()
cell_lv.append(text_elems)
cell_lv.visualize(annotate=True)
cell_lv.visualize_2d()
cell_lv.write_gdsii(filename, layer_map=output_layer_map)

print("Done")
