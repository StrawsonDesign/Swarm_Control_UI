#!/usr/bin/env python

'''
check bandwidth of link
'''

import time
from collections import deque
from pymavlink import mavutil
import csv
import traceback

#from argparse import ArgumentParser
#parser = ArgumentParser(description=__doc__)

#parser.add_argument("--baudrate", type=int,
#                  help="master port baud rate", default=115200)
#parser.add_argument('--device', required=True)
#args = parser.parse_args()

# create a mavlink serial instance
#master = mavutil.mavlink_connection(args.device, baud=args.baudrate)
#device = 'udpout:192.168.1.107:14551'
device = 'udpout:192.168.7.2:14551'
baudrate = 57600
sizeOfBuffer = 10
t1 = time.time()
receivedPacketBuffer = deque([], sizeOfBuffer)
counts = {}
message_Roll = []
message_Pitch = []
message_Yaw = []
bytes_sent = 0
bytes_recv = 0
buff = 10
def wait_heartbeat(m):
    '''wait for a heartbeat so we know the target system IDs'''
    print("Waiting for APM heartbeat")
    m.wait_heartbeat()
    print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_system))

master = mavutil.mavlink_connection(device, baud=baudrate)
_ = 0
#wait_heartbeat(master)
with open('data.csv', 'w', buff * 1024) as csv_handle:
    csv_writer = csv.writer(csv_handle, delimiter=',')
    while True:    
        master.mav.heartbeat_send(1,  2, 3, 4, 5, 6)
        master.mav.sys_status_send(1, 2, 3, 4, 5, 6, 7, 8, 9 ,10, 11, 12,13)
        #master.mav.gps_raw_send(1, 2, 3, 4, 5, 6, 7, 8, 9)
        master.mav.attitude_send(1, 2, 3, 4, 5, 6, 7)
        master.mav.vfr_hud_send(1, 2, 3, 4, 5, 6)
        #master.mav.position_target_local_ned_send(1, 8, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        #master.mav.set_position_target_global_int_send(1,255,0,5,0b0000000000000000,1000,2000,500,1,1,1,2,2,2,1,1)
        #master.mav.attitude_target_send(1,0b0000000000000000,[1,0,0,0],1,1,1,0)  
        #master.mav.local_position_ned_system_global_offset_send(1,2,3,4,5,6,7)
        #master.mav.mission_count_send(255,0,2)
        master.mav.mav_flight_ctrl_and_modes_send(1,2,3,4,5,6,7,8,0,0,0)
        # position_target_local_ned_send(time_boot_ms, coordinate_frame, type_mask, x, y, z, vx, vy, vz, afx, afy, afz, yaw, yaw_rate)
    	# time_boot_ms              : Timestamp in milliseconds since system boot (uint32_t)
    	# coordinate_frame          : Valid options are: MAV_FRAME_LOCAL_NED = 1, MAV_FRAME_LOCAL_OFFSET_NED = 7, MAV_FRAME_BODY_NED = 8, MAV_FRAME_BODY_OFFSET_NED = 9 (uint8_t)
    	# type_mask                 : Bitmask to indicate which dimensions should be ignored by the vehicle: a value of 0b0000000000000000 or 0b0000001000000000 indicates that none of the setpoint dimensions should be ignored. If bit 10 is set the floats afx afy afz should be interpreted as force instead of acceleration. Mapping: bit 1: x, bit 2: y, bit 3: z, bit 4: vx, bit 5: vy, bit 6: vz, bit 7: ax, bit 8: ay, bit 9: az, bit 10: is force setpoint, bit 11: yaw, bit 12: yaw rate (uint16_t)
    	# x                         : X Position in NED frame in meters (float)
    	# y                         : Y Position in NED frame in meters (float)
    	# z                         : Z Position in NED frame in meters (note, altitude is negative in NED) (float)
    	# vx                        : X velocity in NED frame in meter / s (float)
    	# vy                        : Y velocity in NED frame in meter / s (float)
    	# vz                        : Z velocity in NED frame in meter / s (float)
    	# afx                       : X acceleration or force (if bit 10 of type_mask is set) in NED frame in meter / s^2 or N (float)
    	# afy                       : Y acceleration or force (if bit 10 of type_mask is set) in NED frame in meter / s^2 or N (float)
    	# afz                       : Z acceleration or force (if bit 10 of type_mask is set) in NED frame in meter / s^2 or N (float)
    	# yaw                       : yaw setpoint in rad (float)
    	# yaw_rate                  : yaw rate setpoint in rad/s (float)
        time.sleep(1)
        while 1:
            #m = master.recv_msg()
            _ += 1
            try: 
                data = master.recv()
                receivedPacketBuffer.append(data)
                if _ % sizeOfBuffer == 0:
                    for i in xrange(sizeOfBuffer):
                        m2 = master.mav.parse_char(receivedPacketBuffer.popleft())
                                               
                        if m2 is not None:
                            master.post_message(m2)
                        #print 'Message: ' + str(m2) + '\n'
                        
                        #if m2 == None: break:
                        if m2 == None: continue
                        if m2.get_type() not in counts: 
                            counts[m2.get_type()] = 0
                        counts[m2.get_type()] += 1
                        if m2 != None:
                            print("Received packet: MSG ID: %d \n" % (m2.get_msgId()))
                            if m2.get_msgId() == 30:
                                print m2
                                csv_writer.writerow([m2])
                                message_Roll.append(m2.roll)
                                message_Pitch.append(m2.pitch)
                                message_Yaw.append(m2.yaw)
                                #print 'Roll: ' + str(message_Roll) + '\n'
                                #print 'Pitch: ' + str(message_Pitch) + '\n'
                                #print 'Yaw: ' + str(message_Yaw) + '\n'
                                #print 'Type: ' + str(m2.get_type()) + '\n'
                                
                                #print 'Roll: ' + str(m2.roll) + '\n'
                                #print 'Pitch: ' + str(m2.pitch) + '\n'
                                #print 'Type: ' + str(m2.get_type()) + '\n'
                    message_Attitude = {'Roll': message_Roll, 'Pitch': message_Pitch, 'Yaw': message_Yaw}
                                       
                    break
            except(KeyboardInterrupt, SystemExit):
                raise
            except:
                traceback.print_exc()                
                    
        t2 = time.time()
        if t2 - t1 > 1.0:
            print("%u sent, %u received, %u errors bwin=%.1f kB/s bwout=%.1f kB/s" % (
                master.mav.total_packets_sent,
                master.mav.total_packets_received,
                master.mav.total_receive_errors,
                0.001*(master.mav.total_bytes_received-bytes_recv)/(t2-t1),
                0.001*(master.mav.total_bytes_sent-bytes_sent)/(t2-t1)))    
        bytes_sent = master.mav.total_bytes_sent
        bytes_recv = master.mav.total_bytes_received
        t1 = t2        