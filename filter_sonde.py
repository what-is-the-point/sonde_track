#!/usr/bin/env python3

import socket
import os
import string
import sys
import time
import argparse
import datetime
import json, csv, yaml
import subprocess
import sondehub
import math
import copy
from binascii import *
import pandas as pd
import numpy as np

def import_configs_yaml(args):
    ''' setup configuration data '''
    fp_cfg = '/'.join([args.cfg_path,args.cfg_file])
    print (fp_cfg)
    if not os.path.isfile(fp_cfg) == True:
        print('ERROR: Invalid Configuration File: {:s}'.format(fp_cfg))
        sys.exit()
    print('Importing configuration File: {:s}'.format(fp_cfg))
    with open(fp_cfg, 'r') as yaml_file:
        cfg = yaml.safe_load(yaml_file)
        yaml_file.close()

    cfg['serial'] = args.serial
    return cfg

def ImportRadioSondeFile(data_path, serial):
    fn = ".".join([serial,'log'])
    fp = "/".join([data_path,fn])

    if not os.path.isfile(fp):
        print("Data Log does not exist: {:s}".format(fp))
        print("Check path, serial, file names")
        print("Exitting...")
        sys.exit()
    print("Importing Radio Sonde Log file: {:s}".format(fp))

    df = pd.read_json(fp, lines=True)
    original_count = len(df)
    df.drop_duplicates(subset=['datetime'], keep='first', inplace=True, ignore_index=True)
    filtered_count = len(df)
    print("Original Data Point Count: {:d}".format(original_count))
    print("Filtered Data Point Count: {:d}\n".format(filtered_count))
    return df

if __name__ == '__main__':
    """ Main entry point to start the service. """
    startup_ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    #--------START Command Line argument parser----------------
    parser = argparse.ArgumentParser(description="Simple RadioSonde Tracker",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    cwd = os.getcwd()
    cfg_fp_default = '/'.join([cwd, 'config'])
    cfg = parser.add_argument_group('Configuration File')
    cfg.add_argument('--cfg_path',
                       dest='cfg_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'config']),
                       help="Configuration File Path",
                       action="store")
    cfg.add_argument('--cfg_file',
                       dest='cfg_file',
                       type=str,
                       default="filter_sonde_config.yaml",
                       help="Configuration File",
                       action="store")
    cfg.add_argument('--serial',
                       dest='serial',
                       type=str,
                       default=None,
                       help="Radiosonde Serial",
                       action="store")
    args = parser.parse_args()
    #--------END Command Line argument parser-----------------
    subprocess.run(["reset"])

    cfg = import_configs_yaml(args)
    print(cfg)

    #Configure Serial Number
    #  if no serial specified on command line, use the first file
    if cfg['serial'] == None:
        print("No Serial number specified, using first file in datapath...")
        filenames = next(os.walk(cfg['in_path']), (None, None, []))[2]
        cfg['serial'] = filenames[0].split(".")[0]

    df = ImportRadioSondeFile(cfg['in_path'], cfg['serial'])
    df = df[cfg['keep_list']] #filter columns
    df.name = cfg['serial'] #assign serial number to the dataframe name
    
    print(df.head(10)) #print the first ten rows
    print(df.info())
    print(df.name)

    
    if cfg['export']:
        if not os.path.exists(cfg['out_path']):
            print("Output Path Does Not Exist...Creating...")
            os.makedirs(cfg['out_path'])
            print("Created: {:s}".format(cfg['out_path']))
        
        if cfg['format'] == 'json':
            o_f = ".".join([cfg['serial'],"json"])
        elif cfg['format'] == 'csv':
            o_f = ".".join([cfg['serial'],"csv"])
        elif cfg['format'] == 'orig':
            o_f = ".".join([cfg['serial'],"log"])

        o_fp = "/".join([cfg['out_path'],o_f])
        print("Exporting data to: {:s}".format(o_fp))

        if cfg['format'] == 'json':
            df.to_json(o_fp, 
                       orient='records', 
                       date_format = 'iso', 
                       date_unit='us', 
                       indent=4)
        elif cfg['format'] == 'csv':
            df.to_csv(o_fp, index = False)
        elif cfg['format'] == 'orig':
            #maintain original format as the downloaded sonde logs
            df.to_json(o_fp, 
                       orient='records', 
                       date_format='iso', 
                       date_unit='us',
                       lines = True)


    sys.exit()

    