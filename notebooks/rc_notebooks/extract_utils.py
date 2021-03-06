"""
Module containing scripts for reading CMIP6 data into xarray datasets
"""

import intake
import re
import socket

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
        DICT_OUT = DICT_IN.rename(dict(x='j',y='i'))
    elif 'ni' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename(dict(nj='j',ni='i'))
    elif 'nlon' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename(dict(nlat='j',nlon='i'))
    elif 'longitude' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename(dict(latitude='j',longitude='i'))
    else: 
        DICT_OUT = DICT_IN
    return DICT_OUT