from ipkiss3 import all as i3
from ipkiss3.all.circuit_sim import polyval


class MMI1x3Model(i3.CompactModel):
    """Model for a 1x2 MMI.
    * center_wavelength: the center wavelength at which the device operates
    * reflection_in: polynomial coefficients relating reflection at the input port and wavelength
    * reflection_out: polynomial coefficients relating reflection at the output ports and wavelength
    * transmission: polynomial coefficients relating transmission and wavelength
    """

    parameters = [
        "center_wavelength",
        "reflection_in",
        "reflection_out",
        "transmission",
    ]

    terms = [
        i3.OpticalTerm(name="in1"),
        i3.OpticalTerm(name="out1"),
        i3.OpticalTerm(name="out2"),
        i3.OpticalTerm(name="out3"),
    ]

    def calculate_smatrix(parameters, env, S):
        reflection_in = polyval(parameters.reflection_in, env.wavelength - parameters.center_wavelength)
        reflection_out = polyval(parameters.reflection_out, env.wavelength - parameters.center_wavelength)
        transmission = polyval(parameters.transmission, env.wavelength - parameters.center_wavelength)
        S["in1", "out1"] = S["out1", "in1"] = transmission
        S["in1", "out2"] = transmission
        S["in1", "out3"] = S["in1", "out1"] = transmission
        S["in1", "in1"] = reflection_in
        S["out1", "out1"] = S["out3", "out3"] = reflection_out
        S["out2", "out2"] = reflection_out