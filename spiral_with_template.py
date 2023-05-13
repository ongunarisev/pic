"""
Spiral with Tapered Waveguides and Spline Bends
===============================================

If you want to reduce losses you can use spline bends and broader waveguide for the straight sections.

"""

# Importing si_fab's technology and IPKISS

from si_fab import all as pdk
from ipkiss3 import all as i3
from picazzo3.wg.spirals import FixedLengthSpiral


##############################################################################
#
# Defining the Spline Rounding Algorithm
# --------------------------------------
#
# We use a rounding algorithm :py:class:`i3.SplineRoundingAlgorithm <ipkiss3.all.SplineRoundingAlgorithm>`
# that will result in Bezier bends
RA = i3.SplineRoundingAlgorithm(adiabatic_angles=(45, 45))

###############################################################################
#
# Defining the trace template
# --------------------------------------
#
# We take a basic template from the picazzo and derive a `RoundedWaveguideTemplate` version of it,
# which creates bends using a given rounding algorithm
#

wg_tmpl = pdk.SiWireWaveguideTemplate()
# Some parameters need to be defined in the Layout View
wg_tmpl.Layout(core_width=0.5)

wg_tmpl_r = i3.RoundedWaveguideTemplate(trace_template=wg_tmpl)
# Some parameters need to be defined in the Layout View
wg_tmpl_r.Layout(bend_radius=5.0, rounding_algorithm=RA)
###############################################################################
#
# Defining a spiral
# -----------------
# Now we build the spiral using the RoundedWaveguideTemplate.
# By using this specific trace template, the resulting generated waveguide will be of the
# :py:class:`i3.RoundedWaveguide <ipkiss3.all.TaperedWaveguide>` type.

spiral = FixedLengthSpiral(
    total_length=600.0,
    n_o_loops=1,
    trace_template=wg_tmpl_r,
)
spiral_lo = spiral.Layout(
    incoupling_length=5.0,
    spacing=5,
    stub_direction="H",  # either H or V
    growth_direction="H",
)

spiral_lo.visualize(annotate=True)
print("The length of the spiral is {} um".format(spiral_lo.trace_length()))
