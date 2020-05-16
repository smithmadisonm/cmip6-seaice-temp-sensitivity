import cftime
import intake
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import warnings

from load_utils import get_cmip6_catalogue,find_overlap_models,rename_dimensions,rename_lat_lon

# warnings.filterwarnings('ignore')

# Select which datasets are required by populating var_interest with details
# var_interest = {'siconc':{'table_id':'SImon','grid':'gn'},
#                 'tas':{'table_id':'Amon','grid':'gn'},
#                 'areacello':{'table_id':'Ofx','grid':'gn'}}
var_interest = {'siconc':{'table_id':'SImon','grid':'gn'},
                'tas':{'table_id':'Amon','grid':'gn'}}

# Select name for this clollection of inputs
collection_name = 'historical'
#collection_name = 'piControl'
#collection_name = 'ssp370'

# IF True: will check to make sure only r*i1p1n1 experiments are included: 
check_member_id = False

#------------------------------------------------------------------
dset_name, exp, var, table_id, grid_label = [], [], [], [], []

for v in var_interest.keys():
    dset_name.append(v)
    exp.append(collection_name)
    var.append(v)
    table_id.append(var_interest[v]['table_id'])
    grid_label.append(var_interest[v]['grid'])

# Get full catalogue of CMIP6 data on glade or cloud
cmip6_collection = get_cmip6_catalogue()

# Find where models contain all necessary variables
models_intersect = find_overlap_models(dset_name, exp, var, table_id, grid_label, cmip6_collection)
print(collection_name+' model runs containing '+
      str([i for i in var_interest.keys()])+' = '+str(models_intersect))

# Loading each model individually
dset_dict = {}
for i, d in enumerate(dset_name):
    dset_dict[d] = {}
    for m in models_intersect:
        print(d, m)
        #Get catalogue dictionary for a given model/experiment/variable combination
        sub_collection = cmip6_collection.search(source_id=m,
                                experiment_id=exp[i], table_id=table_id[i], 
                                variable_id=var[i], grid_label=grid_label[i])
        #Load catalogue into xarray datasets
        if m != 'MRI-ESM2-0' or exp[i] != 'piControl':
            dset_dict[d][m] = sub_collection.to_dataset_dict(
                                    zarr_kwargs={'consolidated': True, 'decode_times': True}, 
                                    cdf_kwargs={'chunks': {}, 'decode_times': True})  
        elif m == 'MRI-ESM2-0' and exp[i] == 'piControl':
            dset_dict[d][m] = sub_collection.to_dataset_dict(
                                    zarr_kwargs={'consolidated': True, 'decode_times': False}, 
                                    cdf_kwargs={'chunks': {}, 'decode_times': False})
 


# # Get dictionary of file names for speficied data
# dset_dict = {}
# for i in range(0, len(dset_name)):
#     dset_dict[dset_name[i]] = cmip6_collection.search(
#                                 experiment_id=exp[i], table_id=table_id[i], 
#                                 variable_id=var[i], grid_label=grid_label[i])

# # Loading data
# for d in dset_dict.keys():
#     print(d)
#     dset_dict[d] = dset_dict[d].to_dataset_dict(zarr_kwargs={'consolidated': True, 'decode_times': True}, 
#                                                 cdf_kwargs={'chunks': {}, 'decode_times': True})    
# Having some problems, times don't want to be decoded for picontrol. Might not be a problem but should investigate.

# Making key of dataset model name
dset_dict_temp = {}
for d in dset_dict.keys():
    dset_dict_temp[d] = {}
    for model in dset_dict[d].keys():
        for key, item in dset_dict[d][model].items():
            dset_dict_temp[d][model] = item            
dset_dict = dset_dict_temp

#Fixing times
for d in dset_dict.keys():
    if d == 'areacello' or d == 'areacella':
        continue
    # Making time datetime object in models where it is stored as numpy64
    if 'MRI-ESM2-0' in dset_dict[d].keys() and exp[0] == 'piControl':
        print('Fixing MRI-ESM2-0 times')
        t = dset_dict[d]['MRI-ESM2-0']['time']
        t = cftime.num2date(t, t.attrs['units'], calendar=t.attrs['calendar'], only_use_cftime_datetimes=True)
        dset_dict[d]['MRI-ESM2-0']['time'] = t
    # Making time datetime object in models where it is stored as timestamp
    if 'MIROC-ES2L' in dset_dict[d].keys() and exp[0] == 'piControl':
        print('Fixing MIROC-ES2L times')
        MIROC_t = dset_dict[d]['MIROC-ES2L']['time'].values
        for i, t in enumerate(MIROC_t):
            if str(type(t))[8] == "p": #then is a timestamp and needs converting
                t = t.to_pydatetime()
                MIROC_t[i] = cftime.DatetimeGregorian(t.year, t.month, t.day, t.hour)
        dset_dict[d]['MIROC-ES2L']['time'] = MIROC_t

# Rename dimensions to i,j so they're consistent across variables
dset_dict_temp = {}
dset_dict_temp_lalo = {}
for d in dset_dict.keys():
    dset_dict_temp[d] = {}
    dset_dict_temp_lalo[d] = {}
    for m in dset_dict[d].keys():
        dset_dict_temp[d][m] = rename_dimensions(dset_dict[d][m], dset_dict_temp)
        if d == 'siconc':
            dset_dict_temp_lalo[d][m] = rename_lat_lon(dset_dict_temp[d][m], dset_dict_temp_lalo)
        else: 
            dset_dict_temp_lalo[d][m] = dset_dict_temp[d][m]
dset_dict = dset_dict_temp_lalo


if 'areacello' in dset_dict.keys():
    for d in dset_dict.keys(): # for each variable
        for key in dset_dict[d].keys(): # for each model
            # if table_id suggests variable is a sea ice or ocean variable, add areacello
            if dset_dict[d][key].attrs['table_id'][0] in ['S', 'O']:
                dset_dict[d][key]['areacello'] = dset_dict['areacello'][key]['areacello']

if 'areacella' in dset_dict.keys():
    for d in dset_dict.keys(): # for each variable
        for key in dset_dict[d].keys(): # for each model
            # if table_id suggests variable is an atmosphere variable, add areacella
            if dset_dict[d][key].attrs['table_id'][0] in ['A']:
                dset_dict[d][key]['areacella'] = dset_dict['areacella'][key]['areacella']    
                
                
# Ensure only ensemble members that overlap all data variables are included
if check_member_id == True: 
    dset_dict_temp = {}
    for d in dset_dict.keys():
        dset_dict_temp[d] = {}

    for m in models_intersect:
        ems = [0]
        for d in dset_dict.keys():
            dset_dict_temp[d][m] = {}
            if d is not 'areacello':
                if ems[0]==0:
                    ems = dset_dict[d][m]['member_id'].values
                else:
                    ems = list(set(ems) & set(dset_dict[d][m]['member_id'].values))
        for d in dset_dict.keys():                       
            dset_dict_temp[d][m] = dset_dict[d][m].sel(member_id=ems)

        print(m, ems)
        print()
    dset_dict = dset_dict_temp

# add variable names to filename: 
var_text = [v+'_' for v in list(var_interest.keys())]
end_text=''
for v in var_text:
    end_text = end_text+v

# Save dictionaries for future use
save_flag = True
if save_flag:
    if dset_dict:
        np.save('dset_dict_' + collection_name + '_' + end_text + 'extracted.npy', dset_dict)