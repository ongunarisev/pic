# Copyright (C) 2020 Luceda Photonics

from siepic import all as pdk
from ipkiss3 import all as i3
import numpy as np
import pylab as plt
from mzi_pcell_ybranch import MZI_YB


def define_control_point(delay_length_tuple, bend_radius, cp_y_tup):
    """Defines a control point based on the desired delay_length"""

    def f(x):
        device = MZI_YB(
            control_point1=(x[0], cp_y_tup[0]),
            control_point2=(x[1], cp_y_tup[1]),
            bend_radius=bend_radius,
        )
        mzi1_long_arm_length = device.get_connector_instances()[0].reference.trace_length()
        mzi1_short_arm_length = device.get_connector_instances()[1].reference.trace_length()
        mzi2_long_arm_length = device.get_connector_instances()[2].reference.trace_length()
        mzi2_short_arm_length = device.get_connector_instances()[3].reference.trace_length()
        mzi1_delay_length = mzi1_long_arm_length - mzi1_short_arm_length
        mzi2_delay_length = mzi2_long_arm_length - mzi2_short_arm_length
        cost1 = mzi1_delay_length - delay_length_tuple[0]
        cost2 = mzi2_delay_length - delay_length_tuple[1]
        cost = cost1**2 + cost2**2
        return np.abs(cost)

    from scipy.optimize import minimize

    cp_x_tup = minimize(f, x0=np.array([70.0, 70.0]), tol=1e-2).x
    return [(x , cp_y_tup[i]) for i, x in enumerate(cp_x_tup)]


# Parameters for the MZI sweep
delay_lengths = [(50.0, 100.0), (150.0, 200.0)]
bend_radius = 5.0
x0 = 40.0
y0 = 20.0
spacing_x = 180.0

insts = dict()
specs = []

# Create the floor plan for EdX design area
floorplan = pdk.FloorPlan(name="FLOORPLAN", size=(605.0, 410.0))

# Add the floor plan to the instances dict and place it at (0.0, 0.0)
insts["floorplan"] = floorplan
specs.append(i3.Place("floorplan", (0.0, 0.0)))

# Create the MZI sweep
for ind, delay_length in enumerate(delay_lengths):
    cp = define_control_point(
        delay_length_tuple=delay_length,
        bend_radius=bend_radius,
        cp_y_tup=(77, 177),
    )

    # Instantiate the MZI
    mzi = MZI_YB(
        name="MZI{}".format(ind),
        control_point1=cp[0],
        control_point2=cp[1],
        bend_radius=bend_radius,
    )

    # Calculate the actual delay length and print the results
    mzi1_long_arm_length = mzi.get_connector_instances()[0].reference.trace_length()
    mzi1_short_arm_length = mzi.get_connector_instances()[1].reference.trace_length()
    mzi2_long_arm_length = mzi.get_connector_instances()[2].reference.trace_length()
    mzi2_short_arm_length = mzi.get_connector_instances()[3].reference.trace_length()
    mzi1_delay_length = mzi1_long_arm_length - mzi1_short_arm_length
    mzi2_delay_length = mzi2_long_arm_length - mzi2_short_arm_length

    print(
        mzi.name,
        "Desired delay length = {} um".format(delay_length),
        "Actual delay length = {} um".format((mzi1_delay_length, mzi2_delay_length)),
        "Control points 1 = {}".format(cp[0]),
        "Control points 2 = {}".format(cp[1]),
    )

    # Add the MZI to the instances dict and place it
    mzi_cell_name = "mzi{}".format(ind)
    insts[mzi_cell_name] = mzi
    specs.append(i3.Place(mzi_cell_name, (x0, y0)))

    x0 += spacing_x

# Create the final design with i3.Circuit
cell = i3.Circuit(
    name="EBeam_Vesnog",
    insts=insts,
    specs=specs,
)

# Layout
cell_lv = cell.Layout()
cell_lv.visualize(annotate=True)
cell_lv.write_gdsii("EBeam_Vesnog_IPKISS.gds")

# Circuit model
cell_cm = cell.CircuitModel()
wavelengths = np.linspace(1.52, 1.58, 4001)
S_total = cell_cm.get_smatrix(wavelengths=wavelengths)

# Plotting
fig, axs = plt.subplots(2, sharex="all")

for ind, delay_length in enumerate(delay_lengths):
    tr_out1 = i3.signal_power_dB(S_total["mzi{}_out1:0".format(ind), "mzi{}_in:0".format(ind)])
    tr_out2 = i3.signal_power_dB(S_total["mzi{}_out2:0".format(ind), "mzi{}_in:0".format(ind)])

    axs[ind].plot(wavelengths, tr_out1, "-", linewidth=2.2, label="TE - MZI{}:out1".format(ind))
    axs[ind].plot(wavelengths, tr_out2, "-", linewidth=2.2, label="TE - MZI{}:out2".format(ind))

    axs[ind].set_ylabel("Transmission [dB]", fontsize=16)
    axs[ind].set_title("MZI{} - Delay length {} um".format(ind, delay_length), fontsize=16)
    axs[ind].legend(fontsize=14, loc=4)

axs[1].set_xlabel("Wavelength [um]", fontsize=16)
plt.show()

print("Done")
