import argparse
import sys
import apollo
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("tty", type=str, help="need one argument for a serial port name")
args = parser.parse_args()
ttydevice = args.tty 

fname = open('../data/dump_id_'+ttydevice+'.txt', 'r')
Lines = fname.readlines()

ID = Lines[1][3:-1]
CMXX = int(Lines[2][14:])
print("ID: "+str(ID))
print("CM board number: "+str(CMXX))
 
if int(ID)==0:
     ID = input("Please enter a new board ID: ")
     print("You entered ID: " + ID)
     dump_text = open("../data/dump_setid_"+ttydevice+".txt", "w")
     once = apollo.get_command('set_id 12345678 '+ID,ttydevice)
     for j in range(len(once)):
	dump_text.write(once[j] + "\n")
     dump_text.close()

output = subprocess.call(["../shell/set_cm_dir.sh",str(CMXX).zfill(2)])  
fname.close()

                
