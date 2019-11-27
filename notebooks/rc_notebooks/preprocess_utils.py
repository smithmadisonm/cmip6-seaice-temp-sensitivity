"""
Calculates basic variables including:
Arctic mean temperature
Arctic sea ice extent
"""
import numpy as np

def arctic_mean(VAR_DICT,VAR,MIN_LAT):
    ones_full = np.ones((VAR.isel(time=0,member_id=0).shape))
    area_weight = np.cos(np.deg2rad(VAR_DICT.lat)).expand_dims('lon',axis=1)*ones_full

    var_armn = (VAR*area_weight).sel(lat=slice(MIN_LAT,90)).sum(
        dim=['lat','lon'])/(area_weight.sel(lat=slice(MIN_LAT,90)).sum(dim=['lat','lon']))
    return var_armn

def Arctic_SIextent(SICONC_IN,CELLAREA_IN):
   #Find index for NH
   NH_ind = int(SICONC_IN['j'].shape[0]/2)
   #cell areas only where SI concentration greater than 15% - must be same shape/format!
   cellarea_extent = CELLAREA_IN[:,NH_ind:,:].where(SICONC_IN[:,:,NH_ind:,:]>15)
   #sum area where SI conc > 15%
   ts_Arctic_extent = cellarea_extent.sum(dim=['i','j'])
   return ts_Arctic_extent