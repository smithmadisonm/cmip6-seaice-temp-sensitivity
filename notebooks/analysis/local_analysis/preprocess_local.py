"""
preprocess_local.py

This script loads in tas, sic and sit files from CMIP6 and cleans the data,
and calculates pan-Arctic quatitites (Arctic mean temp, total Arctic mean sea ice area, 
total Arctic mean sea ice extent and total Arctic mean sea ice volume). Then it saves
four netcdf files for each model one for: tas, sic, sit and pan_Arctic quantities with all 
the same coordinate and dimension names. 

Originated January 2021
Katie Brennan 
University of Washington
"""

import os, sys 
import numpy as np
import xarray as xr
import warnings
import matplotlib.pyplot as plt

import preprocess_utils as pputils
import analysis_utils as autils 

#--------------------------------------------------------------
#LISTS OF MODELS LEFT TO PREPROCESS: 
#--------------------------------------------------------------
models_historical_left = ['TaiESM1','AWI-ESM-1-1-LR','KIOST-ESM','NESM3']

models_picontrol_error = ['NESM3','KIOST-ESM','AWI-ESM-1-1-LR']

# These models have a datetime issue where the time object switches from a 
# timestamp to Proleptic Gregorian datatime object half way through...
models_picontrol_error_datetime =['EC-Earth3','MPI-ESM1-2-LR','EC-Earth3-Veg',
                                  'EC-Earth3-LR','MPI-ESM-1-2-HAM','MPI-ESM1-2-HR']

# HDF error: 
models_picontrol_error_HDF = ['ACCESS-ESM1-5','ACCESS-CM2']

# HDF error: 
models_ssp370_error_HDF = ['ACCESS-CM2','MPI-ESM1-2-HR']

models_ssp370_error = ['TaiESM1']
#'MPI-ESM1-2-HR' - permission denied 

#--------------------------------------------------------------
# USER PARAMETERS: 
#--------------------------------------------------------------
# models_to_process is a list of strings with models names
models_to_process = ['EC-Earth3','MPI-ESM1-2-LR','EC-Earth3-Veg',
                     'EC-Earth3-LR','MPI-ESM-1-2-HAM','MPI-ESM1-2-HR']

# exp can equal 'ssp370', 'piControl', or 'historical'
exp = 'piControl'

save_dir = ('/glade/work/mkbren/cmip6-data/cmip6-preprocessed/'+exp+'/')

# original location of files 
p = '/glade/scratch/mmsmith/CMIP6/cmip6_downloader/'

#--------------------------------------------------------------
# LET THE PREPROCESSING BEGIN...
#--------------------------------------------------------------
experiments = ['historical','piControl','ssp370']
variables = {'siconc':'SImon_', 'tas':'Amon_', 'sithick':'SImon_','areacella':'fx_','areacello':'Ofx_'}

# directory names in file structure files are originally saved in 
dirs = ['tas_mon_'+exp,'siconc_mon_'+exp,'sithick_mon_'+exp]

warnings.filterwarnings('ignore')

for mod in list(models_to_process):
    print('Working on '+ mod)
    data_out = xr.Dataset()
    data_siconc = xr.Dataset()

#    cellareao_mod, no_cellareao = find_cellareao_npy(mod)
#    cellareao_mod, no_cellareao = find_cellareao_local(mod)
    cellareao_mod, no_cellareao = pputils.find_cellareao_local_npy(mod)
    
    if no_cellareao is True: continue 
        
    variables_list = ['tas','siconc','sithick']

    for v,var in enumerate(variables_list):
        print("-------"+var+"-------")
        
        d = dirs[v]
        filename = var+'_'+variables[var]+mod+'_'+exp+'_r1i1p1f1_*.nc'

        data_save = xr.Dataset()
        
        data = xr.open_mfdataset(os.path.join(p,d,filename), concat_dim='time').load()
        data = pputils.rename_lat_lon(data)
        data = pputils.rename_dimensions(data, mod)
        
        if var == 'siconc':
            data = pputils.rename_lat_lon(data)

        if var is 'tas':
            print('Calculating tas indices...')
            print('1. Arctic mean tas')
            data_out['tas_arc_mean'] = autils.calc_arctic_mean(data.tas, 70)

            print('2. Arctic mean tas anomalies')
            data_out['tas_arc_mean_clim'] = data_out['tas_arc_mean'].groupby('time.month').mean(dim='time')
            data_out['tas_arc_mean_anom'] = data_out['tas_arc_mean'].groupby('time.month') -  data_out['tas_arc_mean_clim'] 
            
            data_save['tas'] = data['tas']
            save_name = mod+'_'+exp+'_tas_full_fields.nc'
            
            # If file already exists don't save: 
            if os.path.exists(os.path.join(save_dir,save_name)) is not True: 
                print('Writing netcdf file for tas.')
                data_save['tas'].encoding = {}
                data_save.to_netcdf(os.path.join(save_dir,save_name))

        elif var is 'siconc':
            print('Calculating siconc indices...')
            print('1. sea ice extent')
            data_out['siextent'] = autils.calc_siextent(data['siconc'],15)
            print('2. total arctic siextent')
            data_out['sie_arc_tot'] = autils.calc_tot_nh_siextent(data_out['siextent'],cellareao_mod.areacello)

            print('3. total arctic siextent anomalies')
            data_out['sie_tot_arc_clim'] = data_out['sie_arc_tot'].groupby('time.month').mean(dim='time')
            data_out['sie_tot_arc_anom'] = data_out['sie_arc_tot'].groupby('time.month') - data_out['sie_tot_arc_clim']
            
            data_siconc['siconc'] = data['siconc']
            data_save['siconc'] = data['siconc']
            save_name = mod+'_'+exp+'_siconc_full_fields.nc' 
            
            # If file already exists don't save: 
            if os.path.exists(os.path.join(save_dir,save_name)) is not True: 
                print('Writing netcdf file for siconc.')
                data_save['siconc'].encoding = {}
                data_save.to_netcdf(os.path.join(save_dir,save_name))

        elif var is 'sithick':
            print('Calculating sithick indices...')
            print('1. sea ice volume')
            data_out['sivolume'] = data.sithick*data_siconc.siconc*cellareao_mod.areacello
            print('2. Arctic mean sivolume')
            data_out['sivol_arc_mean'] = autils.calc_arctic_mean(data_out.sivolume, 70)

            print('3. Arctic mean sivolume anomalies')
            data_out['sivol_arc_mean_clim'] = data_out['sivol_arc_mean'].groupby('time.month').mean(dim='time')
            data_out['sivol_arc_mean_anom'] = data_out['sivol_arc_mean'].groupby('time.month') -  data_out['sivol_arc_mean_clim'] 
            
            data_save['sithick'] = data['sithick']
            save_name = mod+'_'+exp+'_sithick_full_fields.nc'
            
            # If file already exists don't save: 
            if os.path.exists(os.path.join(save_dir,save_name)) is not True: 
                print('Writing netcdf file for sithick.')
                data_save['sithick'].encoding = {}
                data_save.to_netcdf(os.path.join(save_dir,save_name))

        else:
            print('Variable not recognized')

        data_out = data_out.squeeze()

    save_name = mod+'_'+exp+'_siconc_sithick_tas_pan_arctic_fields.nc'
 
    # if os.path.exists(os.path.join(save_dir,save_name)) is not True: 
    print('Writing netcdf file for pan Arctic fields... \n')
    data_out.to_netcdf(os.path.join(save_dir,save_name))