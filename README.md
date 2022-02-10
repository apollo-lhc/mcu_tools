# mcu_tools
various tools for the boot loader.

* sflash: utility for loading the MCU firmware via UART
* minicomlogging: check statuses of a CM board on a given apollo blade via a tty device. 

## minicomlogging 
### requirments 
- **Python 2.7+**
- **pyserial** (for accessing a serial port of a tty device)

### instructions
#### Dump outputs from minicom to data/dump_*.txt. (note that the following commands are called implicitly by automate eyescan scripts in CU production script repo)  

``` sh
$ timestamp="$(date '+day-%d_time-%H.%M.%S')" 
$ python minicom_commands_dump_to_txt.py $ttyname $apollonumber $timestamp
```

example 1:
``` sh
$ timestamp="$(date '+day-%d_time-%H.%M.%S')" 
$ python minicom_commands_dump_to_txt.py ttyUL1 09 $timestamp
```
#### Evaluation of FPGAs' statuses is still a work-in-progress, though we used to have `check_tty_status.py` with a fixed reference from Apollo09 for that.  

