import serial.tools.list_ports
import modbus_tk
import minimalmodbus

import modbus_tk.modbus_rtu as modbus_rtu
import modbus_tk.defines as cst


class Server:

    class ServerError(Exception):
        """ Common base class for all non-exit exceptions. """
        def __init__(self, *args, **kwargs):  # real signature unknown
            pass

        @staticmethod  # known case of __new__
        def __new__(*args, **kwargs):  # real signature unknown
            """ Create and return a new object.  See help(type) for accurate signature. """
            pass

    def about(self):
        print("Sever 2019")

    def reset(self):
        print("reset")
        return None

    def __init__(self):
        self.consol = {"connect": self.connect, "reset": self.reset}
        self.masters = []

    def create_server(self, port, speed, sid):
        """
        Creating Modbus serer and asking devise ID
        :param port: COM port name
        :param speed: COM port baud rate
        :param sid: Modbus slave address
        :return: True if devise found
        """
        master = minimalmodbus.Instrument(port, sid)
        master.serial.baudrate = speed
        master.serial.bytesize = 8
        master.serial.parity = serial.PARITY_NONE
        master.serial.stopbits = 1
        master.serial.timeout = 0.020  # seconds
        master.debug = False
        try:
            req = master._perform_command(43, '\x0E\x01\x01\x00\x00')
        except minimalmodbus.NoResponseError:
            return False
        else:
            req=req[8:16]+req[32:40]+req[44:52]
            self.masters.append([req, sid, speed, port])
            return True

    def connect(self, args):
        """
        Server.connect - searching devices

        :param args: connect [Port Name] [Port Speed] [Device address]
        :return: True/False
        """
        self.masters = []
        serials = serial.tools.list_ports.comports()
        ports = [el.device for el in serials]
        sids = range(1, 256)
        try: sids = range(int(args[3]), int(args[3])+1)
        except (ValueError, IndexError): None
        try: speeds = [int(args[2])]
        except (ValueError, IndexError): speeds = [9600, 38400, 115200, 230400, 480000]
        try:
            if args[1] in ports: ports = [args[1]]
        except IndexError: None

        for port in ports:
            try:
                for sid in sids:
                    for speed in speeds:
                        self.create_server(port, speed, sid)
            except serial.serialutil.SerialException as e:
                print(e)
                raise self.ServerError(e.args)

        if len(self.masters)>0:
            print("Found ", len(self.masters), " devises")
            print(self.masters)
            return True
        raise self.ServerError("Devices not found")

    def main(self, inpt):
        args = inpt.split()
        if args[0] in self.consol:
            self.consol[args[0]](args)


if __name__ == '__main__':
    srv = Server()
    #srv.main("connect /dev/ttyACM0 * *")

    srv.main("connect * * *")
