import re
import serial
#ttydevice = "/dev/ttyUL1"
ansi_esc = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def get_command(command,tty):
    ttydevice = "/dev/" + tty
    ser = serial.Serial(port=ttydevice, baudrate=115200, timeout=1) 
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

