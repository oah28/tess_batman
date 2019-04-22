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
    print("Starting tconvolve...")
    
    # Read in TESS Sector data
    print("Reading TESS data...")
    sector_name = "Sector{}".format(sector)
    if sector == 0:
        sector_name = "sample_"+sector_name
    sector_path = p.join(tess_dir, sector_name)
    sector_files = glob.glob(p.join(sector_path,"*.fits"))
    tess_names = sector_files[start:end]
    print("Found {} TESS files to process".format(len(tess_names)))

    # Read in Batman Curves 
    print("Reading Batman transit curves...")
    batmanCurves = ascii.read(p.join(batman_dir,"batmanCurves_small.csv"), 
                       data_start=1, format='csv')
    times = np.array(batmanCurves['times'])
    curve_names = batmanCurves.columns[1:]
    print("Found {} Batman curves".format(len(curve_names)))
    
    # Do convolution on all tess files
    for tess_fpath in tess_names:
        tess_fname = p.basename(tess_fpath)
        print("Starting TESS file: {}".format(tess_fname))

        try:
            with fits.open(tess_fpath, mode="readonly") as hdulist:
                hdr = hdulist[0].header
                
                # get time and flux
                tess_time = hdulist[1].data['TIME']
                tess_flux = hdulist[1].data['PDCSAP_FLUX']
        except Exception as e: 
            print("ERROR reading file: ", tess_fpath, " with error: ", e)
            continue  # skip to next loop iter
        
        # set nans to 0
        tess_flux[np.isnan(tess_flux)] = 0
        tess_time[np.isnan(tess_time)] = 0

        # Do convolution on each batman curve
        max_array=np.zeros(len(curve_names))
        tmax_array=np.zeros(len(curve_names))
        print("Starting convolution...")
        for j, curvename in enumerate(curve_names):
            # make batman same len at tess
            batman_flux_nopad = batmanCurves[curvename]
            len_diff = len(tess_time)-len(batman_flux_nopad)
            batman_flux = np.pad(batman_flux_nopad, (len_diff, 0), 'constant', constant_values=(1,1))
            
            # run convolution
            batman_FFT=np.fft.fft(batman_flux)
            tess_FFT=np.fft.fft(tess_flux)
            convolution=(np.absolute(np.fft.ifft((batman_FFT)*(tess_FFT))))
            
            # Save max conv value and time
            ind_max = np.argmax(convolution)
            tmax_array[j]= ind_max
            max_array[j] = convolution[ind_max]
            
        # Keep best curves
        mu, std = norm.fit(max_array)
        idxs = np.where(max_array >= mu+3*std)
        convs = max_array[idxs]
        times = tmax_array[idxs]
        curves = curve_names[idxs]
        ncurves = len(curves)
        print("Found: {} fitting curves".format(ncurves))
        

        # Make table
        candidates = Table()
        candidates.add_column(Column([sector_name]*ncurves), name="sector")
        candidates.add_column(Column([tess_fname]*ncurves), name="tessFile")
        candidates.add_column(Columns(curves), name="curveID")
        candidates.add_column(Column(times), name="tcorr")
        candidates.add_column(Column(convs), name="correlation")
        
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