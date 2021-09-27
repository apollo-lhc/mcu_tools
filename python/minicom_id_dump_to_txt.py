import apollo
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("tty", type=str, help="need one argument for a serial port name")
#parser.add_argument('-v', "--verbose", help="a serial port name")
args = parser.parse_args()

ttydevice = args.tty

minicom_commands = ['id']
dump_text = open("../data/dump_id_"+ttydevice+".txt", "w")

for i in range(len(minicom_commands)):
    once = apollo.get_command(minicom_commands[i],ttydevice)
    for j in range(len(once)):
        dump_text.write(once[j] + "\n")
    
dump_text.close()

