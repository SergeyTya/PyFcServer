import serial
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtWidgets import QApplication


class ProdSensEmu(QThread):

    def __init__(self, port_name, speed):
        QThread.__init__(self)
        try:
            self.port = None
            tmp = serial.Serial(port_name, speed)
            self.port = tmp
            self.dev_freq = 0
            self.sens_value = 0
            self.cerr = 0
            print("Production sens emulator started ")
            print("Port = ", port_name, " Speed=", speed)
        except serial.serialutil.SerialException as e:
            print(e)


    def run(self):
        if self.port is None: return
        if not self.port.is_open: return
        cnt = self.port.in_waiting
        if cnt > 3:
            print("PSE - get request: ")
            print(self.port.read_all())
            self.port.write(b'begin\n')
        else:
            self.cerr +=1
            if self.cerr > 50:
                self.cerr = 0
                print("PSE - connection timeout")

    def setFreq(self, freq):
        self.dev_freq = freq



if __name__ == '__main__':

    app = QApplication([])
    pse = ProdSensEmu("/dev/ttyUSB0", 38400)
    pse.start()

