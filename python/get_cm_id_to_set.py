import argparse
import sys
import apollo
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("tty", type=str, help="need one argument for a serial port name")
parser.add_argument("apxx", type=int, help="need one argument for apollo##")
parser.add_argument("timestamp", type=str, help="need one argument for timestamp")
parser.add_argument("userID", type=str, help="need one argument for a new board ID")

args = parser.parse_args()
ttydevice = args.tty
xx = args.apxx 
time = args.timestamp
uID = args.userID
 

dump_text = open("../data/dump_setid_"+ttydevice+"_apollo"+str(xx).zfill(2)+"_"+time+".txt", "w")
print("new ID: "+str(uID).zfill(4)+"0000") 
once = apollo.get_command('set_id 12345678 '+str(44)+' '+uID,ttydevice)
for j in range(len(once)):
     dump_text.write(once[j] + "\n")
dump_text.close()
  


                
