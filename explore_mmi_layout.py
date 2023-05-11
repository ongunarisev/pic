# Copyright (C) 2020 Luceda Photonics

"""1x2 MMI
In this file we are going to:
1. Import MMI1x2 from si_fab. This PCell contains an MMI with 1 input and 2 outputs.
2. Instantiate the layout of MMI1x2 and change its properties.

Note: The circuit model in MMIWithCircuitModel uses the compact model defined in
si_fab/ipkiss/si_fab/compactmodels/all.py -> MMI1x2Model to extract the S-matrix of the 1x2 MMI.
"""

# Importing the technology and IPKISS
from si_fab import all as pdk
from ipkiss3 import all as i3
from mmi2x2_pcell import MMI2x2

# 1. Instantiate the MMI
mmi = MMI2x2(
    trace_template=pdk.SiWireWaveguideTemplate(),
    width=5.0,
    length=15.0,
    taper_width=1.5,
    taper_length=4.0,
    waveguide_spacing=2.5,
)
mmi_layout = mmi.Layout()

# 2. Visualize the layout and export to GDSII
mmi_layout.visualize(annotate=True)
# mmi_layout.write_gdsii("mmi2x2.gds")

# 3. Virtual fabrication and cross-section
mmi_layout.visualize_2d(process_flow=pdk.TECH.VFABRICATION.PROCESS_FLOW_FEOL)
mmi_layout.cross_section(
    cross_section_path=i3.Shape([(-0.5, -1.5), (-0.5, 1.5)]), process_flow=pdk.TECH.VFABRICATION.PROCESS_FLOW_FEOL
).visualize()
