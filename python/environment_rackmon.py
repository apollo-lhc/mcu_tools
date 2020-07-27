#! /usr/bin/env python3


import time
import re
import pickle
import struct
import socket
# environment sensor
import Omron2JCIE_BU01
# daq HATS for 4 channel thermocouple
import daqhats #import mcc134, HatIDs, HatError, TcTypes
#from daqhats_utils import select_hat_device, tc_type_to_string

# script to run on Cornell PSB raspberry pi 3B+ with two OMRON
# 2JCIE-BU01 environment sensors and the four channel thermocouple MCC
# 134


# settable parameters 
GRAPHITE_IP = '192.168.38.1'
GRAPHITE_PORT = 2004 # this is the pickle port
# this is the root directory for the graphite data
carbon_directory = "shelf.00.ENV."
sensor_location=["lower","upper"]
sleeptime=60
# end settable

try:
    # two sensors for the environment monitoring
    sensors = [ Omron2JCIE_BU01.Omron2JCIE_BU01('/dev/ttyUSB0'),
                Omron2JCIE_BU01.Omron2JCIE_BU01('/dev/ttyUSB1')]
except (OSError, serial.SerialException) as e:
    print("Problem setting up the OMRON sensors", e)
    exit()


# set up connection to Graphite database 
sock = socket.socket()
sock.connect((GRAPHITE_IP, GRAPHITE_PORT))
starttime=time.time()

# configure the thermocouple
# type e
tc_type = daqhats.TcTypes.TYPE_E
delay_between_read = 60 # in seconds
channels=(0,1) # of four possible
tc_address = daqhats.hat_list(filter_by_id=daqhats.HatIDs.MCC_134)[0].address
tc_hat = daqhats.mcc134(tc_address)
try:
    for channel in channels:
        tc_hat.tc_type_write(channel, tc_type)
except (HatError, ValueError) as e:
    print("\n", e)
    exit()

db=([])
ii=0
while True:
    ####
    #### OMRON 2JCIE BU01 environmental sensor
    ####
    # loop over two sensors
    # update OMRON readings 
    for s in range(0,2):
        sensors[s].update()
        time_epoch = int(time.time())
    for s in range(0,2):
        vv = [ attr for attr in dir(sensors[s]) if not callable(getattr(sensors[s],attr)) and not attr.startswith("_")]

        for v in vv:
            header = carbon_directory  + sensor_location[s] + "." + v
            header = header.replace(" ", "_")
            val = getattr(sensors[s],v)
            db.append((header,(time_epoch, val)))

    ###
    ### MCC 134 4 channel thermocouple
    ###
    for channel in channels:
        val = tc_hat.t_in_read(channel)
        if val == daqhats.mcc134.OPEN_TC_VALUE:
            val = float('Nan')
        header = carbon_directory  + "tc" + str(channel) + ".TEMP"
        db.append((header,(time_epoch, val)))



    
    # send data to grafana on every cycle
    payload = pickle.dumps(db, protocol=2)
    header = struct.pack("!L", len(payload))
    message = header + payload
    sock.sendall(message)
    ii = ii+ 1
    if ( ii%15 == 0 ) :
        print(db)
        print('sent packet ', ii)
    db = ([])

    
    time.sleep(sleeptime- ((time.time()-starttime)%sleeptime))



try:
    sensors[0].close()
    sensors[1].close()
    sock.close()
except:
    pass

