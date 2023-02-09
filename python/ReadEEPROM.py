#!/usr/bin/env python 

import serial
import time
import io
import argparse
import os
import pdb

dir = os.path.dirname(os.path.abspath(__file__))

#parser = optparse.OptionParser()
parser = argparse.ArgumentParser()
# allow user to specify the config file of a specific synthesizer in upper/lower/mixed case
synth_choices = ["r0a", "r0b", "r1a", "r1b", "r1c"]
parser.add_argument("synth_id", type=str.lower, choices=synth_choices, help='[required] synthesizer to configure {R0A, R0B, R1A, R1B, R1C}')
# the required register list filename has to be an exact match
parser.add_argument('--pages', default='(0,1)', help='Specify the page ranges to read (preamble=0, reg=1-30, postamble=31')
parser.add_argument('--tty', default='ttyUSB0', help='Specify tty device. ttyUL1 for ZYNQ. ttyUSB0 or ttyUSB1 for CPU.')
parser.add_argument('--debug', action="store_true", default=False, help='Print debug statements')
parser.add_argument('--quiet', action="store_true", default=False, help='Do not print out get_command output')
parser.add_argument('--alpha', action="store_true", default=False, help='Enable registers for FF alpha-2 parts')
#o, a = parser.parse_args()

args = parser.parse_args()
page_i = int(args.pages.split(",")[0].strip("("))
page_f = int(args.pages.split(",")[1].strip(")"))
if args.synth_id == "r0a" :
    # SI5341 on mux channel 0 (mask = 0x01)
    # store 0x00-0x07F/0x80-0xFF registers on even/odd pages of 
    # 0x000-0x01F 
    eeprom_pages = [hex(i)[2:] for i in range(0,32)] 
elif args.synth_id == "r0b" :
    # SI5395 on mux channel 1 (mask = 0x02)
    eeprom_pages = [hex(i)[2:] for i in range(32,64)] 
elif args.synth_id == "r1a" :
    # SI5395 on mux channel 2 (mask = 0x04)
    eeprom_pages = [hex(i)[2:] for i in range(64,96)] 
elif args.synth_id == "r1b" :
    # SI5395 on mux channel 3 (mask = 0x08)
    eeprom_pages = [hex(i)[2:] for i in range(96,128)] 
elif args.synth_id == "r1c" :
    # SI5395 on mux channel 4 (mask = 0x10)
    eeprom_pages = [hex(i)[2:] for i in range(128,160)] 


serPort = "/dev/"+args.tty

ser = serial.Serial(serPort,baudrate=115200,timeout=1)  # open serial port
print(ser.portstr)         # check which port was really used
dump_file = open('ReadEEPROM_pages_'+args.synth_id+'.txt', 'w')
def get_command(command):
    lines = []
    # just ensure command has newline 
    command = command.rstrip()
    command = command + '\r\n'
    # show what will be sent to the board    
    #print(command)
    ser.write(command.encode()) # write one char from an int
    done = False
    # wait for the MCU to send back a "%" prompt    
    while ( not done ):
        line  = ser.readline().rstrip()
        if ( len(line) and chr(line[0]) == '%' ) :
            done = True
        else :
            lines.append(line.decode())
    return lines

#write to rev2 EEPROM
i2c_port = "2"
i2c_addr = "0x50"
#When 'noisy' print out returned data of get_command
def read_reg():
    dump_file.write("There are the following number of lines in preamble/reg/postamble lists (0xff(ff) for an unprogramed clock)\n")
    dump_file.write(get_command("i2crr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[31]+"7C"+" 1")[-1]+'\n') 
    dump_file.write(get_command("i2crr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[31]+"7D"+" 2")[-1]+'\n')
    dump_file.write(get_command("i2crr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[31]+"7F"+" 1")[-1]+'\n')
    dump_file.write("**** Below is the triplet registers already written to eeprom in specified range of pages ****\n") 
    for i in range(page_i,page_f): # feel free to specify the page you want to read out the registers (i.e. 0 for preamble list, 1-30 for register list, and 31 for posamble list) by --page      
        for j in range(126):
            if ( 0 < j < 16):
                command = "i2crr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[i]+"0"+str(hex(j).lstrip('0x'))+" 1"
            elif ( j == 0 ):
                command = "i2crr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[i]+"00"+str(hex(j).lstrip('0x'))+" 1" 
            else:
                command = "i2crr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[i]+str(hex(j).lstrip('0x'))+" 1"
            dump_file.write(get_command(command)[-1]+'\n')

# send 'help' command and print out results to show that the MCU is communicating
# print(get_command("help"))


# send the preamble, data, and postamble to the eeprom
def ReadEEPROM():
    # for the preamble, send all data    
    read_reg()

# send data off to eeprom
print(get_command("semaphore 2 take")[-1]) 
ReadEEPROM()

# close the tty port:
print(get_command("semaphore 2 release")[-1]) 
dump_file.close()
ser.close()
