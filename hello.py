"""
Основной скрипт программы.
Запускает конфигуратор окна, подключает слоты и отображает окно.
"""
# Импортируем системый модуль для корректного закрытия программы
import io
# Импортируем минимальный набор виджетов
import minimalmodbus
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QAbstractSlider
# Импортируем созданный нами класс со слотами
#from qtpy import QtCore
from PyQt5.uic.properties import QtWidgets

from form_slots import MainWindowSlots
from PyQt5.QtCore import QTimer, QObject, QThread, pyqtSlot, QEventLoop
from PyQt5 import QtCore, Qt
import server as srv
import sys



# Создаём ещё один класс, наследуясь от класса со слотами
class MainWindow(MainWindowSlots):
    # При инициализации класса нам необходимо выпонить некоторые операции
    def __init__(self, form):
        super().__init__()
        # Сконфигурировать интерфейс методом из базового класса Ui_Form
        self.setupUi(form)
        # Подключить созданные нами слоты к виджетам
        self.connect_slots()
        self.prodseninit()
        self.indicators = [
            self.lineEdit_freq,
            self.lineEdit_vout, self.lineEdit_vbus,
            self.lineEdit_vgrd, self.lineEdit_curr,
            self.lineEdit_tfrc, self.lineEdit_pmtr,
            self.lineEdit_tmtr
        ]

    # Подключаем слоты к виджетам
    def connect_slots(self):

        self.pushButton_Scan.clicked.connect(self.btn_connect_push)
        # setup table ContextMenu
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.slot_qtable_contmenu)
        self.horizontalSlider.sliderReleased.connect(self.slot_slider_moved)
        self.pushButton_Start.clicked.connect(lambda: self.cmd_list.append("write 0 0 1"))
        self.pushButton_Stop.clicked.connect(lambda: self.cmd_list.append("write 0 0 2"))
        self.pushButton_Reset.clicked.connect(lambda: self.cmd_list.append("write 0 0 4"))
        #self.pushButton_Revers.clicked.connect(lambda: self.cmd_list.append("write 0 4 4"))
        return None

if __name__ == '__main__':
    # Создаём экземпляр приложения
    app = QApplication(sys.argv)
    # Создаём базовое окно, в котором будет отображаться наш UI
    window = QWidget()
    # Создаём экземпляр нашего UI
    server = srv.Server()
    ui = MainWindow(window)
    ui.srv = server
    # поток
    timer = QTimer()
    timer.timeout.connect(ui.proc)
    timer.start(100)

    # thread in timer to process serial communication
    class ServerProcTread(QThread):

        def __init__(self, cmd_list, srv, *args, **kwargs, ):
            QThread.__init__(self, *args, **kwargs)
            self.cmd_list = cmd_list
            self.srv = srv

        def run(self):
            try:
                #while len(self.cmd_list) != 0: self.srv.main(inpt=self.cmd_list.pop(0))
                while len(self.cmd_list) != 0: self.srv.main(inpt=self.cmd_list.pop(0))
            except (
                ValueError,
                serial.serialutil.SerialException,
                server.ServerError,
                minimalmodbus.NoResponseError,
                minimalmodbus.InvalidResponseError
            ) as e:
                print(e)

    th = ServerProcTread(ui.cmd_list, server)
    timer2 = QTimer()
    timer2.timeout.connect(lambda: th.start())
    timer2.start(50)

    # Отображаем окно
    window.show()
    # Обрабатываем нажатие на кнопку окна "Закрыть"
    sys.exit(app.exec_())
