# Copyright (C) 2020 Luceda Photonics
# Modified by Ongun Arisev to be used in the context of Silicon Photonics Design, Fabrication and Data Analysis EdX course

from siepic import all as pdk
from ipkiss3 import all as i3
from ipkiss3 import constants
from ipkiss.process.layer_map import GenericGdsiiPPLayerOutputMap
from mzi_pcell_yb_thermo import MZI_YB_thermo, pplayer_map
from datetime import datetime
import numpy as np
import pylab as plt

# Write the content to be written on WG_P6NM on Silicon layer directly
pplayer_map[i3.TECH.PROCESS.WG_P6NM, i3.TECH.PURPOSE.DRAWING] = pplayer_map[i3.TECH.PROCESS.WG, i3.TECH.PURPOSE.DRAWING]
output_layer_map = GenericGdsiiPPLayerOutputMap(pplayer_map=pplayer_map)

# Parameters for the MZI Y-branch sweep
parameters = [50.0]
bend_radius = 5.0
x0 = 5.0
y0 = 5.0
x_spacing = 10
y_spacing = 10

insts = dict()
specs = []

# Create the floor plan for EdX design area
floorplan = pdk.FloorPlan(name="FLOORPLAN", size=(470.0, 440.0))

# Add the floor plan to the instances dict and place it at (0.0, 0.0)
insts["floorplan"] = floorplan
specs.append(i3.Place("floorplan", (0.0, 0.0)))
# Initialize the text label dictionary
text_label_dict = {}  # Text labels dictionary for automated measurement labels
circuit_cell_names = []  # Constituent circuit cell names list

# Create the MZI sweep for MZIs with Y-branches
for ind, parameter in enumerate(parameters, start=1):
    # Instantiate the MZI
    mzi_thermo = MZI_YB_thermo(
        name="MZI_thermo{}".format(ind),
        bend_radius=bend_radius,
    )

    # Add the MZI to the instances dict and place it
    mzi_cell_name = "MZIheater{}".format(ind)
    insts[mzi_cell_name] = mzi_thermo
    size_info = mzi_thermo.Layout().size_info()
    x_pos = x0 + abs(size_info.west)
    y_pos = y0 + abs(size_info.south)
    specs.append(i3.Place(mzi_cell_name, (x_pos, y_pos)))

    # Put the measurement label for optical measurements
    meas_label = f"{mzi_thermo.measurement_label_pretext}{mzi_cell_name}"
    meas_label_coord = mzi_thermo.measurement_label_position + (x_pos, y_pos)
    text_label_dict[mzi_cell_name] = [meas_label, meas_label_coord]
    circuit_cell_names.append(mzi_cell_name)

    # Put the measurement label for electrical measurements
    meas_label = f"{mzi_thermo.bond_pad2.measurement_label_pretext}{mzi_cell_name}_G"
    meas_label_coord = mzi_thermo.elec_meas_label_position + (x_pos, y_pos)
    text_label_dict[f"{mzi_cell_name}_e"] = [meas_label, meas_label_coord]
    # Place the next circuit to the right of GDS layout
    x0 += x_spacing + x_pos
    y0 += y_spacing + y_pos

# Create the final design with i3.Circuit
top_cell = i3.Circuit(
    name=f"EBeam_OngunArisev_thermo_A_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
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
filename = "EBeam_heaters_Vesnog.gds"
cell_lv = top_cell.Layout()
cell_lv.append(text_elems)
cell_lv.visualize(annotate=True)
cell_lv.visualize_2d()
cell_lv.write_gdsii(filename, layer_map=output_layer_map)

# Circuit model
cell_cm = top_cell.CircuitModel()
wavelengths = np.linspace(1.52, 1.58, 4001)
S_total = cell_cm.get_smatrix(wavelengths=wavelengths)

# Plotting
fig, axs = plt.subplots(4, sharex="all", figsize=(12, 18))

for ind, parameter in enumerate(parameters, start=1):
    # After the colon the mode is selected (two modes) / for the particular examples S-matrix has 12x12x2 entries
    # not counting the ones due to wavelength
    tr_out1 = i3.signal_power_dB(S_total["MZIyb{}_out1:0".format(ind), "MZIyb{}_in:0".format(ind)])
    tr_out2 = i3.signal_power_dB(S_total["MZIyb{}_out2:0".format(ind), "MZIyb{}_in:0".format(ind)])

    # Indices of the axes will be zero based
    ax_idx = ind - 1
    axs[ax_idx].plot(wavelengths, tr_out1, "-", linewidth=2.2, label="TE - MZI_YB{}:out1".format(ind))
    axs[ax_idx].plot(wavelengths, tr_out2, "-", linewidth=2.2, label="TE - MZI_YB{}:out2".format(ind))

    axs[ax_idx].set_ylabel("Transmission [dB]", fontsize=16)
    axs[ax_idx].set_title("MZI_YB{} - Delay length {} um".format(ind, parameter), fontsize=16)
    axs[ax_idx].legend(fontsize=14, loc=4)

axs[-1].set_xlabel("Wavelength [um]", fontsize=16)
plt.show()

print("Done")
