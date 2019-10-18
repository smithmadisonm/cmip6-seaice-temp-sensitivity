"""This is a general purpose module containing routines
(a) that are used in multiple notebooks; or 
(b) that are complicated and would thus otherwise clutter notebook design.
"""

import re
import socket
import xarray as xr
import intake
import matplotlib.pyplot as plt
import numpy as np

def rename_dimensions(DICT_IN, DICT_OUT):
    """Renames the dimensions of DICT_IN from whatever they were to 
       'j' and 'i'.
       inputs:  
            DICT_IN = dictionary 
            DICT_OUT = empty dictionary 
       outputs: 
            DICT_OUT = full dictionary with new dimension names
    """
    if 'x' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename(dict(x='j',y='i'))
    elif 'ni' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename(dict(nj='j',ni='i'))
    else: 
        DICT_OUT = DICT_IN
    return DICT_OUT

def find_overlap_models(VAR_LIST,EXP,TABLE_ID,MODEL_INTERSECT,COL):
    """Finds models that contain all the variables in VAR_LIST
       inputs: 
            VAR_LIST = list of variable names (list of (str))
            EXP = name of experiment (str)
            TABLE_ID = list of table ids associated with variable names (list of (str))
            MODEL_INTERSECT = 
            COL = output object of intake.open_esm_datastore 
       outputs: 
           MODEL_INTERSECT = list of models with all variables in VAR_LIST
    """
    for v,variable_id in enumerate(VAR_LIST):
        query = dict(experiment_id=EXP, table_id=TABLE_ID[v], 
                     variable_id=variable_id, grid_label='gn')  
        cat = COL.search(**query)
        MODEL_INTERSECT = MODEL_INTERSECT.intersection(
            {MODEL_INTERSECT for MODEL_INTERSECT in cat.df.source_id.unique().tolist()})

    # ensure the CESM2 models are not included (oxygen was erroneously submitted to the archive)
    # models = models - {'CESM2-WACCM', 'CESM2'}
    MODEL_INTERSECT = list(MODEL_INTERSECT)
    return MODEL_INTERSECT

def time_to_dt(VAR):
    """Defines a datetime variable and replaces time with datetime array. 
    """
    if len(VAR['time'].attrs) is 0:
        print('yes')
        return VAR['time']
    else: 
        attrs = {'units': VAR['time'].units}
        ds = xr.Dataset({'time': ('time', VAR.time.values, attrs)})
        var = xr.decode_cf(ds).time
        return var
    
def arctic_mean(VAR_DICT,VAR,MIN_LAT):
    ones_full = np.ones((VAR.isel(time=0,member_id=0).shape))
    area_weight = np.cos(np.deg2rad(VAR_DICT.lat)).expand_dims('lon',axis=1)*ones_full

    var_armn = (VAR*area_weight).sel(lat=slice(MIN_LAT,90)).sum(
        dim=['lat','lon'])/(area_weight.sel(lat=slice(MIN_LAT,90)).sum(dim=['lat','lon']))
    return var_armn

def AverageArctic_airtemperature(TAS_IN,MEMBER_IN):
    #select latitudes greater than 70N
    tas_Arctic = TAS_IN.sel(lat=slice(70,90))
    # Area weighting
    ones_full = np.ones((tas_dict[m].tas.isel(time=0,member_id=0).shape))
    area_weight = np.cos(np.deg2rad(tas_dict[m].lat)).expand_dims('lon',axis=1)*ones_full
    #average over lat and lon, assumes 
    ts_tas_ArcticAve = tas_Arctic[MEMBER_IN,:,:].mean(dim=['lat','lon'])
    return ts_tas_ArcticAve

def Arctic_SIextent(SICONC_IN,CELLAREA_IN,MEMBER_IN):
    #Find index for NH
    NH_ind = int(SICONC_IN['j'].shape[0]/2)
    #cell areas only where SI concentration greater than 15% - must be same shape/format!
    cellarea_extent = CELLAREA_IN[MEMBER_IN,NH_ind:,:].where(SICONC_IN[MEMBER_IN,:,NH_ind:,:]>15)
    #sum area where SI conc > 15%
    ts_Arctic_extent = cellarea_extent.sum(dim=['i','j'])
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

