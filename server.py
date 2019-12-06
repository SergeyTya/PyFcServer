import sys

import serial.tools.list_ports
import minimalmodbus
import struct
from collections import deque


class Server:
    class ServerError(Exception):
        pass

    class Device:

        def __init__(self, device):
            self.device = device
            self.holdings = []
            self.inputs = []
            self.scope_maxlen = 10000
            self.scope_fifo = [deque([0] * self.scope_maxlen, maxlen=self.scope_maxlen) for i in range(4)]
            self.scope_timeline = deque([0] * self.scope_maxlen, maxlen=self.scope_maxlen)

    def read_scope(self, args):
        curdev = 0
        try:
            curdev = int(args[1])
        except (ValueError, IndexError):
            pass
        if (curdev + 1) > len(self.devices):
            raise self.ServerError("Select another device. Available ", len(self.devices))

        while True:
            try:
                buf = bytearray(map(ord, self.devices[curdev].device._perform_command(20, '\x01\x01\x01')))
                fifo = buf.pop()
                if fifo == 6: print("Scope FIFO overload")
                chnum = buf.pop()
                period = buf.pop()
                buf = struct.unpack('>' + 'h' * (len(buf) // 2), buf)

                if chnum != len(self.devices[curdev].scope_fifo):
                    self.devices[curdev].scope_fifo.clear()
                    self.devices[curdev].scope_fifo = [
                        deque([0] * self.devices[curdev].scope_maxlen,
                              maxlen=self.devices[curdev].scope_maxlen) for i in range(chnum)]
                    self.devices[curdev].scope_timeline = deque(
                        [0] * self.devices[curdev].scope_maxlen,
                        maxlen=self.devices[curdev].scope_maxlen)

                for i in range(chnum):
                    self.devices[curdev].scope_fifo[i].extend(buf[i::chnum])

                t0 = self.devices[curdev].scope_timeline[-1]

                rng = range(0, self.devices[curdev].scope_maxlen)
                rng = map(lambda x: t0+x*period*0.001, rng)
                self.devices[curdev].scope_timeline.extend(rng)
            except (minimalmodbus.SlaveDeviceBusyError, minimalmodbus.InvalidResponseError): return True

    def read_register(self, args):

        curdev = 0
        register_to_read = 0
        function_code = 4

        if len(self.devices) == 0: raise self.ServerError("Device not found")
        try:
            curdev = int(args[1])
        except (ValueError, IndexError): pass
        try:
            register_to_read = int(args[2])
        except (ValueError, IndexError): pass

        try:
            function_code = int(args[3])
        except (ValueError, IndexError): pass

        if (curdev+1) > len(self.devices):
            raise self.ServerError("Select another device. Available ", len(self.devices))

        # device register list initialization
        if (len(self.devices[curdev].inputs) == 0) | (len(self.devices[curdev].holdings) == 0):
            tmp = self.devices[curdev].device.read_registers(0, 2, functioncode=4)
            self.devices[curdev].inputs = [0] * tmp[0]
            self.devices[curdev].holdings = [0] * tmp[1]

        buff = {4: self.devices[curdev].inputs, 3: self.devices[curdev].holdings}

        # read all register
        if register_to_read == 0:
            if function_code == 4:
                self.devices[curdev].inputs = self.devices[curdev].device.read_registers(
                    0,
                    len(self.devices[curdev].inputs),
                    functioncode=function_code)
            if function_code == 3:
                self.devices[curdev].holdings = self.devices[curdev].device.read_registers(
                    0,
                    len(self.devices[curdev].holdings),
                    functioncode=function_code)
        # read one register
        else:
            if register_to_read+1 > len(buff[function_code]): raise ValueError("Input register out of range  ")
            buff[function_code][register_to_read] = self.devices[0].device.read_registers(
                register_to_read,
                1,
                functioncode=function_code)[0]
        return True

    def __init__(self):
        self.consol = {"connect": self.connect, "read_input": self.read_register, "read_scope": self.read_scope}
        self.devices = []

    def create_server(self, port, speed, sid):
        """
        Creating Modbus serer and asking devise ID
        :param port: COM port name
        :param speed: COM port baud rate
        :param sid: Modbus slave address
        :return: True if device found
        """
        master = minimalmodbus.Instrument(port, sid)
        master.serial.baudrate = speed
        master.serial.bytesize = 8
        master.serial.parity = serial.PARITY_NONE
        master.serial.stopbits = 1
        master.serial.timeout = 0.025  # seconds
        master.debug = False
        try:
            req = master._perform_command(43, '\x0E\x01\x01\x00\x00')
        except minimalmodbus.NoResponseError:
            return False
        else:
            req = req[8:16] + req[32:40] + req[44:52]
            self.devices.append(self.Device(master))

            return True

    def connect(self, args):
        """
        Server.connect - searching devices

        :param args: connect [Port Name] [Port Speed] [Device address] [-a]
        :return: True/False
        """
        self.devices = []
        serials = serial.tools.list_ports.comports()
        ports = [el.device for el in serials]
        sids = range(1, 256)
        alloption = False
        try:
            sids = range(int(args[3]), int(args[3]) + 1)
        except (ValueError, IndexError):
            pass
        try:
            speeds = [int(args[2])]
        except (ValueError, IndexError):
            speeds = [9600, 38400, 115200, 230400, 480000]
        try:
            if args[1] in ports: ports = [args[1]]
        except IndexError:
            pass
        try:
            if args[4] == '-a': alloption = True
        except IndexError:
            pass

        for port in ports:
            if (alloption is False) & (len(self.devices) != 0): break
            try:
                for sid in sids:
                    if (alloption is False) & (len(self.devices) != 0): break
                    for speed in speeds:
                        if (alloption is False) & (len(self.devices) != 0): break
                        print("Searching", port, sid, speed)
                        self.create_server(port, speed, sid)
            except serial.serialutil.SerialException as e:
                print(e)
                raise self.ServerError(e.args)

        if len(self.devices) > 0:
            print("Found ", len(self.devices), " devices")
            return True
        raise self.ServerError(
            "Current ports: \n" + "\n".join(ports) + "\nDevice Not found"
        )

    def main(self, inpt):
        args = inpt.split()
        if args[0] in self.consol:
            return self.consol[args[0]](args)
        return None


if __name__ == '__main__':
    print("sdfd")