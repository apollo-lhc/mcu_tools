#!/usr/bin/env python 

import serial
import time
import io
import optparse
import os

dir = os.path.dirname(os.path.abspath(__file__))

parser = optparse.OptionParser()
parser.add_option('--tty', dest="tty_device", default='ttyUL1', help='Specify tty device. ttyUL1 for ZYNQ. ttyUSB0 or ttyUSB1 for CPU.')
parser.add_option('--mode', type="int", dest="mode", default= 0, help='Specify which clock source to set for MGTREFCLK1, 0 is High_Perf, 1 is Synth')
o, a = parser.parse_args()

serPort = "/dev/"+o.tty_device

ser = serial.Serial(serPort,baudrate=115200,timeout=1)  # open serial port
# ser = serial.Serial(
#    port='/dev/ttyUSB0',\
#    baudrate=115200,\
#    parity=serial.PARITY_NONE,\
#    stopbits=serial.STOPBITS_ONE,\
#    bytesize=serial.EIGHTBITS,\
#    timeout=1)
print(ser.portstr)         # check which port was really used

def get_command(command):
    lines = []
    # just ensure command has newline 
    command = command.rstrip()
    command = command + '\r'
    print(command)
    ser.write(command.encode()) # write one char from an int
    done = False
    while ( not done ):
        line  = ser.readline().rstrip()
#        print(line, len(line))
        if ( len(line) and line[0] == '%' ) :
            done = True
        else :
            lines.append(line.decode())
    return lines

print(get_command("help"))
print(get_command("i2c_base 2"))
#enable 0x77 and 0x20, 0x21 via 0x70
print(get_command("i2cw 0x70 1 0xc1"))
#Ping 0x20 and 0x77 to make sure they are indeed enabled
print(get_command("i2cr 0x77 1"))
print(get_command("i2crr 0x20 0x06 1"))
#Setting Control Registers on U93 (TCA9555) to have  I/O port (P0-7 (0x02)) set as outputs (value 0))
print(get_command("i2cwr 0x20 0x06 1 0"))
if (o.mode == 0):
    print(get_command("i2cwr 0x20 0x02 1 00"))
elif (o.mode == 1):
    print(get_command("i2cwr 0x20 0x02 1 0f"))
else:
    print("BUG:mode number not supported!!!")

#if ser.is_open:
ser.close()
