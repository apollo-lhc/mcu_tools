#!/usr/bin/env python 

import serial
import time
import io
import argparse
import os
import pdb
import numpy as np
import pandas as pd

dir = os.path.dirname(os.path.abspath(__file__))

#parser = optparse.OptionParser()
parser = argparse.ArgumentParser()
# allow user to specify the config file of a specific synthesizer in upper/lower/mixed case
synth_choices = ["r0a", "r0b", "r1a", "r1b", "r1c"]
parser.add_argument("synth_id", type=str.lower, choices=synth_choices, help='[required] synthesizer to configure {R0A, R0B, R1A, R1B, R1C}')
# the required register list filename has to be an exact match
parser.add_argument("Reg_List", help='[required] Register List .csv file from ClockBuilderPRO')
parser.add_argument('--tty', default='ttyUSB0', help='Specify tty device. ttyUL1 for ZYNQ. ttyUSB0 or ttyUSB1 for CPU.')
parser.add_argument('--debug', action="store_true", default=False, help='Print debug statements')
parser.add_argument('--quiet', action="store_true", default=False, help='Do not print out get_command output')
parser.add_argument('--alpha', action="store_true", default=False, help='Enable registers for FF alpha-2 parts')
#o, a = parser.parse_args()

args = parser.parse_args()

if args.synth_id == "r0a" :
    # SI5341 on mux channel 0 (mask = 0x01)
    # even(odd) page 0x00-0x1e for address 0x00-0x7f(0x80-0xff) 
    eeprom_pages = [np.base_repr(i,base=16) for i in np.arange(0,32,1,dtype=np.uint8)] 
elif args.synth_id == "r0b" :
    # SI5395 on mux channel 1 (mask = 0x02)
    # even(odd) page 0x20-0x3e for address 0x00-0x7f(0x80-0xff) 
    eeprom_pages = [np.base_repr(i,base=16) for i in np.arange(32,64,1,dtype=np.uint8)] 
elif args.synth_id == "r1a" :
    # SI5395 on mux channel 2 (mask = 0x04)
    # even(odd) page 0x40-0x5e for address 0x00-0x7f(0x80-0xff) 
    eeprom_pages = [np.base_repr(i,base=16) for i in np.arange(64,96,1,dtype=np.uint8)] 
elif args.synth_id == "r1b" :
    # SI5395 on mux channel 3 (mask = 0x08)
    # even(odd) page 0x60-0x7e for address 0x00-0x7f(0x80-0xff) 
    eeprom_pages = [np.base_repr(i,base=16) for i in np.arange(96,128,1,dtype=np.uint8)] 
elif args.synth_id == "r1c" :
    # SI5395 on mux channel 4 (mask = 0x10)
    # even(odd) page 0x80-0x9e for address 0x00-0x7f(0x80-0xff) 
    eeprom_pages = [np.base_repr(i,base=16) for i in np.arange(128,160,1,dtype=np.uint8)] 


serPort = "/dev/"+args.tty

ser = serial.Serial(serPort,baudrate=115200,timeout=1)  # open serial port
print(ser.portstr)         # check which port was really used
dump_file = open('LoadConfig_tripletEEPROM_Clk'+args.synth_id+'.txt', 'w') 
def get_command(command):
    lines = []
    # just ensure command has newline 
    command = command.rstrip()
    command = command + '\r\n'
    # show what will be sent to the board    
    dump_file.write(command)  
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
def write_reg(ListOfRegs,Page_i,Noisy):
    # HighByte = -1
    # Page_i controls the start page of preamble/registers/postamble
    Page = Page_i
    counter = 0
    for register in ListOfRegs:
         
        if ( 0 < counter < 126):
            if (counter < 16):
                command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+str(np.base_repr(counter,16,padding=1))+" 1 "+register+"" 
            else:
                command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+str(np.base_repr(counter,16))+" 1 "+register+""         
            if Noisy:
                print(get_command(command))
            else:
                get_command(command)
            counter += 1
        #reset 
        else:
            if (counter != 0):
                Page += 1
            counter = 0
            # write the new page number to address 0x01  
            command = "i2cwr "+i2c_port+" "+i2c_addr+" 1 0x01 1 "+eeprom_pages[Page]+""
            if Noisy:
                print(get_command(command))
            else:
                get_command(command) 
            command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+str(np.base_repr(counter,16,padding=2))+" 1 "+register+""

            if Noisy:
                print(get_command(command))
            else:
                get_command(command) 
            counter += 1
def write_counter(reg_counter,page_counter,nbyte,Page_i,Noisy):
    Page = Page_i 
    if (page_counter < 16):
        command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+str(np.base_repr(page_counter,16,padding=1))+" "+str(nbyte)+" "+str(np.base_repr(reg_counter,16))+""
    else:
        command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+str(np.base_repr(page_counter,16))+" "+str(nbyte)+" "+str(np.base_repr(reg_counter,16))+""
    if Noisy:
        print(get_command(command))
    else:
        get_command(command) 
 
# send 'help' command and print out results to show that the MCU is communicating
print(get_command("help"))
# check the WP pin and set it to writable
print(get_command("gpio get ID_EEPROM_WP"))
print(get_command("gpio set ID_EEPROM_WP 0"))
print(get_command("gpio get ID_EEPROM_WP"))
# open csv files and create/initialize variables
df = pd.read_csv(args.Reg_List, header=None, delimiter=',', names=['Address','Data'])
Address_List = df['Address'].tolist()
Data_List = df['Data'].tolist()
PreambleList = []
PostambleList = []
RegisterList = []
InPreamble = 0
InRegisters = 0
InPostamble = 0


# read the desired register settings from the "register" file
    
for i in range(len(Address_List)): 
    reg = Address_List[i]
    val = Data_List[i] 
    # append the register address and value to the appropriate list
    if (reg.find("Start") != -1 and reg.find("preamble") != -1):
        InPreamble = 1
        continue
    if (reg.find("End") != -1 and reg.find("preamble") != -1):
        InPreamble = 0
        continue
    if (reg.find("Start") != -1 and reg.find("register") != -1):
        InRegisters = 1
        continue
    if (reg.find("End") != -1 and reg.find("register") != -1):
        InRegisters = 0
        continue
    if (reg.find("Start") != -1 and reg.find("postamble") != -1):
        InPostamble = 1
        continue
    if (reg.find("End") != -1 and reg.find("postamble") != -1):
        InPostamble = 0
        break
    if InPreamble:
        if ("0x" in reg and val):
            PreambleList.append(reg[2:4])
            PreambleList.append(reg[4:6])
            PreambleList.append(val)
    elif InRegisters:
        if ("0x" in reg and val):
            RegisterList.append(reg[2:4]) 
            RegisterList.append(reg[4:6])
            RegisterList.append(val)  
    elif InPostamble:
        if ("0x" in reg and val):
            PostambleList.append(reg[2:4])
            PostambleList.append(reg[4:6])
            PostambleList.append(val)

                 
# send the preamble, data, and postamble to the eeprom
def LoadClkConfigs(PreList,RegList,PostList,Read):
    # for the preamble, send all data   
    # preamble occupies the first even page (e.g. page. 0x00) of each clock 
    write_reg(PreList,0,Read)
    time.sleep(1) #only need 300 msec
    # registers occupies 2-31 pages (include even and odd pages) of each clock
    write_reg(RegList,1,Read)
    time.sleep(1)
    # for the postamble, send all data
    # postamble occupies the last even page (e.g. page. 0x1e) of each clock
    write_reg(PostList,31,Read)
    write_counter(int(len(PreList)/3),124,1,31,Read)
    write_counter(int(len(RegList)/3),125,2,31,Read) 
    write_counter(int(len(PostList)/3),127,1,31,Read)

# send data off to eeprom
LoadClkConfigs(PreambleList, RegisterList, PostambleList, not args.quiet)

# close the dump file
dump_file.close()
# close the tty port:
ser.close()
