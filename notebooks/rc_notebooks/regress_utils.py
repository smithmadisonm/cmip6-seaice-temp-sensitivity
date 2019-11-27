"""
Does linear regression for sea ice extent and arctic temperature
"""

import calendar
import matplotlib.pyplot as plt
import numpy as np

from scipy import stats

def scatter_tas_SIE_linreg(TAS_ARCTIC_IN,SIE_ARCTIC_IN,MONTHS_IN,PLOTFLAG,MODEL):
    slopes_all = []
    r_all = []
    if PLOTFLAG == True:
        fig = plt.figure(figsize=(12,5))
    #Select overlapping time intervals (hopefully, doesn't strictly check)    
    max_time = min(len(TAS_ARCTIC_IN), len(SIE_ARCTIC_IN))
    TAS_ARCTIC_IN = TAS_ARCTIC_IN.isel(time=slice(0,max_time))
    SIE_ARCTIC_IN = SIE_ARCTIC_IN.isel(time=slice(0,max_time))
    for m,mi in enumerate(MONTHS_IN):
        CESM_airtemp_mi = TAS_ARCTIC_IN[mi::12].values
        CESM_extent_mi = SIE_ARCTIC_IN[mi::12].values
        monthname = calendar.month_name[mi+1]

        slope,intercept,r_value, p_value, std_err = stats.linregress(CESM_airtemp_mi,CESM_extent_mi/1e12)
        slopes_all.append(slope)
        r_all.append(r_value)
        
        if PLOTFLAG == True:
            ax = fig.add_subplot(1,len(MONTHS_IN),m+1)
            ax.scatter(CESM_airtemp_mi,CESM_extent_mi/1e12)
            ax.plot(CESM_airtemp_mi, intercept + slope*CESM_airtemp_mi, 'r')
            ax.set_title(monthname+', slope: %f  ' % (slope))
            #print("slope: %f  " % (slope))
            ax.set_xlabel('Temp (K)')
            ax.set_ylabel('SIE (millions km$^2$)')
            fig.suptitle(MODEL)

    if PLOTFLAG == True:
        plt.show()
    return slopes_all, r_all