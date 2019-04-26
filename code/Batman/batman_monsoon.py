import batman
from astropy.io import ascii
from astropy.table import Table, Column
import numpy as np

def make_lightcurve(r, i, width, u_type, u_param, t):
    '''
    r: planet radius (in stellar radii)
    i: inclination (in degrees)
    width: "width parameter" a**3/p**2
    u_type: type of limb darkening
    u_param: list of parameters for limb darkening
    
    t: timesteps that you want the fluxes at
    
    assume circular orbit
    '''
    params = batman.TransitParams()
    params.rp = r                 #planet radius (in units of stellar radii)
    params.inc = i                #orbital inclination (in degrees)
    params.w = 0                  #longitude of periastron (in degrees)
    params.ecc = 0                #eccentricity
    params.per = 100                #orbital period
    params.t0 = 0                 #time of inferior conjunction
    params.a = (width * 100**2)**(1/3)                  #semi-major axis (in units of stellar radii)
    params.u = u_param            #limb darkening coefficients [u1, u2]
    params.limb_dark = u_type             #limb darkening model
    m = batman.TransitModel(params, t)    #initializes model
    flux = m.light_curve(params)          #calculates light curve
    return flux


'''
PARAMETER RANGES:
r: 0.2 - 0.001
    16 intervals (logspaced)
i: from 90 to (np.arccos((1 + planet radius)/(semimajor axis*(1-ecc)))/(2 * np.pi) * 360) (all in units of stellar radii)
    10 intervals
w: 1 - 10**5
    16 intervals (logspaced)
Limb darkening: 
'''

#param = input('Enter name of the parameter file: ')


def make_batman(param):
   # read the parameter file
    with open(param, "r") as file: 
        data = file.readlines()
        lc_file = data[1][19:-1]
        pc_file = data[2][19:-1]
        r_min = float(data[3][13:-1])
        r_max = float(data[4][13:-1])
        r_step = float(data[5][13:-1])
        w_min = float(data[6][13:-1])
        w_max = float(data[7][13:-1])
        w_step = float(data[8][13:-1])
        
# this was a sanity check
# print(lc_file, pc_file, r_min, r_max, r_step, w_min, w_max, w_step)

# set up range of parameters

    potential_radii = np.logspace(r_min, r_max, r_step)
    potential_widths = np.logspace(w_min, w_max, w_step)
    radii = []
    widths = []
    incs = []
    for r in potential_radii:
        for w in potential_widths: 
            a = (w * (100)**2)**(1.0/3.0)
            lim = np.arccos((1 + r)/(a))/(2 * np.pi) * 360
            inc = np.linspace(90, lim, 10)
            for i in inc: 
                incs.append(i)
                radii.append(r)
                widths.append(w)
                
# set up file that will eventually become the curve id file
    batmanParams = Table([radii, incs, widths], names =('rp', 'i', 'width'))
    u = Column(['0.1 0.3']*len(batmanParams))
    ld = Column(['quadratic']*len(batmanParams))
    t0 = Column(np.zeros(len(batmanParams))) # set t0 to 0
    e = Column(np.zeros(len(batmanParams)))
    w = Column(np.zeros(len(batmanParams)))
    batmanParams.add_column(u, name='u')
    batmanParams.add_column(ld, name='ld')
    batmanParams.add_column(t0, name='t0')
    batmanParams.add_column(e, name='e')
    batmanParams.add_column(w, name='w')

# make an ID
    ID = Column(['curve{}'.format(i) for i in range(len(batmanParams))])
    batmanParams['curveID'] = ID

# actually generate the curves and add them to the curve file
    t = np.arange(-2.5, 2.5, 0.013889)
    batmanCurves = Table()
    batmanCurves['times'] = t
    for i in range(len(batmanParams)): 
        p = batmanParams[i]
        f = make_lightcurve(p['rp'], p['i'], p['width'], p['ld'], [float(val) for val in p['u'].split()], t)
        name = 'curve ' + str(i)
        batmanCurves[name] = f

            
# could do this seperately 

    ascii.write(batmanParams, pc_file, format='csv', overwrite=True, comment='#')
    ascii.write(batmanCurves, lc_file, format='csv', overwrite=True, comment='#')

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argment("-p", "--params", type=str)
    make_batman(param_file)

if __name__ == '__main__':
    main()