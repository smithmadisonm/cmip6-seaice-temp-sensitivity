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
    if 'x' in DICT_IN.dims:
        DICT_OUT = DICT_IN.rename(dict(x='j',y='i'))
    else: 
        DICT_OUT = DICT_IN
    return DICT_OUT

def find_overlap_models(VAR_LIST,EXP,TABLE_ID,MODEL_INTERSECT,COL):
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
    if len(VAR['time'].attrs) is 0:
        print('yes')
        return VAR['time']
    else: 
        attrs = {'units': VAR['time'].units}
        ds = xr.Dataset({'time': ('time', VAR.time.values, attrs)})
        var = xr.decode_cf(ds).time
        return var
