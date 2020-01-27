# sflash
Utility to update the boot loader via a UART interface. Based on the TI tool and modified, mainly to get rid of unused options.

## Usage
```bash
./sflash ~/cm_mcu.bin -p 0x4000 -r 0x4000 -c /dev/ttyUSB2 -b 115200 -d -s 252
```

Note that the -p argument _must_ be set to 0x4000. The 'turn off autobaud' option `-d` is accepted but does not do anything (it's off by default and there is no way to turn it on.)

The TI source code allows you to update the boot loader itself; this is not implemented in the boot loader that runs on the MCU.
