"""
Creating a Cell from an Existing GDSII file
===========================================

This sample illustrates how to import an existing GDSII file into a PCell, and assign ports and a circuit model to it.

There are cases when you want to integrate an existing old design into a new Ipkiss design, but
where only the GDSII output is available. Ipkiss can wrap this GDSII file into an Ipkiss cell,
and then you can manually add the ports, netlist and model so that you can use it into a larger circuit.


Note that all the layers used in the GDSII must first be defined in the Technology file.
This may not always be the case. (see example :ref:`Creating a Cell from an Existing GDSII file with a new Technology
<sphx_glr_examples_plot_gdsii_import_new_layers.py>`).


.. figure:: image_sources/import.png
    :width: 600px
    :align: center
    :alt: Import GDSII

    Importing from GDSII


.. rubric:: Illustrates

#. Write a Cell to a GDSII file
#. Import a GDSII file into an IPKISS component
#. Assign a CircuitModel to the imported component

"""


########################################################################
# Export a grating coupler to GDSII
# ---------------------------------
#
# We first write a fiber coupler to gdsii, so that we can import it again later.
# Note that all the layers used in the gdsii must be defined in the technology file.
#
# In this example we will use ``si_fab``, which is an example PDK shipped with Luceda Academy.

from si_fab import all as pdk  # noqa
from ipkiss3 import all as i3
import numpy as np
import pylab as plt

#########################################################################
# Then, we instantiate a grating coupler, and write it to ``my_grating.gds``:
#

from picazzo3.fibcoup.curved.cell import FiberCouplerCurvedGrating  # Here we use a fiber_coupler from Picazzo

my_grating = FiberCouplerCurvedGrating(
    name="unique_grating_name_used_in_GDSII"
)  # We give a unique name to the cell that will be used in the gdsii file.
my_grating_layout = my_grating.Layout()
my_grating_layout_ports = my_grating_layout.ports
my_grating_layout.visualize()
my_grating_layout.write_gdsii("my_grating.gds")

#########################################################################
# We now define a grating coupler simulation model. It is a simple gaussian model with a fixed reflection parameter
# (which is useful to model light that reflects back and forth in the circuit because of the grating coupler).
#


class GratingModel(i3.CompactModel):

    parameters = [
        "bandwidth_3dB",
        "peak_transmission",
        "center_wavelength",
        "reflection",
    ]

    terms = [
        i3.OpticalTerm(name="in"),
        i3.OpticalTerm(name="vertical_in"),
    ]

    def calculate_smatrix(parameters, env, S):
        sigma = parameters.bandwidth_3dB / 2.35482  # fwhm => sigma
        power_S = parameters.peak_transmission * np.exp(
            -((env.wavelength - parameters.center_wavelength) ** 2.0) / (2.0 * (sigma**2.0))
        )
        S["vertical_in", "in"] = S["in", "vertical_in"] = np.sqrt(power_S)
        S["in", "in"] = parameters.reflection


#########################################################################
# Importing the GDSII file
# ------------------------
#
# We use :py:class:`i3.GDSCell <ipkiss3.pcell.gdscell.GDSCell>` to import the GDSII file.
# In addition, we also
#
# * Assign it ports
# * Assign it a simulation model based on ``GratingModel`` that we defined in the code above.
#


class ImportedGrating(i3.GDSCell):
    def _default_filename(self):
        return "my_grating.gds"  # path to the gdsii file that contains the cell to be imported

    def _default_cell_name(self):
        return "unique_grating_name_used_in_GDSII"  # name of the cell to be imported inside the gdsii file.

    class Layout(i3.GDSCell.Layout):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(
                name="in",
                position=(20.0, 0.0),
                angle=0.0,
            )  # We have to manually set the ports as this info is not in the gdsii file yet
            ports += i3.VerticalOpticalPort(
                name="vertical_in",
                position=(0.0, 0.0),
                inclination=90.0,
                angle=0.0,
            )  # For the fiber a vertical port is used.

            return ports

    # Here we use our compact model. The netlist is automatically inferred from the layout.
    class CircuitModel(i3.CircuitModelView):

        center_wavelength = i3.PositiveNumberProperty(default=1.55, doc="center wavelength [um]")
        bandwidth_3dB = i3.PositiveNumberProperty(default=0.060, doc="3dB bandwidth [um]")
        peak_transmission = i3.NonNegativeNumberProperty(default=1.0, doc="peak transmission (0 to 1)")
        reflection = i3.ComplexFractionProperty(default=0.0, doc="Complex reflection back into the waveguide")

        def _generate_model(self):
            return GratingModel(
                center_wavelength=self.center_wavelength,
                bandwidth_3dB=self.bandwidth_3dB,
                peak_transmission=self.peak_transmission,
                reflection=self.reflection,
            )


##########################################################################
# Instantiate the imported cell with its Layout view
im_cell = ImportedGrating()
im_layout = im_cell.Layout()
im_layout.visualize()

##########################################################################
# Instantiate the CircuitModel view and do a simulation
wavelengths = np.arange(1.5, 1.6, 0.001)
im_caphemodel = im_cell.CircuitModel(bandwidth_3dB=0.1, peak_transmission=0.6)
S = im_caphemodel.get_smatrix(wavelengths=wavelengths)
plt.figure()
plt.plot(wavelengths, np.abs(S["in", "vertical_in"]) ** 2)
plt.show()


# sphinx_gallery_thumbnail_number = 1
