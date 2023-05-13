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
# We take a basic template from the picazzo and derive a `TaperedWaveguideTemplate` version of it,
# which does two things:
#
# * flaring out to a different width, with a specified taper length and minimum lengths for the narrow and wider
#   waveguides.
# * creating bends using a given rounding algorithm
#

wg_tmpl = pdk.SiWireWaveguideTemplate()
wg_tmpl.Layout(
    core_width=0.450,
    cladding_width=2 * 2.0 + 0.45,
)

wg_tmpl_wide = pdk.SiRibWaveguideTemplate()
wg_tmpl_wide.Layout(core_width=0.85)

tapered_wg_tmpl = i3.TaperedWaveguideTemplate(
    name="tapered_wg_tmpl",
    trace_template=wg_tmpl,
    straight_trace_template=wg_tmpl_wide,
)

tapered_wg_tmpl.Layout(
    bend_radius=5.0,  # shortest radius of curvature in the bend
    rounding_algorithm=RA,  # use splines instead of circular arcs: smoother transition
    taper_length=10.0,  # length of the taper between the regular waveguide and the expanded waveguide
    # min_expanded_length=1.0, # minimum length of the expanded section. If shorter, don't expand
)

###############################################################################
#
# Defining a spiral
# -----------------
# Now we build the spiral using the TaperedWaveguideTemplate.
# By using this specific trace template, the resulting generated waveguide will be of the
# :py:class:`i3.TaperedWaveguide <ipkiss3.all.TaperedWaveguide>` type.

spiral = FixedLengthSpiral(
    total_length=4000.0,
    n_o_loops=4,
    trace_template=tapered_wg_tmpl,
)
spiral_lo = spiral.Layout(
    incoupling_length=10.0,
    spacing=6,
    stub_direction="V",  # either H or V
    growth_direction="V",
)

spiral_lo.visualize(annotate=True)
print("The length of the spiral is {} um".format(spiral_lo.trace_length()))
