import numpy as np
from scipy.stats import norm
from astropy.io import fits
from astropy.io import ascii
from astropy.table import Table, Column
import time
import glob
import os.path as p

def tconvolve(tess_dir,batman_dir, sector, start, end, output_dir, verbosity=0):
    """
    
    Parameters
    ----------
    tess_dir(str): directory to TESS data
    batman_dir (str): directory to model data
    sector (int): sector to pull data from
    start (int): file to start at
    end (int): file to end at
    output_dir (str): directory to write candidates.csv
    """
    start_time=time.time()
    
    model = ascii.read(p.join(batman_dir,"batmanCurves_small.csv"), 
                       data_start=1, format='csv')
    times = np.array(model['times'])

    batman_curves = model.columns[1:]
    
    if sector == 0:
        sector_name = "sample_Sector"+str(sector)
    else:
        sector_name = "Sector"+str(sector)
    sector_path = p.join(tess_dir, sector_name)
    sector_files = glob.glob(p.join(sector_path,"*.fits"))
#     print(p.join(sector_path,"*.fits"))
#     print(sector_files)

    data = sector_files[start:end]
    tess_names = []
    #batman_indices = []
    
    # output table

    for file_path in data:
        tess_file = p.basename(file_path)
        print(tess_file)

        try:
            fits.getdata(file_path, ext=1).columns
            with fits.open(file_path, mode="readonly") as hdulist:
                hdr = hdulist[0].header
                tess_names.append(tess_file)
                
                # get time and flux
                tess_bjds = hdulist[1].data['TIME']
                pdcsap_fluxes = hdulist[1].data['PDCSAP_FLUX']
        except Exception as e: 
            print(e, "file:",file_path)
        
        # set nans to 0
        pdcsap_fluxes[np.isnan(pdcsap_fluxes)] = 0
        tess_bjds[np.isnan(tess_bjds)] = 0

        # Do convolution
        max_array=np.zeros(len(batman_curves))
        tmax_array=np.zeros(len(batman_curves))
        for j, curvename in enumerate(batman_curves):
            # make batman same len at tess
            batman_flux_nopad = model[curvename]
            len_diff = len(tess_bjds)-len(batman_flux_nopad)
            batman_flux = np.pad(batman_flux_nopad, (len_diff, 0), 'constant', constant_values=(1,1))
            
            # run convolution
            batman_FFT=np.fft.fft(batman_flux)
            tess_FFT=np.fft.fft(pdcsap_fluxes)
            convolution=(np.absolute(np.fft.ifft((batman_FFT)*(tess_FFT))))
            
            # Save max conv value and time
            ind_max = np.argmax(convolution)
            tmax_array[j]= ind_max
            max_array[j] = convolution[ind_max]
            
        # Keep best curves
        mu, std = norm.fit(max_array)
        good_max = max_array[np.where(max_array >= mu+3*std)]
        # get curve ids for good_max
        # get times for good max
        num_good = len(good_max)
        print("Curve: {}, num good fits: {}".format(curvename, num_good))
        
        candidates = Table()
        candidates.add_column(Column([sector_name]*num_good), name="sector")
        candidates.add_column(Column([tess_file]*num_good), name="tessFile")
        #candidates.add_column(curvename, name="curveID")
        candidates.add_column(Column(good_max), name="correlation")
        #candidates.add_column(good_tmax, name="correlation")
        print(good_max)
        ascii.write(candidates, output_dir+'candidates.csv', 
                    format='csv', overwrite=True, comment='#')
        end=time.time()
        print(end-start_time)
    
        
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("tess_dir", type=str)
    parser.add_argument("batman_dir", type=str)
    parser.add_argument("sector", type=int)
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("output_dir", type=str)
    parser.add_argument("-v", "--verbosity", default=False, 
                        action="store_true", help="Print console output")
    args = parser.parse_args()
    tconvolve(args.tess_dir, args.batman_dir, args.sector, args.start, 
          args.end, args.output_dir, args.verbosity)
          
if __name__ == '__main__':
    main()