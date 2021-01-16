"""
Group of functions for parsing and processing CMIP6 output. 

Originated January 2021
Katie Brennan 
University of Washington
"""

import os, sys 
import numpy as np
import xarray as xr
import warnings

def get_directories(path):
    arr2 = os.listdir(path)
    directories = [i for i in arr2 if os.path.isdir(path+i)]
    return directories

def get_models(directories,variables, experiments,path):
    """
    INPUTS: 
    -------
    directories = list of strings of folder names with data 
    variables = dictionary: keys are strings of variable names 
                and objects are string of type of variables
    experiments = list of strings with experiments names as seen in directory and filenames
    
    OUTPUTS: 
    --------
    models = dictionary: keys are folder names (strings) and 
             objects are list of models contained (no repeats, strings)
    """
    models = {}
    for d in directories: 
        arr = os.listdir(path+d)
        var = [v for v in variables.keys() if v in d][0]
        exp = [v for v in experiments if v in d][0]
        mod = []
        for file in arr:
            end = file.find(exp)-1
            start = file.find(variables[var])+len(variables[var])
            mod.append(file[start:end])
        models[d] = set(mod)
    return models

def rename_dimensions(DICT_IN, mod):
    """
    Renames the dimensions of DICT_IN from whatever they were to 
       'j' and 'i'.
       inputs:  
            DICT_IN = dictionary 
            DICT_OUT = empty dictionary 
       outputs: 
            DICT_OUT = full dictionary with new dimension names
    """
    if 'x' in DICT_IN.dims:
        if mod in ['MIROC6','MRI-ESM2-0']:
            DICT_IN = DICT_IN.rename_dims(dict(x='j',y='i'))
        else: 
            DICT_IN = DICT_IN.rename_dims(dict(x='i',y='j'))
    elif 'ni' in DICT_IN.dims:
        DICT_IN = DICT_IN.rename_dims(dict(nj='j',ni='i'))
    elif 'nlon' in DICT_IN.dims:
        DICT_IN = DICT_IN.rename_dims(dict(nlat='i',nlon='j'))
    elif 'longitude' in DICT_IN.dims:
        DICT_IN = DICT_IN.rename_dims(dict(latitude='i',longitude='j'))
    elif 'lon' in DICT_IN.dims:
        DICT_IN = DICT_IN.rename_dims(dict(lat='i',lon='j'))
    return DICT_IN

def rename_lat_lon(DICT_IN):
    """
    Renames the dimensions of DICT_IN from whatever they were to 
       'latitude' and 'longitude'.
       inputs:  
            DICT_IN = dictionary 
            DICT_OUT = empty dictionary 
       outputs: 
            DICT_OUT = full dictionary with new dimension names
    """
    if 'latitude' in list(DICT_IN.coords):
        DICT_IN = DICT_IN
    elif 'latitude' in list(DICT_IN.data_vars):
        DICT_IN = DICT_IN.set_coords(['latitude','longitude'])
    elif 'lat' in list(DICT_IN.coords):
        DICT_IN = DICT_IN.rename({'lat':'latitude','lon':'longitude'})
    elif 'lat' in list(DICT_IN.data_vars):
        dict_out_temp = DICT_IN.rename({'lat':'latitude','lon':'longitude'})
        DICT_IN = dict_out_temp.set_coords(['latitude','longitude'])
    return DICT_IN

def load_cellarea(): 
    path = '/glade/work/mkbren/cmip6_sic/cmip6-seaice-temp-sensitivity/notebooks/analysis/Katie_analysis/cellareao/'
    hist_area_data = np.load(os.path.join(path,'dset_dict_historical_areacello_.npy'), allow_pickle='TRUE').item()
    pi_area_data = np.load(os.path.join(path,'dset_dict_piControl_areacello_.npy'), allow_pickle='TRUE').item()
    ssp_area_data = np.load(os.path.join(path,'dset_dict_ssp370_areacello_.npy'), allow_pickle='TRUE').item()
    
    cellareao = {}
    cellareao=hist_area_data['areacello']
    cellareao2={i: v for i,v in pi_area_data['areacello'].items() if i not in cellareao}
    cellareao = {**cellareao, **cellareao2}
    cellareao3={i: v for i,v in ssp_area_data['areacello'].items() if i not in cellareao}
    cellareao = {**cellareao, **cellareao3}
    
    return cellareao

def find_cellareao_npy(mod):
    cellareao = load_cellarea()
    
    lmod = len(mod)
    found = False
    
    print('Looking for cellarea file...')
    no_cellareao=False
    if mod in cellareao:
        cellareao_mod = cellareao[mod]
        print('cellareao found!')
        found = True
    else: 
        for m in cellareao.keys():
            try:
                test = m.index(mod[:lmod])
                if test>0: 
                    continue
                else: 
                    cellareao_mod = cellareao[m]
                    print('Using cellareao file from '+str(m))
                    break

            except ValueError as e: 
                if m is list(cellareao.keys())[-1]:
                    print('Skipping model '+mod+' because no cell area file - KeyError: "%s"' % str(e))
                    no_cellareao = True
                    cellareao_mod = np.nan
                    break 
                    
    return cellareao_mod, found, no_cellareao

def find_cellarea_files_local():
    cellarea_path = '/glade/scratch/rclancy/CMIP6/'
    cellarea_dirs = ['areacella','areacello']

    areacella_files = os.listdir(os.path.join(cellarea_path,cellarea_dirs[0]))
    areacello_files = os.listdir(os.path.join(cellarea_path,cellarea_dirs[1]))
    areacella_files.remove('.ipynb_checkpoints')

    areacello_models_local = [d[14:-15].split('_')[0] for d in areacello_files]
    areacella_models_local = [d[13:-15].split('_')[0] for d in areacella_files]

    areacella_models = list(set(areacella_models_local) - set(areacello_models_local))
    
    return areacello_files,areacella_files,areacella_models

def find_cellareao_local(mod):
    lmod = len(mod)
    print('Looking for cellarea file...')
    no_cellareao=False
    
    [areacello_files,areacella_files,areacella_models] = find_cellarea_files_local()
    
    if mod in areacella_models: 
        for file in areacella_files: 
            if mod in file: 
                cellareao_filename = file
                cellarea_path = '/glade/scratch/rclancy/CMIP6/areacella'
                print('areacella file found!')
                

    else:
        if mod in areacello_files: 
            cellareao_filename = file
            cellarea_path = '/glade/scratch/rclancy/CMIP6/areacello'
            print('areacello file found!')

        else: 
            for m in areacello_files:
                try:
                    test = m[14:].index(mod[:lmod])
                    if test>0: 
                        continue
                    else: 
                        cellareao_filename = m
                        cellarea_path = '/glade/scratch/rclancy/CMIP6/areacello'
                        print('Using areacello file from '+str(m))
                        break

                except ValueError as e: 
                    if m is list(areacello_files)[-1]:
                        print('Skipping model '+mod+' because no cell area file - KeyError: "%s"' % str(e))
                        no_cellareao = True
                        cellarea_path = 'None'
                        cellareao_mod = np.nan
                        break 
                            
    cellareao_data = xr.open_dataset(os.path.join(cellarea_path,cellareao_filename)).load()

    if 'areacella' in list(cellareao_data.data_vars):
        cellareao_data = cellareao_data.rename_vars({'areacella':'areacello'})

    cellareao_mod = cellareao_data
    cellareao_mod = rename_lat_lon(cellareao_mod)
    cellareao_mod = rename_dimensions(cellareao_mod, mod)
                            
    return cellareao_mod, no_cellareao

def find_cellareao_local_npy(mod):
    lmod = len(mod)
    print('Looking for cellarea file...')
    no_cellareao=False
    found_full = True 
    
    [areacello_files,areacella_files,areacella_models] = find_cellarea_files_local()

    if mod in areacella_models: 
        for file in areacella_files: 
            if mod in file: 
                cellareao_filename = file
                cellarea_path = '/glade/scratch/rclancy/CMIP6/areacella'
                print('areacella file found!')


    elif mod in areacello_files:
        for file in areacella_files: 
            if mod in file:
                cellareao_filename = file
                cellarea_path = '/glade/scratch/rclancy/CMIP6/areacello'
                print('areacello file found!')

    else: 
        found_full = False
        for m in areacello_files:
            try:
                test = m[14:].index(mod[:lmod])
                if test>0: 
                    continue
                else: 
                    cellareao_filename = m
                    cellarea_path = '/glade/scratch/rclancy/CMIP6/areacello'
                    break

            except ValueError as e: 
                if m is list(areacello_files)[-1]:
                    print('Skipping model '+mod+' because no cell area file - KeyError: "%s"' % str(e))
                    no_cellareao = True
                    cellarea_path = 'None'
                    cellareao_mod = np.nan
                    break 
                    
    if found_full is True: 
        cellareao_data = xr.open_dataset(os.path.join(cellarea_path,cellareao_filename)).load()

        if 'areacella' in list(cellareao_data.data_vars):
            cellareao_data = cellareao_data.rename_vars({'areacella':'areacello'})

        cellareao_mod = cellareao_data
    else: 
        [cellareao_npy,found,c] = find_cellareao_npy(mod)
        
        if found is True:
            print('Using areacello file from npy file')
            cellareao_mod = cellareao_npy
        else: 
            print('Using areacello file from '+str(m))
            cellareao_data = xr.open_dataset(os.path.join(cellarea_path,cellareao_filename)).load()

            if 'areacella' in list(cellareao_data.data_vars):
                cellareao_data = cellareao_data.rename_vars({'areacella':'areacello'})

            cellareao_mod = cellareao_data
        
    cellareao_mod = rename_lat_lon(cellareao_mod)
    cellareao_mod = rename_dimensions(cellareao_mod, mod)
                            
    return cellareao_mod, no_cellareao