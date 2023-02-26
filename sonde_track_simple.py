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
from binascii import *

from utilities import razel

obs = {}
cnt = 0



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

    if cfg['main']['base_path'] == 'cwd':
        cfg['main']['base_path'] = os.getcwd()

    cfg['serial'] = args.serial
    return cfg

def on_message(msg):
    # print(type(msg), len(msg))
    # print(json.dumps(msg, indent=4))
    global cnt
    cnt = cnt + 1
    ts = datetime.datetime.utcnow()
    rae = razel.RAZEL(obs['lat'], obs['lon'], obs['alt']/1000.0,
                      msg['lat'], msg['lon'], msg['alt']/1000.0)
    
    print("MESSAGE INFO:", msg['serial'])
    print("        counter: {:d}".format(cnt))
    print("   Sonde Serial:", msg['serial'])
    print(" Sonde Datetime:", msg['datetime'])
    print("  Received Time:", msg['time_received'])
    print("            Now:", datetime.datetime.strftime(ts, "%Y-%m-%dT%H:%M:%S.%fZ"))
    print("      Sonde Loc:", msg['lat'], msg['lon'], msg['alt'])
    print("RECEIVER INFO")
    print("       Receiver:", msg['uploader_callsign'])
    print("   Receiver Loc:", msg['uploader_position'], msg['uploader_alt'])
    print("   Receiver Ant:", msg['uploader_antenna'])
    print("       SNR [dB]:", msg['snr'])
    print("RADIOSONDE INFO:")
    print("   Altitude [km]: {:3.3f}".format(msg['alt']/1000.0))
    # print("V Velocity [m/s]: {:+3.3f}".format(msg['vel_v']))
    if msg['vel_v'] < 0.0:
        print("V Velocity [m/s]: {:+3.3f}".format(msg['vel_v']), "DESCENDING")
    else:
        print("V Velocity [m/s]: {:+3.3f}".format(msg['vel_v']), "Ascending")
    print("H Velocity [m/s]: {:3.3f}".format(msg['vel_h']))
    print("   Heading [deg]: {:3.3f}".format(msg['heading']))
    if 'temp' in msg.keys(): 
        print(" Temperature [C]: {:3.3f}".format(msg['temp']))
    if 'batt' in msg.keys(): 
        print("     Battery [V]: {:3.3f}".format(msg['batt']))
    if 'sats' in msg.keys(): 
        print("  Satellites [#]: {:d}".format(msg['sats']))
    print("OBSERVER INFO: {:s}".format(obs['name']))
    print("    Observer Loc:", obs['lat'], obs['lon'], obs['alt'])
    print("     Range  [km]: {:3.3f}".format(rae['rho']))
    print("   Azimuth [deg]: {:3.3f}".format(rae['az']))
    print(" Elevation [deg]: {:3.3f}".format(rae['el']))
    
    print()
    
    

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
                       default="simple_config.yaml",
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
    #print(chr(27) + "[2J")
    subprocess.run(["reset"])
    #print(sys.path)
    print(args.serial)
    if not args.serial:
        print("Please enter a target Radiosonde Serial Number...")
        sys.exit()


    cfg = import_configs_yaml(args)
    print(cfg)
    obs = cfg['main']['observer']

    test = sondehub.Stream(on_message=on_message, 
                           sondes=[cfg['serial']])
    while 1:
        time.sleep(1)
        pass
    sys.exit()




