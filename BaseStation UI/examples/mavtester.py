#!/usr/bin/env python

'''
test mavlink messages
'''

import sys, struct, time, os
#from curses import ascii
#import mavtest
from pymavlink import mavutil

from argparse import ArgumentParser
parser = ArgumentParser(description=__doc__)

device = 'udpout://192.168.7.1:14551'
baudrate = 57600

parser.add_argument("--source-system", dest='SOURCE_SYSTEM', type=int,
                  default=22, help='MAVLink source system for this GCS')
args = parser.parse_args()

def wait_heartbeat(m):
	'''wait for a heartbeat so we know the target system IDs'''
	print("Waiting for APM heartbeat")
	msg = m.recv_match(type='HEARTBEAT', blocking=True)
	print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_system))

# create a mavlink serial instance
master = mavutil.mavlink_connection(device, baud=baudrate, source_system=args.SOURCE_SYSTEM)

# wait for the heartbeat msg to find the system ID
wait_heartbeat(master)

print("Sending all message types")
#mavtest.generate_outputs(master.mav)

