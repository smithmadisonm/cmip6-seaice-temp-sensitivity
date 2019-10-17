"""This is a general purpose module containing routines
(a) that are used in multiple notebooks; or 
(b) that are complicated and would thus otherwise clutter notebook design.
"""

def AverageArctic_airtemperature(TAS_IN,MEMBER_IN):
    #select latitudes greater than 70N
    tas_Arctic = TAS_IN.sel(lat=slice(70,90))
    #average over lat and lon, assumes 
    ts_tas_ArcticAve = tas_Arctic[MEMBER_IN,:,:].mean(dim=['lat','lon'])
    return ts_tas_ArcticAve


def Arctic_SIextent(SICONC_IN,CELLAREA_IN,MEMBER_IN):
    #cell areas only where SI concentration greater than 15% - must be same shape/format!
    cellarea_extent = CELLAREA_IN[MEMBER_IN,:,:].where(SICONC_IN[MEMBER_IN,:,:,:]>.15)
    #sum area where SI conc > 15%
    ts_Arctic_extent = cellarea_extent.sum(dim=['nlat','nlon'])
    return ts_Arctic_extent