"""This is a general purpose module containing routines
(a) that are used in multiple notebooks; or 
(b) that are complicated and would thus otherwise clutter notebook design.
"""

def AverageArctic_airtemperature(TAS_IN,MEMBER_IN):
    #select latitudes greater than 70N
    tas_Arctic = TAS_IN.sel(lat=slice(70,90))
    #average over lat and lon, assumes 
    ts_tas_ArcticAve = tas_Arctic[MEMBER_IN,:,:].mean(dim=['lat','lon'])
    return ts_tas_ArcticAve


def Arctic_SIextent(SICONC_IN,CELLAREA_IN,MEMBER_IN):
    #cell areas only where SI concentration greater than 15% - must be same shape/format!
    cellarea_extent = CELLAREA_IN[MEMBER_IN,:,:].where(SICONC_IN[MEMBER_IN,:,:,:]>.15)
    #sum area where SI conc > 15%
    ts_Arctic_extent = cellarea_extent.sum(dim=['nlat','nlon'])
    return ts_Arctic_extent

def scatter_tas_SIE_linreg(TAS_ARCTIC_IN,SIE_ARCTIC_IN,MONTHS_IN,PLOTFLAG):
    import calendar
    slopes_all = []
    r_all = []
    if PLOTFLAG == True:
        fig = plt.figure()
    for m,mi in enumerate(MONTHS_IN):
        CESM_airtemp_mi = TAS_ARCTIC_IN[mi::12].values
        CESM_extent_mi = extent_NH[mi::12].values
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

    if PLOTFLAG == True:
        plt.show()
    return slopes_all, r_all