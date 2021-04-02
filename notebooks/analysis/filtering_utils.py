# Butterworth filter functions

def butter_filt(x, filt_year, fs, order_butter, ftype):
    #filt_year = 1 #1 year
    #fs = 12 #monthly data
    # if ftype = band provide filt_year as a list or np array
    #fn = fs/2; # Nyquist Frequency
    fc = (1 / np.array(filt_year)) / 2 # cut off frequency 1sample/ 1year = (1/1)/2 equals 1 year filter (two half cycles/sample)
    #fc = (1/2)/2 # cut off frequency 1sample/ 2year = (1/1)/2 equals 2 year filter (two half cycles/sample)
    #fc = (1/4)/2 # cut off frequency 1sample/ 4year = (1/1)/2 equals 4 year filter (two half cycles/sample)
    #ftype = "low", "high" or "band"
    b, a = signal.butter(order_butter, fc, ftype, fs=fs, output='ba')

    return signal.filtfilt(b, a, x)

def filtfilt_butter(x, filt_year, fs, order_butter, ftype, dim='time'):
    # x ...... xr data array
    # dims .... dimension aong which to apply function    
    filt = xr.apply_ufunc(
                butter_filt,  # first the function
                x,# now arguments in the order expected by 'butter_filt'
                filt_year,  # as above
                fs,  # as above
                order_butter,  # as above
                ftype,
                input_core_dims=[[dim], [], [], [], []],  # list with one entry per arg
                output_core_dims=[[dim]],  # returned data has 3 dimension
                exclude_dims=set((dim,)),  # dimensions allowed to change size. Must be a set!
                vectorize=True,  # loop over non-core dims
                )

    return filt

def filtfilt_butter_monthly(x, filt_year, fs, order_butter, ftype, dim='time'):
    """
    Use this to filter each month of a timeseries separately and combine
    
    in:
    x = unfiltered vector time series e.g.: era_data['t2m_arc_mean_anom']
    others as for filtfilt_butter
    
    out:
    temp = filtered output
    """
    temp = np.zeros_like(x) * np.nan
    for m in range(0, 12):
        temp[m : len(temp) : 12] = filtfilt_butter(x.sel(time=x.time.dt.month == m+1),
                                                  filt_year=filt_year, fs=fs, order_butter=order_butter,
                                                  ftype=ftype, dim=dim)
    temp = xr.DataArray(temp, coords={'time': x.time}, dims=['time'])
    return temp