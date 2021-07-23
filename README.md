# mcu_tools
various tools for the boot loader.

* sflash: utility for loading the MCU firmware via UART
* minicomlogging: check statuses of a current board via a tty device in comparision to Apollo09 as a reference

## minicomlogging 
### requirments 
- **Python 3+**
- **pyserial** (for accessing a serial port of a tty device)

### instructions
#### step 1: dump outputs from minicom to data/dump_text_*.txt where * is the tty device's name 
example 1:
``` sh
$ python3 minicom_commands_dump_to_txt.py ttyUL1
```
#### step 2: call a shell script (shell/diff.sh) to dump the different outputs to data/dump_diff_from_apollo09.txt, and check if the deviation is more than x% or not (x is a user specified variable in percent) 
``` sh
$ python3 check_tty_status.py dump_text_*.txt x
```
example 2:
``` sh
$ python3 check_tty_status.py dump_text_ttyUL1.txt 10.0
```
#### logging file: after step 2, it goes to output/check_yyyy-mm-dd-HH-MM-SS_*.txt. 
example 3 (check_2021-07-09-11-09-09_ttyUL1.txt): 
``` sh
READ_IOUT(ignored)                                                                                                      
SUPPLY KVCCINT1                                                                                                                 
VALUE 00.45     VALUE 00.08                                   | VALUE 00.30     VALUE 00.40                     
failed -> err : 33%                                                                                                     
failed -> err : 400%
...
```
showing the Kintex's output current(I) of a random board (second last two columns) that is different from the one on CM of Apollo09 (first two columns) by 33% (one supply) and 400% (another supply) columnwise. Note that the current logging only shows the outputs that are different from Apollo09 more than the threshold (x%), and we are currentlly ignore the IOUT outputs. 
