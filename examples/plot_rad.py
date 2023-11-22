"""
Plot a rad file
===============

Get a rad file from PSG and plot it.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from pypsg.cfg.config import PyConfig
from pypsg import APICall
from pypsg import settings
from pypsg.rad import PyRad

CFG_PATH = Path(__file__).parent / 'psg_cfg.txt'

settings.save_settings(url=settings.INTERNAL_PSG_URL)
settings.reload_settings()

#%%
# Read the file
# ------------

pycfg = PyConfig.from_file(CFG_PATH)


#%%
# Run PSG
# -------

psg = APICall(pycfg,'rad')
out = psg()

#%%
# Read the response
# -----------------
rad = PyRad.from_bytes(out)

spec = rad.target

plt.plot(spec.spectral_axis,spec.flux)
plt.xlabel(spec.spectral_axis.unit)
plt.ylabel(spec.flux.unit)
0