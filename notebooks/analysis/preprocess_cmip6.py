import intake
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from scipy import stats
import warnings

from analysis_utils import arctic_mean, Arctic_SIextent

# Load dataset
#collection_fname = 'dset_dict_historical.npy'
collection_fname = 'dset_dict_piControl.npy'
# ------------------------------------------------------------------------

dset_dict = np.load(collection_fname, allow_pickle='TRUE').item()
first_dset = list(dset_dict.keys())[0]
models_intersect = dset_dict[first_dset].keys()

si_dict = dset_dict['siconc']
tas_dict = dset_dict['tas']

for m in models_intersect:
    si_dict[m]['sie_tot_arc'] = Arctic_SIextent(si_dict[m]['siconc'], si_dict[m]['areacello'], 15)
    tas_dict[m]['tas_arc_mean'] = arctic_mean(tas_dict[m], tas_dict[m]['tas'], 70)
    
dset_dict['siconc'] = si_dict
dset_dict['tas'] = tas_dict
# ------------------------------------------------------------------------

# Calculate climatology, anomalies and stds for variables matching dataset keys
# There are some performance warnings from dask. Hopefully not an issue?
warnings.filterwarnings('ignore')

for d in dset_dict.keys():
    if d not in ['areacello', 'areacella']:
        for m in models_intersect:
            dset_dict[d][m][d + '_clim'] = dset_dict[d][m][d].groupby('time.month').mean(dim='time')
            dset_dict[d][m][d + '_anom'] = dset_dict[d][m][d].groupby('time.month') - dset_dict[d][m][d + '_clim']
            dset_dict[d][m][d + '_std'] = dset_dict[d][m][d].groupby('time.month').std()
            
warnings.filterwarnings('default')
# ------------------------------------------------------------------------

# Possibly want to detrend the data. Repurpose this code if so:
#from scipy.signal import detrend
#sst_anom_detrended = xr.apply_ufunc(detrend, sst_anom.fillna(0),
#                                    kwargs={'axis': 0}).where(~sst_anom.isnull())

# Actually more likely to want to filter or remove moving average probably.
# ------------------------------------------------------------------------

# Calculate climatology, anomalies and stds for Arctic sea ice extent and mean Arctic temperature
# There are some performance warnings from dask. Hopefully not an issue?
warnings.filterwarnings('ignore')

# n.b. total anomalies don't add up to exactly zero for sie_tot_arc_anom
# this is just a precision thing because xarrays are only 8 sig figs

for m in models_intersect:
    var1 = dset_dict['siconc'][m]['sie_tot_arc']
    dset_dict['siconc'][m]['sie_tot_arc_clim'] = var1.groupby('time.month').mean(dim='time')
    dset_dict['siconc'][m]['sie_tot_arc_anom'] = var1.groupby('time.month') - dset_dict['siconc'][m]['sie_tot_arc_clim']
    
    var2 = dset_dict['tas'][m]['tas_arc_mean']
    dset_dict['tas'][m]['tas_arc_mean_clim'] = var2.groupby('time.month').mean(dim='time')
    dset_dict['tas'][m]['tas_arc_mean_anom'] = var2.groupby('time.month') -  dset_dict['tas'][m]['tas_arc_mean_clim'] 
    
warnings.filterwarnings('default')
# ------------------------------------------------------------------------

# Save dictionaries for future use
save_flag = True
if save_flag:
    if dset_dict:
        np.save(collection_fname, dset_dict)