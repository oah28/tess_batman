#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 11:47:23 2019

@author: CatherineClark
"""

from astropy.io import fits
from scipy.signal import find_peaks
import batman
import numpy as np
from scipy.stats import norm
import math
import pandas as pd

#define the batman parameters
def make_lightcurve(T0, RP, INC, PER, width, u_type, u_param, t):
    '''
    r: planet radius
    i: inclination
    per = orbital period
    width: "width parameter" a ** 3/per ** 2
    u_type: type of limb darkening
    u_param: list of parameters for limb darkening
    
    assume circular orbit
    '''
    params = batman.TransitParams()
    params.w = 0                  #longitude of periastron (in degrees)
    params.ecc = 0                #eccentricity
    params.t0 = T0                 #time of inferior conjunction
    params.rp = RP                 #planet radius (in units of stellar radii)
    params.inc = INC                #orbital inclination (in degrees)
    params.per = PER               #orbital period
    params.a = (width * PER ** 2) ** (1/3)                  #semi-major axis (in units of stellar radii)
    params.u = u_param            #limb darkening coefficients [u1, u2]
    params.limb_dark = u_type             #limb darkening model
    m = batman.TransitModel(params, t)    #initializes model
    flux = m.light_curve(params)          #calculates light curve
    return flux

def make_table(tess_dir, params_file, candidates_file):
    #read table
    params = pd.read_csv(params_file)
    candidates = pd.read_csv(candidates_file)
    candidates["curveID"] = candidates["curveID"].str.replace(" ", "")
    df = pd.merge(candidates, params, on = "curveID", how = "left")
    df.to_csv("merged.csv", index = False)
    #make empty chi-squared list
    chi_squared = np.zeros(len(df))
    for i, row in df.iterrows():
        fname = tess_dir + "/" + row["sector"] + "/" + row["tessFile"]
        #open fits file
        fits.info(fname)
        fits.getdata(fname, ext = 1).columns
        with fits.open(fname, mode = "readonly") as hdulist:
            tess_bjds = hdulist[1].data['TIME']
            pdcsap_fluxes = hdulist[1].data['PDCSAP_FLUX']
        #get params for this row
        T0 = row["tcorr"] - tess_bjds[0]
        RP = row["rp"]
        INC = row["i"]
        width = row["width"]
        #find the lightcurve minima to calculate the exoplanet period
        arr = pdcsap_fluxes / np.nanmedian(pdcsap_fluxes)
        arr[np.isnan(arr)] = np.nanmedian(arr)
        mu, std = norm.fit(1 / arr)
        peaks, _ = find_peaks(1 / arr, height = mu + 4 * std, distance = 1000)
        p = np.diff(tess_bjds[peaks])
        #define parameters
        PER = np.mean(p)
        u_type = 'quadratic'
        u_param = [0.1, 0.3]
        t = tess_bjds - tess_bjds[0]        
        #normalize flux
        fluxes_array = np.array(pdcsap_fluxes)
        outcounts = [i for i in fluxes_array if i >= np.mean(np.nan_to_num(fluxes_array))]
        mu, sigma = norm.fit(outcounts)
        normalized_fluxes = fluxes_array / mu
        normalized_sigma = np.array([math.sqrt(i) / mu for i in fluxes_array])        
        #calculate reduced chi-squared
        reduced_chi_squared = np.nansum(((normalized_fluxes - make_lightcurve(T0, RP, INC, PER, width, u_type, u_param, t)) ** 2 / normalized_sigma ** 2) / 8)
        #add reduced chi-squared values to list
        chi_squared[i] = reduced_chi_squared
    #add reduced chi-squared values to column in .csv file
    df["reduced chi-squared"] = chi_squared
    #write table
    df.to_csv("chisquared_values.csv")   

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("tess_dir", type=str)
    parser.add_argument("params_file", type=str)
    parser.add_argument("candidates_file", type=str)
    args = parser.parse_args()
    make_table(args.tess_dir, args.params_file, args.candidates_file)
          
if __name__ == '__main__':
    main()
