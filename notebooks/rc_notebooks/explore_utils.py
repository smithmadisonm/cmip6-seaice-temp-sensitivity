"""
Module containing scripts for exploring CMIP6 collection
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