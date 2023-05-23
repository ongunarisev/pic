# Copyright (C) 2020 Luceda Photonics
# Modified by Ongun Arisev to be used in the context of Silicon Photonics Design, Fabrication and Data Analysis EdX course

from siepic import all as pdk
from ipkiss3 import all as i3
from ipkiss3 import constants
from ipkiss.process.layer_map import GenericGdsiiPPLayerOutputMap
from ring_resonator_cell import RingResonator
from ring_resonator_calib_cell import RingResonator_calib
from datetime import datetime
import numpy as np
import pylab as plt
from scipy.io import savemat, loadmat
import pickle


# We make a copy of the layer dictionary to freely modify it
pplayer_map = dict(i3.TECH.GDSII.LAYERTABLE)
# Write the content to be written on WG_P6NM on Silicon layer directly
pplayer_map[i3.TECH.PROCESS.WG_P6NM, i3.TECH.PURPOSE.DRAWING] = pplayer_map[i3.TECH.PROCESS.WG, i3.TECH.PURPOSE.DRAWING]
output_layer_map = GenericGdsiiPPLayerOutputMap(pplayer_map=pplayer_map)

# Parameter sweep for ring resonator
gap_array= np.arange(0.125, 0.26, 0.025)

bend_radius = 5.0
x0 = 3
y0 = 5.0
x_spacing = 5.0

insts = dict()
specs = []

# Create the floor plan for EdX design area
floorplan = pdk.FloorPlan(name="FLOORPLAN", size=(605.0, 410.0))

# Add the floor plan to the instances dict and place it at (0.0, 0.0)
insts["floorplan"] = floorplan
specs.append(i3.Place("floorplan", (0.0, 0.0)))
# Initialize the text label dictionary
text_label_dict = {}  # Text labels dictionary for automated measurement labels
circuit_cell_names = []  # Constituent circuit cell names list


# Create the sweep over resonator radius for ring resonators
for ind, gap in enumerate(gap_array, start=1):
    rr = pdk.EbeamAddDropSymmStraight(coupler_length=0.5, radius=20, gap=gap)
    # Instantiate the MZI
    rr = RingResonator(
        name="Ring_Resonator_rr{:.2f}".format(gap),
        ring=rr,
        bend_radius=bend_radius,
    )

    # Add the MZI to the instances dict and place it
    rr_cell_name = "RRcl{}".format(ind)
    insts[rr_cell_name] = rr

    # Put the measurement label
    meas_label = f"{rr.measurement_label_pretext}{rr_cell_name}"
    size_info = rr.Layout().size_info()
    x_pos = x0 + abs(size_info.west)
    y_pos = y0 + abs(size_info.south)
    specs.append(i3.Place(rr_cell_name, (x_pos, y_pos)))
    meas_label_coord = rr.measurement_label_position + (x_pos, y_pos)
    text_label_dict[rr_cell_name] = [meas_label, meas_label_coord]
    circuit_cell_names.append(rr_cell_name)

    # Place the next circuit to the right of GDS layout
    x0 += size_info.width + x_spacing

rr_cal = RingResonator_calib(
    name="Ring_Resonator_calibration",
    bend_radius=bend_radius,
)

# Add the calibration circuit to the instances dict and place it
rr_cell_name = "RRc"
insts[rr_cell_name] = rr_cal

# Put the measurement label
meas_label = f"{rr_cal.measurement_label_pretext}{rr_cell_name}"
size_info = rr_cal.Layout().size_info()
x_pos = x0 + abs(size_info.west)
y_pos = y0 + abs(size_info.south) + rr_cal.fgc_spacing_y
specs.append(i3.Place(rr_cell_name, (x_pos, y_pos)))
meas_label_coord = rr_cal.measurement_label_position + (x_pos, y_pos)
text_label_dict[rr_cell_name] = [meas_label, meas_label_coord]
circuit_cell_names.append(rr_cell_name)

# Create the final design with i3.Circuit
top_cell = i3.Circuit(
    name=f"EBeam_OngunArisev_G_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
    insts=insts,
    specs=specs,
)

# Bigger visualization
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['figure.dpi'] = 100


text_elems = []
# For the GDS text elements for automated measurement
for cell in circuit_cell_names:
    text_label = text_label_dict[cell][0]
    text_label_coord = text_label_dict[cell][1]
    text_elems += i3.Label(layer=i3.TECH.PPLAYER.TEXT, text=text_label,
                          coordinate=text_label_coord,
                          alignment=(constants.TEXT.ALIGN.LEFT, constants.TEXT.ALIGN.BOTTOM), height=2)

# Layout
filename = "EBeam_Vesnog_G.gds"
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
fig, axs = plt.subplots(gap_array.size, sharex="all", figsize=(12, 28))

# Dictionary for saving variables
m_dict = {}

for ind, gap in enumerate(gap_array, start=1):
    # After the colon the mode is selected (two modes) / for the particular examples S-matrix has 12x12x2 entries
    # not counting the ones due to wavelength
    circ = "RRcl{}".format(ind)
    tr_pass = i3.signal_power_dB(S_total["{}_pass:0".format(circ), "{}_in:0".format(circ)])
    tr_drop = i3.signal_power_dB(S_total["{}_drop:0".format(circ), "{}_in:0".format(circ)])
    tr_add = i3.signal_power_dB(S_total["{}_add:0".format(circ), "{}_in:0".format(circ)])

    # Indices of the axes will be zero based
    ax_idx = ind - 1
    axs[ax_idx].plot(wavelengths, tr_pass, "-", linewidth=2.2, label="TE - RR{}:pass".format(ind))
    axs[ax_idx].plot(wavelengths, tr_drop, "-", linewidth=2.2, label="TE - RR{}:drop".format(ind))
    axs[ax_idx].plot(wavelengths, tr_add, "-", linewidth=2.2, label="TE - RR{}:add".format(ind))

    axs[ax_idx].set_ylabel("Transmission [dB]", fontsize=16)
    axs[ax_idx].set_title("Ring resonator {0:d} - Resonator gap {1:.4f} um".format(ind, gap), fontsize=16)
    axs[ax_idx].legend(fontsize=14, loc=4)
    m_dict[f"RR_resonator_gap_{gap:.4f}"] = {"pass": tr_pass, "drop": tr_drop, "add": tr_add}

savemat(f'./data/RR_circuitG.mat', m_dict)
with open(f'./data/RR_circuitG.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump(m_dict, f)
axs[-1].set_xlabel("Wavelength [um]", fontsize=16)
plt.show()

print("Done")
