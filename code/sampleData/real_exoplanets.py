# Compute the BATMAN transit curves of a few real exoplanets identified by TESS
# by Oriel Humes and Christian Tai Udovicic
import batman
from astropy.io import ascii
from astropy.table import Table, Column
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Read in data
cols = ['pl_name', 'pl_orbper', 'pl_orbincl', 'pl_orbeccen', 'pl_orbsmax',
        'pl_radj', 'st_rad']
planets = ascii.read('real_exoplanets.csv', include_names=cols)
planets['pl_orbeccen'][3] = 0

# Make a batmanParams astropy table from the relevent planets columns
batmanParams = planets[cols[:4]]
batmanParams.meta['comments']=[""]  # get rid of metadata

# rename batman columns in a unnecessarily fancy way
names = ['ID', 'per', 'inc', 'ecc']
for col, name in zip(cols, names):
    batmanParams.rename_column(col, name)

# Generate and add missing batman param columns (and fix units on rp and a)
t0 = Column(np.zeros(len(planets))) # set t0 to 0
rp = planets['pl_radj'] / (9.731 * planets['st_rad'])  # planet radius
a = planets['pl_orbsmax']*215/planets['st_rad']  # semi-major axis
w = Column(np.zeros(len(planets))) # set w to 0
u = Column(["0.1, 0.3"]*len(planets))
ld = Column(['quadratic']*len(planets))
batmanParams.add_column(t0, name='t0')
batmanParams.add_column(rp, name='rp')
batmanParams.add_column(a, name='a')
batmanParams.add_column(w, name='w')
batmanParams.add_column(u, name='u')
batmanParams.add_column(ld, name='limb_dark')

# Define a time array 
t = np.linspace(-10, 10, 1001)
transitCurves = Table()
transitCurves['t'] = t
for p in batmanParams: 
    # Init batman params
    params = batman.TransitParams()
    params.t0 = p['t0']  # time of inferior conjunction
    params.per = p['per']  # orbital period
    params.rp = p['rp']  # planet radius (in units of stellar radii)
    params.a = p['a']  # semi-major axis (in units of stellar radii)
    params.inc = p['inc']  # orbital inclination (in degrees)
    params.ecc = p['ecc']  # eccentricity
    params.w = p['w']  # longitude of periastron (in degrees)
    params.u = [float(val) for val in p['u'].split(',')]  # limb darkening coefficients [u1, u2]
    params.limb_dark = p['limb_dark']  # limb darkening model

    # Na-Na-Na-Na-Na-Na-Na-Na Na-Na-Na-Na-Na-Na-Na-Na
    m = batman.TransitModel(params, t)  # initializes model
    flux = m.light_curve(params)        # calculates light curve
    transitCurves[p['ID']] = flux
    plt.plot(t, flux)

# Generate batmanParams.csv and batmanCurves.csv
ascii.write(batmanParams, 'sample_batmanParams.csv', format='csv', overwrite=True, comment='#')
ascii.write(transitCurves, 'sample_batmanCurves.csv', format='csv', overwrite=True, comment='#')
plt.show()