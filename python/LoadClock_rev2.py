#!/usr/bin/env python 

import serial
import time
import io
import optparse
import os
import re

dir = os.path.dirname(os.path.abspath(__file__))

parser = optparse.OptionParser()
#synth_choices = ["r0a", "r0b", "r1a", "r1b", "r1c"]
#parser.add_argument("synth_id", type=str.lower, choices=synth_choices, help='[required] synthesizer to configure {R0A, R0B, R1A, R1B, R1C}')
parser.add_option('--RegisterList', dest="Reg_List", default=dir+'/../data/Si5430_RevD_reg_In3_312p195122MHz_nozeros.txt',help='Base path of Register List.')
parser.add_option('--tty', dest="tty_device", default='ttyUSB0', help='Specify tty device. ttyUL1 for ZYNQ. ttyUSB0 or ttyUSB1 for CPU.')
parser.add_option('--debug', action="store_true", dest="Debug", default=False,help='Print debug statementss')
parser.add_option('--quiet', action="store_true", dest="Quiet", default=False,help='Do not print out get_command output')
parser.add_option('--alpha', action="store_true", dest="Alpha", default=False,help='Enable registers for FF alpha-2 parts')

o, a = parser.parse_args()

serPort = "/dev/"+o.tty_device

ser = serial.Serial(serPort,baudrate=115200,timeout=0.05)  # open serial port
# ser = serial.Serial(
#    port='/dev/ttyUSB0',\
#    baudrate=115200,\
#    parity=serial.PARITY_NONE,\
#    stopbits=serial.STOPBITS_ONE,\
#    bytesize=serial.EIGHTBITS,\
#    timeout=1)
print(ser.portstr)         # check which port was really used

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def get_command(command):
    lines = []
    # just ensure command has newline 
    command = command.rstrip()
    command = command + '\r\n'
    print(command)
    ser.write(command.encode()) # write one char from an int
    done = False
    # wait for the MCU to send back a "%" prompt
    iters = 0
    while ( not done ):
        if o.tty_device == "ttyUL1":
            line  = ser.readline().rstrip()
        else:
            line  = ser.readline().rstrip().decode("utf-8") 
        line = ansi_escape.sub('', line)
        if ( len(line) and line[0] == '%' ) :
            done = True
        else :
            if o.tty_device == "ttyUL1":
                lines.append(line.decode())
            else:
                lines.append(line)
        iters = iters + 1
        if ( iters > 10 ) :
            print("stuck: ", line.decode(), iters)
            ser.write(command.encode())
    return lines

#write to ClockSynthesizer at 0x77
#When Read print out output of get_command
def write_reg(ListOfRegs,Read):
    HighByte = -1
    for register in ListOfRegs:
        ChangePage = True if int(register[0][2:4],16)!=HighByte else False
        HighByte = int(register[0][2:4],16)
        if ChangePage:
            command = "i2cwr 2 0x77 1 0x01 1 "+register[0][0:4]+""
            if Read:
                print(get_command(command))
            else:
                get_command(command)
        command = "i2cwr 2 0x77 1 0x"+register[0][4:6]+" 1 "+register[1]+""
        if Read:
            print(get_command(command))
        else:
            get_command(command)
    #Set page back to 0 in the end
    if Read:
        print(get_command("i2cwr 2 0x77 1 0x01 1 0"))
    else:
        get_command("i2cwr 2 0x77 1 0x01 1 0")
        
#enable 0x77 and 0x20, 0x21 via 0x70
print(get_command("i2cw 2 0x70 1 0xc1"))
#Ping 0x20 and 0x77 to make sure they are indeed enabled
print(get_command("i2cr 2 0x77 1"))
print(get_command("i2crr 2 0x20 1 0x06 1"))
#Setting Control Registers on U93 (TCA9555) to have all I/O ports (P0-7 (0x02),P10-17 (0x03)) set as outputs (value 0))
print(get_command("i2cwr 2 0x20 1 0x06 1 0"))
print(get_command("i2cwr 2 0x20 1 0x07 1 0"))
#Configuring clock muxes for xcvrs via 0x20
print(get_command("i2cwr 2 0x20 1 0x02 1 20"))
print(get_command("i2cwr 2 0x20 1 0x02 1 A0"))
#Configuring Clock Synthesizer chip (enable and reset) via 0x20
print(get_command("i2cwr 2 0x20 1 0x03 1 00"))
#print(get_command("i2cwr 2 0x20 0x03 1 01"))
#Clear sticky flags of clock synth status monitor (raised high after reset)
#print(get_command("i2cwr 0x77 0x01 1 0"))
#print(get_command("i2cwr 0x77 0x11 1 0"))

# print(get_command("i2cwr 2 0x20 0x06 1 0x70"))  # 01110000 [P07..P00]
# print(get_command("i2cwr 2 0x20 0x07 1 0xc2"))  # 11000010 [P17..P10]
# print(get_command("i2cwr 2 0x20 0x02 1 0x80"))  # 10000000 [P07..P00]
# print(get_command("i2cwr 2 0x20 0x03 1 0x01"))  # 00000001 [P17..P10]
# print(get_command("i2cwr 2 0x21 0x06 1 0x70"))  # 01110000 [P07..P00]
# print(get_command("i2cwr 2 0x21 0x07 1 0x00"))  # 00000000
# print(get_command("i2cwr 2 0x21 0x02 1 0x80"))  # 10000000
# print(get_command("i2cwr 2 0x21 0x03 1 0x03"))  # 00000011

# print(get_command("i2cw 4 0x70 1 0x80"))
# print(get_command("i2cwr 4 0x20 0x06 1 0xff"))  # 11111111 [P07..P00]
# print(get_command("i2cwr 4 0x20 0x07 1 0xff"))  
# print(get_command("i2cw 4 0x71 1 0x40"))
# print(get_command("i2cwr 4 0x21 0x06 1 0xff"))  # 11111111 [P07..P00]
# print(get_command("i2cwr 4 0x21 0x07 1 0xf0"))

if o.Alpha:
    #enable 10011111 = 9f
    #enable 10000000 = 80
    print(get_command("i2cw 4 0x71 1 0x40"))
    print(get_command("i2cwr 4 0x21 1 0x07 1 0xf0"))
#    print(get_command("i2cwr 4 0x21 1 0x03 1 0x7c"))
#    print(get_command("i2cwr 4 0x21 1 0x03 1 0x7d"))
    print(get_command("i2cwr 4 0x21 1 0x03 1 0x7e"))
    print(get_command("i2cwr 4 0x21 1 0x03 1 0x7f"))
    print(get_command("i2cw 4 0x71 1 0x00"))

PreambleList=[("0x0B24","0xC0"),
              ("0x0B25","0x00"),
              ("0x0502","0x01"),
              ("0x0505","0x03"),
              ("0x0957","0x17"),
              ("0x0B4E","0x1A")]

PostambleList=[("0x001C","0x01"),
               ("0x0B24","0xC3"),
               ("0x0B25","0x02")]

regfile=open(o.Reg_List, 'r')
RegisterList =[]
for line in regfile:
    for words in line.split('"'):
        reg_loc = words.find("0x")
        reg = words[reg_loc:reg_loc+6]
        if o.Debug:
            print(reg)
        val_loc = words.find("0x",reg_loc + 1)
        val = words[val_loc:val_loc+4]
        if o.Debug:
            print(words[val_loc:val_loc+4])
        RegisterList.append((reg,val))
if o.Debug:
    print(RegisterList)

def LoadClock(PreList,RegList,PostList,Read):
    write_reg(PreList,Read)
    time.sleep(1) #only need 300 msec
    write_reg(RegList,Read)
    time.sleep(1)
    write_reg(PostList,Read)

LoadClock(PreambleList, RegisterList, PostambleList, not o.Quiet)
print(get_command("i2cw 2 0x70 1 0x00"))

#if ser.is_open:
ser.close()
