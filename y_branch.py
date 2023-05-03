from siepic import all as pdk
from ipkiss3 import all as i3
import numpy as np
import pylab as plt

splitter = pdk.EbeamY1550()

# 1. Layout
splitter_layout = splitter.Layout()
f=splitter_layout.visualize(annotate=True, show=False)
ax = f.axes[0]
ax.set_xlabel("$x(\mu m)$", fontdict={'fontsize':12, 'fontweight':'bold', 'color':'b'})
ax.set_ylabel("$y(\mu m)$", fontdict={'fontsize':12, 'fontweight':'bold', 'color':'b'})
splitter_layout.visualize_2d()
splitter_layout.cross_section(cross_section_path=i3.Shape([(-0.5, -1.5), (-0.5, 1.5)])).visualize()

# 2. Circuit
splitter_circuit = splitter.CircuitModel()

# 3. Plotting
wavelengths = np.linspace(1.52, 1.58, 51)
S = splitter_circuit.get_smatrix(wavelengths=wavelengths)
plt.plot(wavelengths, i3.signal_power_dB(S["opt2", "opt1"]), "-", linewidth=2.2, label="T(opt2)")
plt.plot(wavelengths, i3.signal_power_dB(S["opt3", "opt1"]), "-", linewidth=2.2, label="T(opt3)")
plt.plot(wavelengths, i3.signal_power_dB(S["opt2", "opt2"]), "-", linewidth=2.2, label="R(opt2)")
plt.plot(wavelengths, i3.signal_power_dB(S["opt3", "opt3"]), "-", linewidth=2.2, label="R(opt3)")
plt.ylim(-25.0, 0.0)
plt.xlabel("Wavelength [um]", fontsize=16)
plt.ylabel("Transmission [dB]", fontsize=16)
plt.legend(fontsize=14, loc=1)
plt.show()
