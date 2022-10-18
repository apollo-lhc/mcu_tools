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
parser.add_argument("Reg_List", help='[required] Register List .csv file from ClockBuilderPRO')
parser.add_argument('--tty', default='ttyUSB0', help='Specify tty device. ttyUL1 for ZYNQ. ttyUSB0 or ttyUSB1 for CPU.')
parser.add_argument('--debug', action="store_true", default=False, help='Print debug statements')
parser.add_argument('--quiet', action="store_true", default=False, help='Do not print out get_command output')
parser.add_argument('--alpha', action="store_true", default=False, help='Enable registers for FF alpha-2 parts')
#o, a = parser.parse_args()

args = parser.parse_args()

if args.synth_id == "r0a" :
    # SI5341A
    # occupies 32 EEPROM pages 0x00-0x1f for one specified config file 
    eeprom_pages = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1A', '1B', '1C', '1D', '1E', '1F'] 
elif args.synth_id == "r0b" :
    # SI5395A
    # occupies 32 EEPROM pages 0x20-0x3f for one specified config file
    eeprom_pages = ['20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2A', '2B', '2C', '2D', '2E', '2F', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3A', '3B', '3C', '3D', '3E', '3F'] 
elif args.synth_id == "r1a" :
    # SI5341
    # occupies 32 EEPROM pages 0x40-0x5f for one specified config file
    eeprom_pages = ['40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4A', '4B', '4C', '4D', '4E', '4F', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5A', '5B', '5C', '5D', '5E', '5F'] 
elif args.synth_id == "r1b" :
    # SI5341
    # occupies 32 EEPROM pages 0x60-0x7f for one specified config file
    eeprom_pages = ['60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6A', '6B', '6C', '6D', '6E', '6F', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7A', '7B', '7C', '7D', '7E', '7F'] 
elif args.synth_id == "r1c" :
    # SI5341
    # occupies 32 EEPROM pages 0x80-0x9f for one specified config file
    eeprom_pages = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8A', '8B', '8C', '8D', '8E', '8F', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9A', '9B', '9C', '9D', '9E', '9F'] 


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
i2c_port = "2" # EEPROM I2C device #
i2c_addr = "0x50" # EEPROM I2C address
#When 'noisy' print out returned data of get_command
def write_reg(ListOfRegs,Page_i,Noisy):
    # Page_i initializes the start page of preamble/register/postamble list
    Page = Page_i
    counter = 0
    for register in ListOfRegs:
         
        if ( 0 < counter < 126): # the triplet version is assigned to have a maximum of 126 data or addresses per EEPROM page
            if (counter < 16):
                command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+"0"+str(hex(counter).lstrip('0x'))+" 1 "+register+"" 
            else:
                command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+str(hex(counter).lstrip('0x'))+" 1 "+register+""         
            if Noisy:
                print(get_command(command)[-1])
            else:
                get_command(command)
            counter += 1
        #reset counter and move on to the next page 
        else:
            if (counter != 0):
                Page += 1
            counter = 0
            # write the new page number to address 0x01  
            command = "i2cwr "+i2c_port+" "+i2c_addr+" 1 0x01 1 "+eeprom_pages[Page]+""
            if Noisy:
                print(get_command(command)[-1])
            else:
                get_command(command) 
            command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+"00"+" 1 "+register+""

            if Noisy:
                print(get_command(command)[-1])
            else:
                get_command(command) 
            counter += 1
    print(counter)
def write_counter(reg_counter,page_counter,nbyte,Page_i,Noisy):
    Page = Page_i 
    if (page_counter < 16):
        command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+"0"+str(hex(page_counter).lstrip('0x'))+" "+str(nbyte)+" "+str(hex(reg_counter).lstrip('0x'))+""
    else:
        command = "i2cwr "+i2c_port+" "+i2c_addr+" 2" +" 0x"+eeprom_pages[Page]+str(hex(page_counter).lstrip('0x'))+" "+str(nbyte)+" "+str(hex(reg_counter).lstrip('0x'))+""
    if Noisy:
        print(get_command(command)[-1])
    else:
        get_command(command) 
 
# send 'help' command and print out results to show that the MCU is communicating
print(get_command("help"))
# check the WP pin and set it to writable
print(get_command("gpio get ID_EEPROM_WP"))
print(get_command("gpio set ID_EEPROM_WP 0"))
print(get_command("gpio get ID_EEPROM_WP"))
# open csv files and create/initialize variables
regfile = open(args.Reg_List, 'r')

PreambleList = []
PostambleList = []
RegisterList = []
InPreamble = 0
InRegisters = 0
InPostamble = 0


# read the desired register settings from the "register" file
for line in regfile:
    for words in line.split('"'):
        reg_loc = words.find("0x")
        if (reg_loc == 0):
            reg = words[reg_loc:reg_loc+6]
        else:
            reg = words[:]
        val_loc = words.find("0x",reg_loc + 1)
        val = words[val_loc:val_loc+4]
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
def LoadClkConfig(PreList,RegList,PostList,Read): 
    # preamble list occupies the first page (e.g. page. 0x00 for r0a) of each clock 
    write_reg(PreList,0,Read)
    time.sleep(1) #only need 300 msec
    # register list occupies pages 2-31 (e.g. page 0x01-0x1e for r0a) of each clock
    write_reg(RegList,1,Read)
    time.sleep(1)
    # postamble list occupies the last page (e.g. page. 0x1f for r0a) of each clock
    write_reg(PostList,31,Read)
    # the sizes of the three lists are written to the last four addresses on the last page of each clock
    write_counter(int(len(PreList)/3),124,1,31,Read) # (e.g. write 1 byte to addr  0x1f7c for r0a) 
    write_counter(int(len(RegList)/3),125,2,31,Read)  # (e.g. write 2 bytes to addr  0x1f7d for r0a)
    write_counter(int(len(PostList)/3),127,1,31,Read) # (e.g. write 1 byte to addr  0x1f7f for r0a)

# send data off to eeprom
LoadClkConfig(PreambleList, RegisterList, PostambleList, not args.quiet)

# close the dump file
dump_file.close()
# close the tty port:
ser.close()
