# Batman Parameter File
LIGHTCURVE_TABLE = lc.csv
PARAMETERS_TABLE = param.csv
LOG_R_MIN  = -5
LOG_R_MAX  = -1
NUM_R_STEP = 16
LOG_W_MIN  = 0
LOG_W_MAX  = 5
NUM_W_STEP = 16

Above is an example of a parameter file for batman_monsoon.py. 
Keep the = sign in the same place, and make sure to put a ' '
space after each = sign otherwise the file will not read in
properly. 

Description of the variables: 

LIGHTCURVE_TABLE: name of the file where the lightcurves will
    be written
PARAMETERS_TABLE: name of the file where the light curve ids
    and corresponding parameters will be written
LOG_R_MIN: the log_10 of the minimum planet radius, in terms 
    of stellar radius
LOG_R_MAX: the log_10 of the maximum planet radius, in terms
    of stellar radius
NUM_R_STEP: number of log-spaced intervals at which to evaluate
    planet radius
LOG_W_MIN: the log_10 of the minimum width parameter, in terms 
    of stellar radius
LOG_W_MAX: the log_10 of the maximum width parameter, in terms
    of stellar radius
NUM_W_STEP: number of log-spaced intervals at which to evaluate
    width parameter
