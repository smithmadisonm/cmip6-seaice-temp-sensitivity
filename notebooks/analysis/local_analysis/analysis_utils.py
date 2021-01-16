"""
Group of functions for analyzing sea ice and temperature CMIP6 output. 

Originated January 2021
Katie Brennan 
University of Washington
"""

import xarray as xr
import numpy as np
import pandas as pd
import scipy.stats as stats 
import os as os
import warnings
import matplotlib.pyplot as plt

def calc_tot_nh_siextent(siextent,areacello):
    """Finds total Arctic sea ice extent
       Inputs: 
       siextent = xarray DataArray (needs a 'latitude' coordinate)
       
       Outputs: 
       tot_nh_siextent = total nh sea ice extent (units = km^2)
    """
    if areacello.units == 'm2':
        areacello = areacello*1e-6
        areacello.attrs['units']='km2' 
        
    if len(areacello.shape)>2:
        areacello = areacello[0,:,:]

    tot_nh_siextent = (siextent*areacello)
    tot_nh_siextent = tot_nh_siextent.where(siextent['latitude']>0.0).sum(dim='j').sum(dim='i')
    
    tot_nh_siextent.attrs['units'] = 'km2'

    return tot_nh_siextent

def calc_siextent(siconc_in,cutoff):
    """Finds total Arctic sea ice extent
       Inputs: 
       siconc_in = 
       cutoff = Percent concentration to cutoff (%)
       
       Outputs: 
       si_extent
    """
    cut = cutoff/100
    if np.nanmax(siconc_in)>2.0:
        siconc_in = siconc_in/100

    siconc_in.where(np.logical_or(siconc_in>cut,siconc_in.isnull()),0.0)
    siextent = siconc_in.where(np.logical_or(siconc_in<=cut,siconc_in.isnull()),1.0)

    return siextent

def calc_arctic_mean(VAR,MIN_LAT):
    """Calculates area weighted Arctic mean: 
        Inputs: 
        VAR = Xarray DataArray variable with time dimension
        LAT = Xarray DataArray variable with latitude
        MIN_LAT = Minimum latitude to include in arctic mean 

        outputs: 
        var_armn = Area weighted Arctic mean
    """
    area_weight = np.cos(np.deg2rad(VAR.latitude))
        
    var_arsum = (VAR*area_weight).where(VAR['latitude']>=MIN_LAT).sum(dim=['i','j'])
    if len(VAR.latitude.shape) == 1:
        wt_sum = area_weight.where(VAR['latitude']>=MIN_LAT).sum(dim=['i'])*VAR.sizes['j']
    else: 
        wt_sum = area_weight.where(VAR['latitude']>=MIN_LAT).sum(dim=['i','j'])
        
    var_armn = var_arsum/wt_sum
    
    return var_armn

def scatter_linreg(varx,vary,data, months_in,model,plotflag=False):
    
    import calendar
    from scipy import stats
    import math
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
        airtemp_mi = varx.sel(time=data.time.dt.month.isin([mi]))
        extent_mi = vary.sel(time=data.time.dt.month.isin([mi]))
        extent_mi_nonans = extent_mi[np.logical_not(np.isnan(extent_mi))]
        airtemp_mi_nonans = airtemp_mi[np.logical_not(np.isnan(extent_mi))]
        
        monthname = calendar.month_name[mi]

        slope,intercept,r_value,_,_ = stats.linregress(airtemp_mi_nonans,extent_mi_nonans)
        slopes_all.append(slope)
        r_all.append(r_value)
        intercept_all.append(intercept)
        
        if plotflag == True:
            nmon = len(months_in)

            ax = fig.add_subplot(math.ceil(nmon/2.0),2,m+1)  
#            ax = fig.add_subplot(1,len(months_in),m+1)
            ax.scatter(airtemp_mi,extent_mi)
            ax.plot(airtemp_mi, intercept + slope*airtemp_mi, 'r')
            ax.set_title(monthname+', slope: %f , R$^2$: %f' % (slope,r_value**2))
            #print("slope: %f  " % (slope))
            ax.set_xlabel('Temp (K)')
            ax.set_ylabel('SIE (millions km$^2$)')
            fig.suptitle(model)

    if plotflag == True:
        plt.show()
        
    return slopes_all, r_all, intercept_all

def sub_arctic_plot(ax,fig,vec,lat,lon,maxv=-1,
                    minv=-1,colorbar=True,extent=True,cmap='RdBu_r'):
    if len(lat.shape)>1:
        nlat = lat.shape[0]
        nlon = lon.shape[1]
    else: 
        nlat = lat.shape[0]
        nlon = lon.shape[0]
        
    pdat = np.reshape(vec,[nlat,nlon])
                    
    if maxv == -1:
        maxv = np.nanmax(vec)
    if minv == -1:
        minv = -maxv                
           
#    pdat_wrap, lon_wrap = add_cyclic_point(pdat,coord=lon[0,:], axis=1)
#    new_lon2d, new_lat2d = np.meshgrid(lon_wrap, lat)
                    
    if extent is True: 
        ax.set_extent([-150, 140, 50, 90], crs=ccrs.PlateCarree())
    ax.gridlines(linestyle='--')
    ax.add_feature(cfeature.LAND, facecolor=(1, 1, 1))
    cs = ax.pcolormesh(lon, lat, vec, 
                       vmin=minv, vmax=maxv, cmap=cmap, 
                       transform=ccrs.PlateCarree())
    ax.coastlines(resolution='110m', linewidth=0.5)
    if colorbar is True:
        plt.colorbar(cs, ax=ax)
        
    return 

def global_plot(fig,ax,var,lat,lon,title,bound):
    var_new, lon1 = add_cyclic_point(var, coord=lon)
    new_lon, new_lat = np.meshgrid(lon1, lat)

    cs = ax.pcolormesh(new_lon, new_lat, var_new,
                       vmin=-bound,vmax=bound,cmap='RdBu_r',
                       transform=ccrs.PlateCarree())
#    plt.colorbar(cs, ax=ax)
    ax.coastlines(resolution='110m', linewidth=0.5)
    ax.set_title(title, fontsize=16)
    
    return cs

