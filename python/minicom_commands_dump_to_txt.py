import apollo
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("tty", type=str, help="need one argument for a serial port name")
parser.add_argument("apxx", type=int, help="need one argument for apollo##")
parser.add_argument("timestamp", type=str, help="need one argument for timestamp")
#parser.add_argument('-v', "--verbose", help="a serial port name")
args = parser.parse_args()

ttydevice = args.tty
xx = args.apxx
time = args.timestamp


minicom_commands = ['id','ff', 'adc','ff_status','psmon 1','psmon 2','psmon 3','psmon 4', 'psmon 5', 'psmon 6', 'errorlog 64', 'uptime', 'task info']
dump_text = open("../data/dump_text_"+ttydevice+"_apollo"+str(xx).zfill(2)+"_"+time+".txt", "w")
print(dump_text)
for i in range(len(minicom_commands)):
    once = apollo.get_command(minicom_commands[i],ttydevice)
    for j in range(len(once)):
        dump_text.write(once[j] + "\n")
    
dump_text.close()

