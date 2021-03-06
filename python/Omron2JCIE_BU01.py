# code from 
# https://github.com/hito4t/Omron2JCIE-BU01.git

import serial

class Omron2JCIE_BU01:
    def __init__(self, portName):
        self.__serial = serial.Serial(portName, 115200, timeout=1.0)

    def update(self):
        cmd = bytearray()

        # Header
        cmd.append(0x52)
        cmd.append(0x42)
        # Length
        cmd.append(0x05)
        cmd.append(0x00)

        # Payload
        #   Command
        cmd.append(0x01) # Read
        #   Address : Latest data Short
        cmd.append(0x22)
        cmd.append(0x50)

        # CRC-16
        crc = self.__crc16(cmd, 0, 7)
        cmd.append(crc & 0xFF)
        cmd.append((crc >> 8) & 0xFF)

        self.__serial.write(cmd)

        bytes = self.__serial.read(7)
        # Header
        if (self.__res_to_int16(bytes, 0) != 0x4252):
            raise IOError("Illegal response header :" + hex(self.__res_to_int16(bytes, 0)))

        # Length
        len = self.__res_to_int16(bytes, 2)

        # Command
        if (self.__b(bytes[4]) == 0x81):
            errorBytes = self.__serial.read(1)
            raise IOError("Read error :" + hex(self.__b(errorBytes[0])))

        bytes = self.__serial.read(len - 3)

        # 1-2 Temperature
        self.temperature = self.__res_to_int16(bytes, 1) * 0.01 # degC

        # 3-4 Relative humidity
        self.humidity = self.__res_to_int16(bytes, 3) * 0.01 # %

        # 5-6 Ambient light
        self.light = self.__res_to_int16(bytes, 5) # lx

        # 11-12 Sound noise
        self.noise = self.__res_to_int16(bytes, 11) * 0.01 # dB

        # 13-14 Sound noise
        self.eTVOC = self.__res_to_int16(bytes, 13) # ??

        # 7-10
        self.pressure = self.__res_to_int32(bytes,7) *0.001 # hPa


    def __crc16(self, bytes, fromIndex, toIndex):
        crc = 0xFFFF
        for i in range(fromIndex, toIndex):
            b = bytes[i]
            crc = crc ^ b
            for _ in range(0, 8):
                lsb = (crc & 1)
                crc = (crc >> 1) & 0x7FFF
                if lsb == 1:
                    crc = crc ^ 0xA001
        return crc


    def __res_to_int16(self, bytes, i):
        return self.__b(bytes[i]) | (self.__b(bytes[i + 1]) << 8)

    def __res_to_int32(self, bytes, i):
        return self.__b(bytes[i]) | (self.__b(bytes[i + 1]) << 8) | self.__b(bytes[i+2] << 16 ) | (self.__b(bytes[i + 3]) << 24)  


    def __b(self, b):
        # for supporting both old pySerial and new pySerial
        if type(b) is str:
            return ord(b)
        return b

    def close(self):
        self.__serial.close()
