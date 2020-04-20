"""
Does linear regression for sea ice extent and arctic temperature
"""

import calendar
import matplotlib.pyplot as plt
import math

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
        intercept_all.append(intercept)
        
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

def scatter_linreg(varx,vary,months_in,model,plotflag=False):
    """
    Calculates regression between two variables. 
    -------------------------------------
    INPUTS: 
    varx =      DataArray: (time, lat, lon) 
    vary =      DataArray: (time, lat, lon)  
    months_in = months of interest (list)
    plotflag =  show scatter plots
    model =     model name (string)
    -------------------------------------  
    OUTPUTS:
    slopes_all =    Slope between varx and vary for all models (list)
    r_all =         r-value between varx and vary for all models (list)
    intercept_all = intercept from regression between varx and 
                    vary for all models (list)
    """
    slopes_all = []
    r_all = []
    intercept_all = []
    
    if plotflag == True:
        fig = plt.figure(figsize=(12,5))
        
    #Select overlapping time intervals (hopefully, doesn't strictly check)    
    max_time = min(len(varx), len(vary))
    varx = varx.isel(time=slice(0,max_time))
    vary = vary.isel(time=slice(0,max_time))
    
    for m,mi in enumerate(months_in):
        print(mi)
        airtemp_mi = varx[mi::12]
        extent_mi = vary[mi::12]
        monthname = calendar.month_name[mi+1]

        slope,intercept,r_value,_,_ = stats.linregress(airtemp_mi,extent_mi/1e12)
        slopes_all.append(slope)
        r_all.append(r_value)
        intercept_all.append(intercept)
        
        if plotflag == True:
            nmon = len(months_in)

            ax = fig.add_subplot(math.ceil(nmon/2.0),2,m+1)  
#            ax = fig.add_subplot(1,len(months_in),m+1)
            ax.scatter(airtemp_mi,extent_mi/1e12)
            ax.plot(airtemp_mi, intercept + slope*airtemp_mi, 'r')
            ax.set_title(monthname+', slope: %f  ' % (slope))
            #print("slope: %f  " % (slope))
            ax.set_xlabel('Temp (K)')
            ax.set_ylabel('SIE (millions km$^2$)')
            fig.suptitle(model)

    if plotflag == True:
        plt.show()
        
    return slopes_all, r_all, intercept_all

# def plot_scatter(varx,vary,slopes,intercepts,r_value,nmonths)
#     fig = plt.figure(figsize=(12,5))       
#     ax = fig.add_subplot(1,len(months_in),m+1)
#     ax.scatter(airtemp_mi,extent_mi/1e12)
#     ax.plot(airtemp_mi, intercept + slope*airtemp_mi, 'r')
#     ax.set_title(monthname+', slope: %f  ' % (slope))
#     #print("slope: %f  " % (slope))
#     ax.set_xlabel('Temp (K)')
#     ax.set_ylabel('SIE (millions km$^2$)')
#     fig.suptitle(model)

#     if plotflag == True:
#         plt.show()