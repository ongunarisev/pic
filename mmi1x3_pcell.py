# Copyright (C) 2020 Luceda Photonics

"""1x2 MMI
In this file, we are going to define the PCell for the 1x2 MMI.
Note: The circuit model in MMIWithCircuitModel uses the compact model defined in
si_fab/ipkiss/si_fab/compactmodels/all.py -> MMI1x2Model to extract the S-matrix of the 1x2 MMI.
"""

# Importing the technology and IPKISS
from si_fab import all as pdk
from ipkiss3 import all as i3
from mmi1x3_cm import MMI1x3Model
from simulate_camfr import *


# Building the MMI PCell with properties that describe its geometry
class MMI1x3(i3.PCell):
    """MMI with 1 input and 3 outputs."""

    _name_prefix = "MMI1x3"
    trace_template = i3.TraceTemplateProperty(doc="Trace template of the access waveguide")
    width = i3.PositiveNumberProperty(default=9.0, doc="Width of the MMI section.")
    length = i3.PositiveNumberProperty(default=20.0, doc="Length of the MMI secion.")
    taper_width = i3.PositiveNumberProperty(default=1.0, doc="Width of the taper.")
    taper_length = i3.PositiveNumberProperty(default=1.0, doc="Length of the taper")
    waveguide_spacing = i3.PositiveNumberProperty(default=2.0, doc="Spacing between the waveguides.")

    def _default_trace_template(self):
        return pdk.SiWireWaveguideTemplate()

    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            length = self.length
            width = self.width
            taper_length = self.taper_length
            taper_width = self.taper_width
            out_wg_sp = self.waveguide_spacing
            core_layer = self.trace_template.core_layer
            cladding_layer = self.trace_template.cladding_layer
            core_width = self.trace_template.core_width
            # Si core
            elems += i3.Rectangle(
                layer=core_layer,
                center=(0.5 * length, 0.0),
                box_size=(length, width),
            )
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(-taper_length, 0.0),
                end_coord=(0.0, 0.0),
                begin_width=core_width,
                end_width=taper_width,
            )
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(length, out_wg_sp),
                end_coord=(length + taper_length, out_wg_sp),
                begin_width=taper_width,
                end_width=core_width,
            )
            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(length, -out_wg_sp),
                end_coord=(length + taper_length, -out_wg_sp),
                begin_width=taper_width,
                end_width=core_width,
            )

            elems += i3.Wedge(
                layer=core_layer,
                begin_coord=(length, 0),
                end_coord=(length + taper_length, 0),
                begin_width=taper_width,
                end_width=core_width,
            )

            # Cladding
            elems += i3.Rectangle(
                layer=cladding_layer,
                center=(0.5 * length, 0.0),
                box_size=(length + 2 * taper_length, width + 2.0),
            )
            return elems

        def _generate_ports(self, ports):
            length = self.length
            taper_length = self.taper_length
            trace_template = self.trace_template

            ports += i3.OpticalPort(
                name="in1",
                position=(-taper_length, 0.0),
                angle=180.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="out1",
                position=(length + taper_length, self.waveguide_spacing),
                angle=0.0,
                trace_template=trace_template,
            )
            ports += i3.OpticalPort(
                name="out2",
                position=(length + taper_length, 0),
                angle=0.0,
                trace_template=trace_template,
            )

            ports += i3.OpticalPort(
                name="out3",
                position=(length + taper_length, -self.waveguide_spacing),
                angle=0.0,
                trace_template=trace_template,
            )

            return ports

    class Netlist(i3.NetlistFromLayout):
        pass

    class CircuitModel(i3.CircuitModelView):
        center_wavelength = i3.PositiveNumberProperty(doc="Center wavelength")
        transmission = i3.NumpyArrayProperty(doc="Polynomial coefficients, transmission as a function of wavelength")
        reflection_in = i3.NumpyArrayProperty(
            doc="Polynomial coefficients, reflection at input port as a function of wavelength"
        )
        reflection_out = i3.NumpyArrayProperty(
            doc="Polynomial coefficients, reflection at output ports as a function  of wavelength"
        )

        def _default_center_wavelength(self):
            raise NotImplementedError("Please specify center_wavelength")

        def _default_transmission(self):
            raise NotImplementedError("Please specify transmission")

        def _default_reflection_in(self):
            raise NotImplementedError("Please specify reflection_in")

        def _default_reflection_out(self):
            raise NotImplementedError("Please specify reflection_out")

        def _generate_model(self):
            return MMI1x3Model(
                center_wavelength=self.center_wavelength,
                transmission=self.transmission,
                reflection_in=self.reflection_in,
                reflection_out=self.reflection_out,
            )


if __name__ == "__main__":
    mmi = MMI1x3(
        trace_template=pdk.SiWireWaveguideTemplate(),
        width=6.0,
        length=15.0,
        taper_width=1.5,
        taper_length=4.0,
        waveguide_spacing=2,
    )
    mmi_layout = mmi.Layout()

    # 2. Visualize the layout and export to GDSII
    mmi_layout.visualize(annotate=True)
    mmi_layout.write_gdsii("mmi1x3.gds")

    # 3. Virtual fabrication and cross-section
    mmi_layout.visualize_2d(process_flow=pdk.TECH.VFABRICATION.PROCESS_FLOW_FEOL)
    mmi_layout.cross_section(
        cross_section_path=i3.Shape([(-0.5, -1.5), (-0.5, 1.5)]), process_flow=pdk.TECH.VFABRICATION.PROCESS_FLOW_FEOL
    ).visualize()

    wavelengths = np.arange(1.5, 1.6, 0.01)
    center_wavelength = 1.55
    print("Simulating...")
    sim_result = simulate_splitter_by_camfr(
        layout=mmi_layout,
        wavelengths=wavelengths,
        num_modes=20,
        north=0.5 * mmi_layout.size_info().get_height(),
        plot=True,
    )
    print("Done")

    pol_trans = np.polyfit(wavelengths - center_wavelength, sim_result[0], 7)
    pol_refl_in = np.polyfit(wavelengths - center_wavelength, sim_result[1], 7)
    # The value of pol_refl_out is not extracted from the CAMFR simulation but we assume it's the same as pol_refl_in
    pol_refl_out = pol_refl_in

    simulate_splitter_by_camfr(
        layout=mmi_layout,
        wavelengths=np.array([center_wavelength]),
        num_modes=20,
        north=0.5 * mmi_layout.size_info().get_height(),
        plot=True,
    )
