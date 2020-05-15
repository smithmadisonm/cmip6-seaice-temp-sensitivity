import intake
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from scipy import stats
import warnings

import analysis_utils as au

# USER PARAMETERS: -----------------------------------
# Load dataset
collection_fname = '../dset_dict_historical.npy'
#collection_fname = 'dset_dict_piControl.npy'

# Set maximum number of ensemble members to look at for each model
# N.B. doing this for anomalies give you the same answer as not anomalies.
# Which makes sense when you think about it.
max_ems = 1
# ----------------------------------------------------

dset_dict = np.load(collection_fname, allow_pickle='TRUE').item()
first_dset = list(dset_dict.keys())[0]
models_intersect = list(dset_dict[first_dset].keys())

# Check for member_ids ending in 'i1p1f1' and removes others
for m in models_intersect:
    ems_str=[]
    ems = list(dset_dict['siconc'][m]['member_id'].values)
    ems_new = []
    for memid in ems: 
        if memid.endswith('i1p1f1'):
            ems_new.append(memid)
    if len(ems_new) == 0: 
        models_intersect.remove(m)
    dset_dict['siconc'][m] = dset_dict['siconc'][m].sel(member_id=ems_new)
# ----------------------------------------------------

warnings.filterwarnings('ignore')
slopes_all, r_all, intercept_all= {}, {}, {}

for m in models_intersect:
    if max_ems ==1:
        ems = ['r1i1p1f1']
    else:
        ems = np.sort(dset_dict['siconc'][m]['member_id'].values)
    if len(ems)>max_ems:
        ems = ems[0:max_ems]
    print('Working on...')
    print(m)
    
    # Perform regression
    slopes_all[m], r_all[m],intercept_all[m] = {}, {}, {}
    for i, em in enumerate(ems):
        print(em)
        [slopes_all[m][i], 
        r_all[m][i],
        intercept_all[m][i]] = au.scatter_linreg(dset_dict['tas'][m]['tas_arc_mean'].sel(member_id=em),
                                                 dset_dict['siconc'][m]['sie_tot_arc'].sel(member_id=em),
                                                 [2,8], m, False)
warnings.filterwarnings('default')
# ----------------------------------------------------

# Calculate ensemble mean and r values for each model
slopes_mean, r_mean = {}, {}

print('Model, slopes (mar, sept), r (mar, sept)')
print()
for m in models_intersect:
    slopes_mean_temp, r_mean_temp = [], []
    for em in slopes_all[m].keys():
        slopes_mean_temp.append(slopes_all[m][em])
        r_mean_temp.append(r_all[m][em])                
    slopes_mean[m] = np.mean(slopes_mean_temp,0)
    r_mean[m] = np.mean(r_mean_temp,0)
    
# Save dictionaries for future use
results_fname = 'results_' + collection_fname[10:]
save_flag = True
if save_flag:
    if dset_dict:
        np.save(results_fname, slopes_mean, r_mean)