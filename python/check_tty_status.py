import argparse 
import subprocess
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('file2', type=str, help="need one argument for a file to compare with appolo09 outputs")
parser.add_argument('err', type=float, help="err threshold(%) that is still acceptable for the two different ouputs")

args = parser.parse_args()

file2 = args.file2
err = args.err

def timeStamped(fname, fmt='{fname}_%Y-%m-%d-%H-%M-%S_'):
    return datetime.datetime.now().strftime(fmt).format(fname=fname)
#cmd = ["diff -a --suppress-common-lines -y", "dump_text_apollo09_ttyUL1.txt", file2]
#ps = subprocess.Popen(("diff", "-a", "--suppress-common-lines", "-y", "dump_text_apollo09_ttyUL1.txt", file2), stdout = subprocess.PIPE)
command_lines = [2,24,47,68,80,92,104,116,128,140,201,203]
command_names = ["FF temperature", "ADC outputs", "FIREFLY STATUS", "READ_TEMPERATURE_3", "READ_VIN", "READ_VOUT","READ_IOUT(ignored)","STATUS_WORD","OT_FAULT_LIMIT","Entries in EEPROM buffer","uptime","task info"]
output = subprocess.call(["../shell/diff.sh",'../data/'+file2])
print(output)


diff_file = open('../data/dump_diff_from_apollo09.txt', 'r')
Lines = diff_file.readlines()

fname1 = open('../data/dump_text_apollo09_ttyUL1.txt', 'r')
Lines1 = fname1.readlines()

fname2 = open('../data/'+file2,'r')
Lines2 = fname2.readlines()


n = 0
output_file = open('../output/'+timeStamped('check')+file2.split('_')[-1],'w')
for line in Lines:
    two_files_list = line.split('|')
    apollo09_list = two_files_list[0].split()
    file2_list = two_files_list[1].split()
    ls_err = [] 
    error_name = ""
    for name in command_names:
        n = int(apollo09_list[0])
        if int(apollo09_list[0]) > command_lines[command_names.index(name)] :
            error_name = name
    if len(apollo09_list) - len(file2_list) == 1 :
    	for i in range(len(apollo09_list)-1):
            if apollo09_list[i+1] != file2_list[i]:
                apollo09_value = float(apollo09_list[i+1])
                file2_value = float(file2_list[i])
                if abs((file2_value - apollo09_value)*100/apollo09_value) > err :
                    ls_err.append(str(round(abs((file2_value - apollo09_value)*100/apollo09_value)))+"%")
    else :
        n = int(apollo09_list[0])
        ls_err.append('non-numeric difference')
    if len(ls_err) > 0 :
        output_file.write(error_name+"\n")
        if 'VALUE' in apollo09_list :
            output_file.write(Lines1[n-2])
        output_file.write(line.replace(str(n),''))
        output_file.writelines("failed -> err : %s\n" % item for item in ls_err)

diff_file.close()
output_file.close()

                
