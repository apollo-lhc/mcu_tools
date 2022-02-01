import argparse
import sys
import apollo
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("tty", type=str, help="need one argument for a serial port name")
parser.add_argument("apxx", type=int, help="need one argument for apollo##")
parser.add_argument("timestamp", type=str, help="need one argument for timestamp")

args = parser.parse_args()
ttydevice = args.tty
xx = args.apxx 
time = args.timestamp

fname = open("../data/dump_text_"+ttydevice+"_apollo"+str(xx).zfill(2)+"_"+time+".txt", 'r')
Lines = fname.readlines()

ID = Lines[1][3:-1]
CMXX = int(Lines[2][14:])
print("ID: "+str(ID))
print("CM board number: "+str(CMXX))
 
if int(ID)==0:
     ID = input("Please enter a new board ID: ")
     print("You entered ID: " + ID)
     dump_text = open("../data/dump_setid_"+ttydevice+"_apollo"+str(xx).zfill(2)+"_"+time+".txt", "w")
     once = apollo.get_command('set_id 12345678 '+ID,ttydevice)
     for j in range(len(once)):
          dump_text.write(once[j] + "\n")
     dump_text.close()

output = subprocess.call(["../shell/set_cm_dir.sh",str(CMXX).zfill(2),ttydevice,str(xx).zfill(2),time])  
fname.close()

                
