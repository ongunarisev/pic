# Copyright (C) 2020 Luceda Photonics
# This version of Luceda Academy and related packages
# (hereafter referred to as Luceda Academy) is distributed under a proprietary License by Luceda
# It does allow you to develop and distribute add-ons or plug-ins, but does
# not allow redistribution of Luceda Academy  itself (in original or modified form).
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# For the details of the licensing contract and the conditions under which
# you may use this software, we refer to the
# EULA which was distributed along with this program.
# It is located in the root of the distribution folder.

from ipkiss3 import all as i3
from pysics.basics.material.material import Material

import camfr
import numpy as np
import pylab as plt


class LayoutSimulationWrapper(i3.PCell):
    child = i3.ChildCellProperty()

    class Layout(i3.LayoutView):
        simulation_box = i3.SizeInfoProperty()

        def _generate_instances(self, insts):
            insts += i3.SRef(self.child)
            return insts

        def _default_simulation_box(self):
            return self.child.size_info()

        def _generate_elements(self, elems):
            elems += i3.Rectangle(
                layer=i3.TECH.PPLAYER.DOC,
                center=self.simulation_box.center,
                box_size=(self.simulation_box.width, self.simulation_box.height),
            )
            return elems


def simulate_splitter_by_camfr(
    layout,
    wavelengths,
    num_modes=10,
    discretization_res=20,
    north=4.0,
    plot=True,
):
    """It simulates a symmetric splitter and returns the transmission and reflection.

    Parameters
    ----------
    layout : LayoutView
        Layout view of the splitter
    wavelengths: ndarray
        Wavelengths for the simulation in um
    num_modes : int, optional, default=10
        Number of modes
    discretization_res : int, optional, default=20
        Discretization resolution of the structure
    north : float, optional, default=4.0
        Northbound limit of the simulation
    plot : boolean, optional, default=True
        Plot the fields if True

    Returns
    -------
    trans_list, refl_list : list of floats, list of floats
        Transmission and reflection of the simulated component

    """
    trans_list = []
    refl_list = []
    for w in wavelengths:

        west = layout.ports["W0"].position.x
        east = layout.ports["E0"].position.x

        layout.simulation_box = i3.SizeInfo(west, east, north, -north)
        process_flow = i3.TECH.VFABRICATION.PROCESS_FLOW_FEOL  # Process flow for the virtual fabrication

        environment = i3.Environment(wavelength=w)

        # We compute the effective index for each material stack, which we then pass to
        # camfr_stack_expr_for_structure
        mat_stacks = i3.device_sim.get_material_stacks(layout, process_flow=process_flow)
        material_stack_to_material_map = dict()
        for ms in mat_stacks:
            neff = i3.device_sim.camfr_compute_stack_neff(ms, environment=environment, mode="TE0")
            material_stack_to_material_map[ms] = Material(
                name="effective_" + ms.name,
                epsilon=neff.real**2,
                n=neff.real,
            )

        # Now compose and simulate the MMI with the calculated effective indices
        camfr.set_lambda(w)
        camfr.set_N(num_modes)
        camfr.set_polarisation(camfr.TM)  # E-field in the plane
        camfr.set_upper_PML(-0.05)
        camfr.set_lower_wall(camfr.slab_E_wall)
        camfr.set_backward_modes(True)
        sim_window = i3.SizeInfo(
            west=west,
            east=east,
            south=-north,
            north=north,
        )

        stack_expr = i3.device_sim.camfr_stack_expr_for_structure(
            structure=layout,
            discretisation_resolution=discretization_res,
            window_size_info=sim_window,
            environment=environment,
            material_stack_to_material_map=material_stack_to_material_map,
            process_flow=process_flow,
        )
        camfr_stack = camfr.Stack(stack_expr)

        # Run the simulation

        # set incident field
        inc = np.zeros(camfr.N())
        inc[0] = 1
        camfr_stack.set_inc_field(inc)
        camfr.set_lower_wall(camfr.slab_E_wall)
        camfr_stack.calc()
        # camfr_stack.plot()

        if plot:

            # Create a coordinate mesh
            grid_step = 0.05
            x_coords = np.arange(0.0, sim_window.width, grid_step)
            y_coords = np.arange(0.0, sim_window.height, grid_step)
            x_mesh, y_mesh = np.meshgrid(x_coords, y_coords)

            #################
            # Extracting and plotting field profiles
            #################
            fields = np.ndarray(shape=np.shape(x_mesh), dtype=complex)
            for ix, x in enumerate(x_coords):
                for iy, y in enumerate(y_coords):
                    coord = camfr.Coord(y, 0.0, x)  # different coordinate system
                    fields[iy, ix] = camfr_stack.field(coord).H2()

            # Plot real part of fields with red-blue colormap

            ####################
            # Overlay refractive index on field plot
            ####################
            real_field = np.real(fields)
            limits = [-np.max(np.abs(real_field)), np.max(np.abs(real_field))]
            plt.contourf(x_mesh, y_mesh, real_field, 100, cmap="bwr")
            plt.clim(limits)
            plt.axis("image")
            plt.show()

        # Return the reflection and the transmission
        trans_list.append(abs(camfr_stack.T12(0, 0)) / (2.0**0.5))
        refl_list.append(abs(camfr_stack.R12(0, 0)))

    return trans_list, refl_list
