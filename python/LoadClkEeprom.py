#! /usr/bin/env python

import time
import argparse
import os
import sys
import serial

### CONSTANTS ###
I2C_PORT = 2
I2C_DEVICE_ADDR = 0x50
I2C_ADDR_BYTES = 2
I2C_DATA_BYTES = 1

EEPROM_MAX_TRIPLES = 126
EEPROM_REGL_ADDR   = 0x7D
EEPROM_PREL_ADDR   = 0x7C
EEOMRP_POSTL_ADDR  = 0x7F
NPAGES_PER_CONFIG = 32


# parse command line arguments
parser = argparse.ArgumentParser()
# allow user to specify the config file of a specific synthesizer in upper/lower/mixed case
synth_choices = ["r0a", "r0b", "r1a", "r1b", "r1c"]
parser.add_argument("synth_id", type=str.lower, choices=synth_choices, help='[required] synthesizer to configure {R0A, R0B, R1A, R1B, R1C}')
# the required register list filename has to be an exact match
parser.add_argument("Reg_List", help='[required] Register List .csv or txt file from ClockBuilderPRO')
parser.add_argument('--tty', default='ttyUSB0', help='Specify tty device. ttyUL1 for ZYNQ. ttyUSB0 or ttyUSB1 for CPU.')
parser.add_argument('--debug', action="store_true", default=False, help='Print debug statements')
parser.add_argument('--quiet', action="store_true", default=False, help='Do not print out get_command output')
parser.add_argument('--alpha', action="store_true", default=False, help='Enable registers for FF alpha-2 parts')
parser.add_argument('--dry-run', action="store_true", default=False, help='Perform a dry run without writing to EEPROM')

args = parser.parse_args()



if args.synth_id == "r0a" :
    # SI5341A (Rev2) or SI5395A (Rev3)
    # occupies 32 EEPROM pages 0x00-0x1f for one specified config file 
    eeprom_pages = list(range(NPAGES_PER_CONFIG))
elif args.synth_id == "r0b" :
    # SI5395A
    # occupies 32 EEPROM pages 0x20-0x3f for one specified config file
    eeprom_pages = list(range(NPAGES_PER_CONFIG, 2 * NPAGES_PER_CONFIG))
elif args.synth_id == "r1a" :
    # SI5395A
    # occupies 32 EEPROM pages 0x40-0x5f for one specified config file
    eeprom_pages = list(range(2 * NPAGES_PER_CONFIG, 3 * NPAGES_PER_CONFIG))
elif args.synth_id == "r1b" :
    # SI5341
    # occupies 32 EEPROM pages 0x60-0x7f for one specified config file
    eeprom_pages = list(range(3 * NPAGES_PER_CONFIG, 4 * NPAGES_PER_CONFIG))
elif args.synth_id == "r1c" :
    # SI5341
    # occupies 32 EEPROM pages 0x80-0x9f for one specified config file
    eeprom_pages = list(range(4 * NPAGES_PER_CONFIG, 5 * NPAGES_PER_CONFIG))
else : # should never get here
    print(f"Error: Invalid synthesizer ID {args.synth_id}.")
    sys.exit(1)

# parse the input file
def parse_input_file(fname: str) -> tuple:
    """Parse the input file and extract the preamble, register, and postamble data."""
    PreambleList = []
    RegisterList = []
    PostambleList = []

    # States to track which section we are in
    InPreamble = False
    InRegisters = False
    InPostamble = False

    with open(fname, 'r', encoding="ascii") as f:
        for line in f:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Detect section transitions in comments
            if line.startswith("#"):
                if "Start configuration preamble" in line:
                    InPreamble = True
                    continue
                elif "End configuration preamble" in line:
                    InPreamble = False
                    continue
                elif "Start configuration registers" in line:
                    InRegisters = True
                    continue
                elif "End configuration registers" in line:
                    InRegisters = False
                    continue
                elif "Start configuration postamble" in line:
                    InPostamble = True
                    continue
                elif "End configuration postamble" in line:
                    InPostamble = False
                    continue

            # Parse the line into address and data. Skip line if it is a header
            # the header line does not have a 0x in it.
            if "," in line and '0x' in line:
                address, data = line.split(",")
                address = address.strip()
                data = int(data.strip(), 16) # Convert data to integer base 16

                # Split the address into upper and lower bytes
                address_int = int(address, 16) # Convert address to integer base 16
                upper_byte = (address_int >> 8) & 0xFF
                lower_byte = address_int & 0xFF

                # Add the parsed data to the appropriate list
                if InPreamble:
                    PreambleList.append([upper_byte, lower_byte, data])
                elif InRegisters:
                    RegisterList.append([upper_byte, lower_byte, data])
                elif InPostamble:
                    PostambleList.append([upper_byte, lower_byte, data])
    return PreambleList, RegisterList, PostambleList


# a wrapper to write to the EEPROM
def write_triplet_to_eeprom(address: int, triplet: list) -> None:
    """Write a triplet (address, data) to the EEPROM."""
    # loop through the triplet
    for data in triplet:
        if args.debug:
            print(f"Writing to address {address}: >{data}< {type(data)} {triplet}")
        # convert the data to an integer
        command = f"i2cwr {I2C_PORT:02x} {I2C_DEVICE_ADDR:02x} {address:02x} {I2C_ADDR_BYTES} {data:02x} {I2C_DATA_BYTES}"
        address += 1
        if not args.quiet:
            print(f"Writing: {command}")
        response = get_command(command)
        if not args.quiet:
            print(f"Response: {response}")

def get_command(command: str) -> list:
    """Send a command to the serial port and read the response."""
    lines = []
    # just ensure command has newline
    command = command.rstrip()
    command = command + '\r\n'
    # show what will be sent to the board
    dump_file.write(command)
    if args.dry_run:
        print(f"DRYRUN: {command}")
        return [command]
    ser.write(command.encode())
    done = False
    iters = 0
    # wait for the MCU to send back a "%" prompt
    while not done:
        line  = ser.readline().rstrip()
        if ( len(line) > 0 and line[0] == 37 ) :
            done = True
        else :
            lines.append(line.decode())

        iters = iters + 1
        if iters > 10 :
            print("stuck: ", line.decode(), iters)
            ser.write(command.encode())
    return lines

# write the register list to the EEPROM
def write_register_list(register_list: list, start_page: int) -> None:
    """Write the register list to the EEPROM starting from the specified page."""
    counter = 0
    page = start_page
    for triplet in register_list:
        if len(triplet) != 3:
            print(f"Invalid triplet: {triplet}")
            return
        address = (page << 16) | counter
        write_triplet_to_eeprom(address, triplet)
        address += 1
        counter += 1
        if counter >= 126:
            # reset counter and move on to the next page
            counter = 0
            start_page += 1

def disable_write_protect() -> None:
    """Disable write protect on the EEPROM."""
    # check the WP pin and set it to writable
    print(get_command("gpio get ID_EEPROM_WP")[-1])
    print(get_command("gpio set ID_EEPROM_WP 0")[-1])
    print(get_command("gpio get ID_EEPROM_WP")[-1])
    print(get_command("semaphore 2 take")[-1])

####################################################################################
# main program starts here
####################################################################################
# open the configuration file passed in and parse it

dump_file = open("dump.txt", "w", encoding="ascii")
if args.debug:
    print("Opening input file:", args.Reg_List)

input_file = args.Reg_List
if not os.path.isfile(input_file):
    print(f"Error: File {input_file} does not exist.")
    sys.exit(1)
PreambleList, RegisterList, PostambleList = parse_input_file(input_file)
if args.debug:
    print("Preamble List:", PreambleList)
    print("Register List:", RegisterList)
    print("Postamble List:", PostambleList)

# save the length of the lists
len_preamble = len(PreambleList)
len_register = len(RegisterList)
len_postamble = len(PostambleList)
if args.debug:
    print(f"Preamble List Length: {len_preamble}")
    print(f"Register List Length: {len_register}")
    print(f"Postamble List Length: {len_postamble}")

# open the serial port, if not dry_run
if not args.dry_run:
    ser = serial.Serial(
        port='/dev/' + args.tty,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=.05)

    print(ser.portstr)         # check which port was really used

# write the three lists to the EEPROM
if args.debug:
    print("Writing Preamble List to EEPROM...")
write_register_list(PreambleList, eeprom_pages[0])
time.sleep(0.4) 
if args.debug:
    print("Writing Register List to EEPROM...")
write_register_list(RegisterList, eeprom_pages[1])
time.sleep(0.4) 
if args.debug:
    print("Writing Postamble List to EEPROM...")
write_register_list(PostambleList, eeprom_pages[-1])

# write the length of the lists to the EEPROM
if args.debug:
    print("Writing lengths to EEPROM...")
ADDRS = [EEPROM_PREL_ADDR, EEPROM_REGL_ADDR, EEOMRP_POSTL_ADDR]
LENS = [len_preamble, len_register, len_postamble]
for addr, length in zip(ADDRS, LENS):
    command = f"i2cwr {I2C_PORT} {I2C_DEVICE_ADDR} {addr} {I2C_ADDR_BYTES} {length:02x} {I2C_DATA_BYTES}"
    if args.debug:
        print(f"Writing: {command}")
    response = get_command(command)
    if not args.quiet:
        print(f"Response: {response}")

# release the semaphore
if args.debug:
    print("Releasing semaphore...")
print(get_command("semaphore 2 release")[-1])

# exit
if not args.dry_run:
    ser.close()