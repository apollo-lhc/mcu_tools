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

fname = open("../data/dump_text_"+ttydevice+"_apollo"+str(xx).zfill(2)+"_"+time+".txt")
Lines = fname.readlines()

ID = Lines[1][3:-1]
CMXX = int(Lines[2][14:])
fname.close()
print("ID: "+str(ID))
print("CM board number: "+str(CMXX))
 
if int(ID)==0:
     uID = input("Please enter a new board ID: ")
     full_uID = str(uID).zfill(4)+"0000"
     print("You entered ID: " + full_uID)
     output0 = subprocess.call(["../shell/automate_apollo_set_board_ID.sh",ttydevice,str(xx).zfill(2),time,str(uID)])
     fname = open("../data/dump_text_"+ttydevice+"_apollo"+str(xx).zfill(2)+"_"+time+".txt","w")
     edit1 = list(full_uID)
     Lines[1] = Lines[1][:3] + full_uID + "\n" 
     Lines[2] = Lines[2][:14] + str(uID) + "\n"
     new_Lines = "".join(Lines)
     fname.write(new_Lines)
     CMXX = int(uID)
output1 = subprocess.call(["../shell/set_cm_dir.sh",str(CMXX).zfill(2),ttydevice,str(xx).zfill(2),time])  


                
