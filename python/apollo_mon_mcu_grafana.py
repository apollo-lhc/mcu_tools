#!/usr/bin/env python
# coding: utf-8
# wittich
# run with python2

### this is a script that is run on the zynq
### and reads out the monitoring data from the
### UART for the MCU and then sends it to the
### grafana

### this script is not needed in its current form
### with the ZYNQ-MCU UART data monitoring path
###
### 7/2020


from __future__ import print_function
import serial
import time
import re
import pickle
import struct
import socket

# settable parameters 
GRAPHITE_IP = '192.168.38.1'
GRAPHITE_PORT = 2004 # this is the pickle port
carbon_directory = "shelf.00.AP09.MCU." # this is the root directory for the graphite data
ttydevice = "/dev/ttyUL1"

# strip out escape characters
ansi_esc = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

### this is unused but useful 
column_headers = [
    "Time",
    "T(3V3/1V8)",
    "T(KVCCINT1)",
    "T(KVCCINT2)",
    "T(VVCCINT1)",
    "T(VVCCINT2)",
    "I1(3V3/1V8)",
    "I1(KVCCINT1)",
    "I1(KVCCINT2)",
    "I1(VVCCINT1)",
    "I1(VVCCINT2)",
    "I2(3V3/1V8)",
    "I2(KVCCINT1)",
    "I2(KVCCINT2)",
    "I2(VVCCINT1)",
    "I2(VVCCINT2)",
    "K01  12 Tx GTH",
    "K01  12 Rx GTH",
    "K02  12 Tx GTH",
    "K02  12 Rx GTH",
    "K03  12 Tx GTH",
    "K03  12 Rx GTH",
    "K04 4 XCVR GTY",
    "K05 4 XCVR GTY",
    "K06 4 XCVR GTY",
    "K07  12 Tx GTY",
    "K07  12 Rx GTY",
    "V01 4 XCVR GTY",
    "V02 4 XCVR GTY",
    "V03 4 XCVR GTY",
    "V04 4 XCVR GTY",
    "V05 4 XCVR GTY",
    "V06 4 XCVR GTY",
    "V07 4 XCVR GTY",
    "V08 4 XCVR GTY",
    "V09 4 XCVR GTY",
    "V10 4 XCVR GTY",
    "V11  12 Tx GTY",
    "V11  12 Rx GTY",
    "V12  12 Tx GTY",
    "V12  12 Rx GTY",
]


def get_command(command):
    lines = []
    # just ensure command has newline 
    command = command.rstrip()
    command = command + '\r\n'
    #print(command)
    ser.write(command.encode()) # write one char from an int
    done = False
    while ( not done ):
        line  = ser.readline()
        line = ansi_esc.sub('',line).rstrip()
        #if ( len(line) ) :
            #print( '>',line, '<')
            #print '>',line, '<>', len(line), '<>', line[0], type(line[0])
        #if ( len(line) and chr(line[0]) == '%' ) :
        if ( len(line) and (line[0]) == '%' ) :
            done = True
        else :
            lines.append(line)
    return lines


def update_ps_temps():
    tempmap = {}
    once = get_command("psmon 0")
    #print('once is\n', once)
    # skip command and first line
    for io in once[2:]:
        #print('>',io,'<')
        if (len(io) == 0) : 
            continue
        if (io.find("SUPPLY") != -1 ) : #header
            key = io.split()[1]
            continue
        elif (io.find("VALUE") != -1) : # values
            undef, svalue1, undef, svalue2 = io.split()
            value1 = float(svalue1.strip())
            value2 = float(svalue2.strip())
        else :
            print("I'm confused",io,__name__)
            key = "None"
            value1 = None
            value2 = None
        if key == "3V3/1V8":
            tempmap["T.PS3V3"] = value1
            tempmap["T.PS1V8"] = value2
        else:
            tempmap["T.PS"+key+"1"] = value1
            tempmap["T.PS"+key+"2"] = value2
    return tempmap

def update_ps_currents():
    currmap = {}
    once = get_command("psmon 4")
    # skip command and first line
    for io in once[2:]:
        if (len(io) == 0) : 
            continue
        if (io.find("SUPPLY") != -1 ) : #header
            key = io.split()[1]
            continue
        elif (io.find("VALUE") != -1) : # values
            undef, svalue1, undef, svalue2 = io.split()
            value1 = float(svalue1.strip())
            value2 = float(svalue2.strip())
        else :
            print("I'm confused",io,__name__)
            key = "None"
            value1 = None
            value2 = None
        if key == "3V3/1V8":
            currmap["I.3V3"] = value1
            currmap["I.1V8"] = value2
        else:
            currmap["I1."+key] = value1
            currmap["I2."+key] = value2
    try:
        currmap["I.VVCCINT"] = currmap["I1.VVCCINT1"] \
                               + currmap["I2.VVCCINT1"] \
                               + currmap["I1.VVCCINT2"] \
                               + currmap["I2.VVCCINT2"]
        currmap["I.KVCCINT"] = currmap["I1.KVCCINT1"] \
                               + currmap["I2.KVCCINT1"] \
                               + currmap["I1.KVCCINT2"] \
                               + currmap["I2.KVCCINT2"]
    except KeyError, e:
        print("error adding currents", e, currmap)
    
    return currmap

def update_ff():
    tempmap = {}
    once = get_command('ff')
    #print(once)
    for io in once:
        oneline = list(map( str.strip, io.split('\t')))
        for o in oneline:
            if (len(o) == 0) : 
                continue
            if ( o.find(":") == -1 ):
                continue
            key,svalue = o.split(":")
            if ( svalue.strip() == "--") : 
                continue

            value = int(svalue.strip())
            tempmap["T."+key] = value
            
    return tempmap

sleeptime=60



def timestamp_str():
    return time.strftime("%Y%m%d_%H%M")
#    return str(int(time.time()))

i=0

# set up connection to Graphite database 
sock = socket.socket()
sock.connect((GRAPHITE_IP, GRAPHITE_PORT))
starttime=time.time()

#initalize data to send to grafana
db = ([])

ii=0
while True:
    try: 
        ser = serial.Serial(port=ttydevice, baudrate=115200, timeout=1)
        timestamp = time.time()
        temps1 = update_ff()
        temps2 = update_ps_temps()
        currents = update_ps_currents()
        ser.close()
        time_epoch = int(time.time())
        for d in [ temps1, temps2, currents] :
            for key in d.keys():
                try:
                    header = carbon_directory + key.replace(" ", "_")
                    val = float(d[key])
                    db.append((header,(time_epoch, val)))
                except (ValueError, TypeError) as e:
                    print("can't make this a float:", d[key], e)
        if len(db) > 50 :
            payload = pickle.dumps(db, protocol=2)
            header = struct.pack("!L", len(payload))
            #print(db)
            message = header + payload
            sock.sendall(message)
            ii = ii+ 1
            print('sent packet ', ii)
            db = ([])

    except (OSError, serial.SerialException) as e:
        print("missing iteration (serial or os error) ", i, timestamp, e)
    except ValueError, e:
        print("Error in conversion, skipping iteration", e)
    except Exception as e:
        print("unknown error", e)
    time.sleep(sleeptime- ((time.time()-starttime)%sleeptime))








