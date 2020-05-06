"""
Calculates basic Arctic and sea ice relevant quantities:
Examples: 
Arctic means
Totals Arctic sea ice extent
"""
import numpy as np
import calendar
import matplotlib.pyplot as plt
import math

from scipy import stats

def arctic_mean(VAR_DICT,VAR,MIN_LAT):
    """Calculates area weighted Arctic mean: 
        Inputs: 
        VAR_DICT = Xarray Dataset with latitude and longitude values
        VAR = Xarray DataArray variable with time dimension
        MIN_LAT = Minimum latitude to include in arctic mean 

        outputs: 
        var_armn = Area weighted Arctic mean
    """
    ones_full = np.ones((VAR.isel(time=0,member_id=0).shape))
    area_weight = np.cos(np.deg2rad(VAR_DICT.lat)).expand_dims('lon',axis=1)*ones_full

    var_arsum = (VAR*area_weight).sel(lat=slice(MIN_LAT,90)).sum(dim=['lat','lon'])
    var_armn = var_arsum/(area_weight.sel(lat=slice(MIN_LAT,90)).sum(dim=['lat','lon']))
    
    return var_armn

def calc_arctic_mean(VAR_DICT,VAR,MIN_LAT):
    """Calculates area weighted Arctic mean: 
        Inputs: 
        VAR_DICT = Xarray Dataset with latitude and longitude values
        VAR = Xarray DataArray variable with time dimension
        MIN_LAT = Minimum latitude to include in arctic mean 

        outputs: 
        var_armn = Area weighted Arctic mean
    """
    ones_full = np.ones((VAR.isel(time=0,member_id=0).shape))
    area_weight = np.cos(np.deg2rad(VAR_DICT.lat)).expand_dims('lon',axis=1)*ones_full

    var_arsum = (VAR*area_weight).where(VAR['lat']>=MIN_LAT).sum(dim=['i','j'])
    var_armn = var_arsum/(area_weight.where(VAR['lat']>=MIN_LAT).sum(dim=['lon','j']))
    
    return var_armn

def Arctic_SIextent(SICONC_IN,CELLAREA_IN,CUTOFF):
    """Finds total Arctic sea ice extent
       Inputs: 
       SICONC_IN = 
       CELLAREA_IN = cell area (time,lat,lon)
       CUTOFF = Percent concentration to cutoff
       
       Outputs: 
       ts_Arctic_extent = total Arctic sea ice extent
    """
    #Find index for NH
    NH_ind = int(SICONC_IN['j'].shape[0]/2)
    
    #cell areas only where SI concentration greater than CUTOFF - must be same shape/format!
    cellarea_extent = CELLAREA_IN[:,NH_ind:,:].where(SICONC_IN[:,:,NH_ind:,:]>CUTOFF)
    
    #sum area where SI conc > 15%
    ts_Arctic_extent = cellarea_extent.sum(dim=['i','j'])
    
    return ts_Arctic_extent

def calc_siextent(siconc_in,cutoff):
    """Finds total Arctic sea ice extent
       Inputs: 
       siconc_in = 
       cutoff = Percent concentration to cutoff (%)
       
       Outputs: 
       si_extent
    """
    cut = cutoff/100
    if siconc_in.max()>2.0:
        siconc_in = siconc_in/100

    siconc_in.where(np.logical_or(siconc_in>cut,siconc_in.isnull()),0.0)
    siextent = siconc_in.where(np.logical_or(siconc_in<=cut,siconc_in.isnull()),1.0)

    return siextent

def calc_tot_nh_siextent(siextent,areacello,model):
    """Finds total Arctic sea ice extent
       Inputs: 
       siextent = xarray DataArray (needs a 'latitude' coordinate)
       model = model name (str)
       
       Outputs: 
       tot_nh_siextent = total nh sea ice extent (units = km^2)
    """
    if areacello.units == 'm2':
        areacello = areacello*10e-6
        areacello.attrs['units']='km2' 
        
    if len(areacello.shape)>2:
        areacello = areacello[0,:,:]

    tot_nh_siextent = (siextent*areacello)
    tot_nh_siextent = tot_nh_siextent.where(siextent['latitude']>0.0).sum(dim='j').sum(dim='i')
    
    tot_nh_siextent.attrs['units'] = 'km2'

    return tot_nh_siextent

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
    model =     model name (string)
    plotflag =  show scatter plots
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
        print('month '+str(mi))
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


def add_text_plt(data,ncolor,nfont):
    """Adds text to a pre-existing pcolormesh plot. 
    
       Inputs: 
       data = data values to be printed (array)
       ncolor = color of font (str)
       nfont = fontsize for text 
    """
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            plt.text(x + 0.5, y + 0.5, '%.2f' % data[y, x],
                     horizontalalignment='center',
                     verticalalignment='center',color=ncolor, fontsize=nfont)
    return 

def get_cellareao(model): 
    """Gets the cellarea data for a given model. 
    """
    cellarea_path = ('/glade/work/mkbren/cmip6_sic/cmip6-seaice-temp-sensitivity'+
                     '/notebooks/analysis/Katie_analysis/cellareao/')
    filename = 'areacello_dict_hist_picontrol_ssp370.npy'
    
    data = np.load(cellarea_path+filename, allow_pickle='TRUE').item()
    
    return data[model]['areacello']