"""
Module containing scripts for exploring and reading CMIP6 data into xarray datasets
"""

import intake
import re
import socket

def is_ncar_host():
    """
    Determine if host is an NCAR machine
    """
    hostname = socket.getfqdn()
    
    return any([re.compile(ncar_host).search(hostname) 
                for ncar_host in ['cheyenne', 'casper', 'hobart']])

def get_cmip6_catalogue():
    """
    Get full catalogue of CMIP6 data on glade or cloud
    """
    if is_ncar_host():
        cmip6_collection = intake.open_esm_datastore("../../catalogs/glade-cmip6.json")
    else:
        cmip6_collection = intake.open_esm_datastore("../../catalogs/pangeo-cmip6.json")
    
    return cmip6_collection;
    
def find_overlap_models(DSET_NAME, EXP_LIST, VAR_LIST, TABLE_ID, GRID_LIST, COL):
    """
    Finds models that contain all the variables in VAR_LIST
       inputs: 
            VAR_LIST = list of variable names (list of (str))
            EXP_LIST = list of experiment names (str)
            TABLE_ID = list of table ids associated with variable names (list of (str))
            MODEL_LIST = 
            COL = output object (cmip6_collection) of intake.open_esm_datastore 
       outputs: 
           MODEL_INTERSECT = list of models with all variables in VAR_LIST
    """
    uni_dict = COL.unique(['source_id', 'experiment_id', 'table_id'])
    MODEL_LIST = set(uni_dict['source_id']['values']) # all the models
    
    for v in range(0, len(VAR_LIST)):
        query = dict(experiment_id=EXP_LIST[v], table_id=TABLE_ID[v], 
                     variable_id=VAR_LIST[v], grid_label=GRID_LIST[v])  
        cat = COL.search(**query)
        MODEL_LIST = MODEL_LIST.intersection(
            {MODEL_LIST for MODEL_LIST in cat.df.source_id.unique().tolist()})

    MODEL_INTERSECT = list(MODEL_LIST)
    return MODEL_INTERSECT

def rename_dimensions(DICT_IN, DICT_OUT):
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
        DICT_OUT = DICT_IN.rename_dims(dict(x='j',y='i'))
    elif 'ni' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename_dims(dict(nj='j',ni='i'))
    elif 'nlon' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename_dims(dict(nlat='j',nlon='i'))
    elif 'longitude' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename_dims(dict(latitude='j',longitude='i'))
    elif 'lon' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename_dims(dict(lat='j',lon='i'))
    else: 
        DICT_OUT = DICT_IN
    return DICT_OUT

def rename_lat_lon(DICT_IN, DICT_OUT):
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
        DICT_OUT = DICT_IN
    elif 'latitude' in list(DICT_IN.data_vars):
        DICT_OUT = DICT_IN.set_coords(['latitude','longitude'])
    elif 'lat' in list(DICT_IN.coords):
        DICT_OUT = DICT_IN.rename({'lat':'latitude','lon':'longitude'})
    elif 'lat' in list(DICT_IN.data_vars):
        dict_out_temp = DICT_IN.rename({'lat':'latitude','lon':'longitude'})
        DICT_OUT = dict_out_temp.set_coords(['latitude','longitude'])
    else: 
        DICT_OUT = DICT_IN
        
    return DICT_OUT