# -*- coding: utf-8 -*-
"""
Created on Sat April 13 12:45:47 2019
TESS Convolution

@author: Team Convolve
"""

import numpy as np
#import matplotlib.pyplot as plt
#from astropy.table import Table
#from tabulate import tabulate
from scipy.stats import norm
from astropy.io import fits
from astropy.io import ascii
import time
import glob

start_time=time.time()

model = ascii.read("batmanCurves_small.csv", data_start=1, format='csv')
times = np.array(model['times'])

batman_curves = [] #np.zeros(5)

for i in range(0,len(model[0])-1):
    batman_curves.append(model['curve '+str(i)])


data = glob.glob('/common/contrib/classroom/ast520/tess_batman/data/TESS/Sector2/*.fits')

test=[]
sector = []
TIC = []
batman_indices = []

for i in data:
    
    fits_file = str(i)
    fits.info(fits_file)
    try:
        fits.getdata(fits_file, ext=1).columns
        with fits.open(fits_file, mode="readonly") as hdulist:
            hdr = hdulist[0].header
            sector.append(hdr[20])
            #identifier
            TIC.append(hdr[21])
            tess_bjds = hdulist[1].data['TIME']

            pdcsap_fluxes = hdulist[1].data['PDCSAP_FLUX']
    except Exception as e: 
        print(e, "file:",fits_file)
    pdcsap_fluxes[np.isnan(pdcsap_fluxes)] = 0
    tess_bjds[np.isnan(tess_bjds)] = 0

    #image = fits.open(str(i))
    #Read the exposure time from the header

    #flux2 is the lightcurve data
    #flux2 is the model
    max_array=np.zeros(len(batman_curves))

    for j in range(len(batman_curves)):
        column2 = np.pad(batman_curves[j], (len(tess_bjds)-len(batman_curves[j]),0), 'constant', constant_values=(1,1))
        Model_FFT=np.fft.fft(column2)

        TESS_FFT=np.fft.fft(pdcsap_fluxes)

        Product=(np.absolute(np.fft.ifft((Model_FFT)*(TESS_FFT))))
        Product[np.isnan(Product)] = 0
               
        MaxConvolution=Product.max(0)

        max_array[j]=MaxConvolution
        batman_indices.append(j)
        
    test.append(max_array)
    
test=np.asarray(test)
#print(batman_curves)
batman_curves = np.asarray(batman_curves)      
batman_indices = np.asarray(batman_indices)  
#print(batman_curves)
mu=np.zeros(len(test))
std=np.zeros(len(test))

batman_good = []

#plt.plot(test)
#plt.show()

##Write data to file
out_file = open('sample_candidates.txt', 'w')
line1 = 'sector' + ',' + 'tessFile' + ',' + 'curveID' + ',' + 'correlation' + '\n'

good=[]
for row in range(len(test)):
    
    mu, std = norm.fit(test[row])
    good.append(test[row][np.where(test[row] >= mu+3*std)])
    #print('values: ',test[row][0])
    #print('std: ', mu+3*std)
    #print('index: ',np.where(test[row] >= mu+1*std)[0])
    #plt.plot(test[row])
    #plt.show()
    
    batman_good.append(batman_indices[np.where(test[row] >= mu+3*std)])
good=np.asarray(good)  
batman_good=np.asarray(batman_good) 

try:
    for row in range(len(good)):
        for column in range(len(good[row]-1)):
            line =  str(sector[row]) + ',' + str(data[row]) + ',' + str(batman_good[row][column]) + ',' + str(good[row][column]) + '\n'
            out_file.write(line)
except IndexError:
    print('out of loop')
        
out_file.close()

#    plt.plot(max_array)
#    plt.show()
#    plt.plot(max_array[Good])
#    plt.show()
'''
table=Table([sector, data, batman_curves, good], names=('Sector', 'TESS_File', 'Curve_ID', 'Correlation'))
#
##Write data to file
f=open('Candidates.csv', 'w')
f.write(tabulate(data, headers=['Sector', 'TESS_File', 'Curve_ID', 'Correlation']))
f.close()
'''


        
   
  
'''  
#arrays for data (all # of columns)
sector = ['sample_sector0']
tessFile = ['HD_lsls.fits']
curveID = ['curve1']
correlation = ['99.322811332']

LN = 0

out_file = open('sample_candidates.csv', 'w')

line1 = 'sector' + ',' + 'tessFile' + ',' + 'curveID' + ',' + 'correlation' + '\n'

out_file.write(line1)

for i in sector:
    
        line =  sector[LN] + ',' + tessFile[LN] + ',' + curveID[LN] + ',' + correlation[LN] + '\n'
        LN += 1
        out_file.write(line)
        
out_file.close()
'''

end=time.time()

print(end-start_time)
