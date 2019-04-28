import time
import glob
import os.path as p
import multiprocessing as mp
import numpy as np
from scipy.signal import fftconvolve
from astropy.io import ascii, fits
from astropy.table import Table, Column

def convolve(curves):
    """For parallel"""
    peak_times = np.zeros(len(curves))
    peak_convs = np.zeros(len(curves))
    for i,curve in enumerate(curves):
        batman_curve = batmanCurves[curve]
        conv = np.abs(fftconvolve(tess_flux, batman_curve, 'same'))
        ind_max = np.argmax(conv)
        peak_times[i] = tess_time[ind_max]
        peak_convs[i] = conv[idxs]

    # Return top 10
    idxs = peak_convs.argsort()[-10:]
    return peak_times[idxs], peak_convs[idxs]


def tconvolve(tess_dir, batman_dir, batman_suffix, sector, start, end, output_dir, nprocs, chunks, verbosity=0):
    """
    
    Parameters
    ----------
    tess_dir(str): directory to TESS data
    batman_dir (str): directory to model data
    batman_suffix(str): suffix to append to barmanCurves file (e.g. _small)
    sector (int): sector to pull data from
    start (int): file to start at
    end (int): file to end at
    output_dir (str): directory to write candidates.csv
    """
    
    tconv_start = time.time()
    print("===START TCONVOLVE===",flush=True)
    
    # Handle relative paths
    tess_dir = p.abspath(tess_dir)
    batman_dir = p.abspath(batman_dir)
    output_dir = p.abspath(output_dir)
    
    # Read in TESS Sector data
    print("Reading TESS data...")
    sector_name = "Sector{}".format(sector)
    if sector == 0:
        sector_name = "sample_"+sector_name
    sector_path = p.join(tess_dir, sector_name)
    sector_files = glob.glob(p.join(sector_path,"*.fits"))
    tess_names = sector_files[start:end]
    ntess = len(tess_names)
    print("Found {} TESS files to process".format(ntess),flush=True)

    # Read in Batman Curves 
    print("Reading Batman transit curves...")
    batmanCurves = ascii.read(p.join(batman_dir,"batmanCurves{}.csv".format(batman_suffix)), 
                       data_start=1, format='csv')
    times = np.array(batmanCurves['times'])
    curve_names = np.array(batmanCurves.colnames[1:])
    nbatman = len(curve_names)
    print("Found {} Batman curves".format(nbatman),flush=True)
    
    #Init dict for saving best batman curves 
    d = {key : [] for key in ['sector','tessFile','curveID','tcorr','correlation']}
    s = 0
    nerr = 0  # count number of failed files
    # Do convolution on all tess files
    for tind,tess_fpath in enumerate(tess_names):
        tess_fname = p.basename(tess_fpath)
        print("Starting TESS file: {}".format(tess_fname),flush=True)
        tess_start = time.time()

        try:
            with fits.open(tess_fpath, mode="readonly") as hdulist:
                hdr = hdulist[0].header
                tess_time = hdulist[1].data['TIME']
                tess_flux = hdulist[1].data['PDCSAP_FLUX']
        except Exception as e: 
            print("ERROR reading file: ", tess_fpath, " with error: ", e,flush=True)
            nerr += 1
            continue  # skip to next loop iter
        
        # clean tess lightcurve of nans
        med = np.nanmedian(tess_flux)
        tess_flux[np.isnan(tess_flux)] = med
        
        tmean = np.mean(tess_flux)
        tstd = np.std(tess_flux)
        tess_flux = (tess_flux - tmean)/tstd
        
        # PARALLEL
       # chunk = 100
       # chunks = [curve_names[i::chunk] for i in range(chunk)]
       # pool = mp.Pool(processes=nprocs)
       # peak_times, peak_convs = zip(*pool.map(convolve, chunks))

        # SEQUENTIAL Do convolution on each batman curve
        num_keep = 10
        curves = [""]*num_keep
        times = np.zeros(num_keep)
        convs = np.zeros(num_keep)
        conv_start = time.time()
        print("Starting convolutions...",flush=True)
        for curvename in curve_names:
            # run convolution
            # new way
            batman_curve = batmanCurves[curvename]
            conv = np.abs(fftconvolve(tess_flux, batman_curve, 'same'))
            ind_max = np.argmax(conv)
            conv_max = conv[ind_max]
            # Only keep if in top 10
            if conv_max > convs[-1]:
                # insert in reverse sorted order
                ind = np.searchsorted(-convs, -conv_max)
                curves = curves[:ind] + [curvename] + curves[ind:-1]
                times = np.insert(times, ind, tess_time[ind_max])[:-1]
                convs = np.insert(convs, ind, conv_max)[:-1]

        conv_time = time.time() - conv_start
        print("Convolved {} curves in {:.3} s".format(nbatman, conv_time),flush=True)
        
        # Save this TESS curve's best batman curves to dict
        d['sector'].extend([sector_name]*num_keep)
        d['tessFile'].extend([tess_fname]*num_keep)
        d['curveID'].extend(curves)
        d['tcorr'].extend(times)
        d['correlation'].extend(convs)

        # Make table every 100 tess curves
        if (tind % 10 == 0) or (tind == len(tess_names)-1):
            e = start+tind
            outname = 'candidates_sector{}_s{}_e{}.csv'.format(sector, s, e)
            outpath = p.join(output_dir, outname)
            # Convert to astropy table and write to csv
            candidates = Table(d,names=['sector','tessFile','curveID','tcorr','correlation'])
            ascii.write(candidates, outpath, format='csv', overwrite=True, comment='#')
            print("Wrote file {} at {} s".format(outname,time.time()-tess_start),flush=True)
            # reset dicts
            d = {key : [] for key in ['sector','tessFile','curveID','tcorr','correlation']}
            columnDict = {}
            s=e+1

    tconv_time = time.time() - tconv_start
    print("Convolved {}/{} tess files with {} curves in {:.3} s".format(ntess-nerr, ntess, nbatman, tconv_time),flush=True)
    print("===END TCONVOLVE===",flush=True)
    
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("tess_dir", type=str)
    parser.add_argument("batman_dir", type=str)
    parser.add_argument("sector", type=int)
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("output_dir", type=str) 
    parser.add_argument("batman_suffix",type=str,default="")
    parser.add_argument("nprocs", type=int)
    parser.add_argument("chunks", type=int)
    parser.add_argument("-v", "--verbosity", default=False, 
                        action="store_true", help="Print console output")
    args = parser.parse_args()
    tconvolve(args.tess_dir, args.batman_dir, args.batman_suffix, args.sector, args.start, 
          args.end, args.output_dir, args.nprocs, args.chunks, args.verbosity)
          
if __name__ == '__main__':
    main()
