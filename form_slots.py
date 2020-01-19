'''
Created on 28 нояб. 2019 г.

@author: sergey
'''
import ctypes
import io
import math

import minimalmodbus
import serial
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QIntValidator, QCursor, QTextCursor, QDoubleValidator
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QComboBox, QLineEdit, QMenu, QHeaderView, QScrollBar, \
    QPushButton, QSizePolicy, QDialog, QInputDialog, QMainWindow
import json
import ProdSensEmu

# from qtconsole.qt import QtCore, QtGui
from PyQt5 import QtCore

from form_consetup import Ui_Dialog

"""
Пользовательские слоты для виджетов.
"""
# Импортируем класс интерфейса из созданного конвертером модуля
from form_ui import Ui_MainWindow as Ui_Form

import server as srv
import sys


# Создаём собственный класс, наследуясь от автоматически сгенерированного
class MainWindowSlots(Ui_Form):

    def __init__(self):
        self.send_total = 0
        self.send_err = 0
        self.cmd_list = []
        self.srv = srv.Server()
        self.ylwcells = []
        self.out_tmp = sys.stdout
        sys.stdout = io.StringIO("", newline=None)
        self.jsdtr = None
        self.loggers = [0] * 10
        self.jsstatus = []
        try:
            with open('status.json', 'r') as fh:  # открываем файл на чтение
                self.jsstatus = json.load(fh)  # загружаем из файла данные в словарь data
        except (
                json.decoder.JSONDecodeError,
                FileNotFoundError
        ) as e: print(e)

    def proc(self):
        # status bar
        tmpstbar = "нет устройства"
        if len(self.srv.devices) > 0:
            if len(self.srv.devices[0].inputs) > 2:
                tmpdvname = self.srv.devices[0].slave_name
                tmpstbar = self.srv.devices[0].device.serial.port + " " + str(self.srv.devices[0].device.serial.baudrate)+\
                           " Adr "+str(self.srv.devices[0].device.address) +" : " + tmpdvname +\
                           " : status "+ str(hex(self.srv.devices[0].inputs[2]))+\
                           " : tot=" + str(self.send_total)+ " err=" + str(self.send_err)
        self.statusbar.showMessage(tmpstbar)

        # First int
        if len(self.srv.devices) > 0: self.widget_init()

        # Holding table check
        self.check_holding_table()

        # input indicators refresh
        if len(self.srv.devices) > 0:
            self.cmd_list.append("read 0 * 4")
            if len(self.srv.devices[0].inputs) >= len(self.indicators):
                for i, el in enumerate(self.indicators):
                    tmp = ctypes.c_int16(self.srv.devices[0].inputs[i + 3])
                    inid_str =str(tmp.value / 10) + el.toolTip()
                    el.setText(inid_str)

        # Device status label
        if len(self.srv.devices) > 0:
            if len(self.srv.devices[0].inputs) > 2:
                str_status = str(hex(self.srv.devices[0].inputs[2]))
                try:
                    str_status2 = " " + self.jsstatus[0][str_status[2:3]][0]+" "+self.jsstatus[1][str_status[3:5]]
                    self.label_DevStatus.setStyleSheet(self.jsstatus[0][str_status[2:3]][1])
                except (
                        KeyError,
                        IndexError
                ):
                    str_status2 = str_status
                self.label_DevStatus.setText(str_status2)

        # prodsens emulator controls
        if len(self.srv.devices) > 0:
            if len(self.srv.devices[0].inputs) > 0:
                try:
                    tmp = float(self.lineEdit_EmuOut_gain.text())
                    self.pse.setOutpuGain(tmp)
                except ValueError: pass

                tmp_vl = ctypes.c_int16(self.srv.devices[0].inputs[3])
                self.pse.setFreqValue(math.fabs(tmp_vl.value/10))

                #self.lineEdit_EmuOut.setText(str(self.pse.pse_float_value).format("f%2"))
                #self.lineEdit_EmuOut.setText('{0: >#016.2f}'.format(self.pse.pse_float_value))

        if len(self.srv.devices) > 0:
            if len(self.srv.devices[0].inputs) > 0:
                for i in range(len(self.indicators)):
                    self.loggers[i].logValue(self.srv.devices[0].inputs[i+3])

        # stdout read to form consol
        tmp = sys.stdout.getvalue()
        if len(tmp) > 0:
            textCursor = self.plainTextEdit_consol.textCursor()
            textCursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor, 1)
            self.plainTextEdit_consol.setTextCursor(textCursor)
            self.plainTextEdit_consol.textCursor().insertText(tmp)
            self.plainTextEdit_consol.verticalScrollBar().setValue(
                self.plainTextEdit_consol.verticalScrollBar().maximum()
            )
            sys.stdout = io.StringIO("", newline=None)

    # production sensor
    def prodseninit(self):
        self.lineEdit_EmuOut_gain.setText("0.042")
        self.lineEdit_EmuPort.setText("COM6")
        self.lineEdit_EmuSpeed.setText("38400")

        def pse_con_lstn():
            try:
                spd = int(self.lineEdit_EmuSpeed.text())
            except ValueError:
                return
            self.timer3 = None
            self.pse = ProdSensEmu.ProdSensEmu(self.lineEdit_EmuPort.text(), spd)
            self.lineEdit_EmuOut.returnPressed.connect(lambda: self.pse.logger.show())


            if self.pse.port is None: return
            self.timer3 = QTimer()
            self.timer3.timeout.connect(lambda: self.pse.start())
            self.timer3.start(10)

        pse_con_lstn()
        self.pushButton_EmuPortOpen.clicked.connect(pse_con_lstn)

        # Определяем пользовательский слот
    def signal_search(self, Param = False):

        form = Ui_Dialog()
        self.win = QDialog()
        form.setupUi(self.win)

        def connect():
            self.send_total = 0
            self.send_err = 0
            self.tableWidget.setRowCount(0)
            if form.comboBox_portlist.currentIndex() == 0:
                port = "*"
            else:
                port = form.comboBox_portlist.currentText()
            speed = "*"
            try:
                int(form.comboBox_speedlist.currentText())
                speed = form.comboBox_speedlist.currentText()
            except ValueError: pass
            ID = "*"
            try:
                int(form.lineEdit_ID.text())
                ID = form.lineEdit_ID.text()
            except ValueError: pass
            cmd = "connect "+port+" "+speed+" "+ID
            self.cmd_list.append(cmd)
            self.cmd_list.append("read 0 * 3")
            self.cmd_list.append("read 0 * 4")
            self.win.close()
            return None

        serials = serial.tools.list_ports.comports()
        for el in serials: form.comboBox_portlist.addItem(el.device)
        form.pushButton_CN.clicked.connect(self.win.close)
        form.pushButton_OK.clicked.connect(connect)
        if Param: self.win.show()
        else: connect()

    def signal_slider_moved(self):
        if len(self.srv.devices) == 0: return
        value = int(self.horizontalSlider.value()*self.srv.devices[0].holdings[5]/self.horizontalSlider.maximum())
        self.tableWidget.cellWidget(3, 1).setText(str(value))
        self.marking_cell(3)
        req = "write 0 3 " + str(value)
        self.lineEdit_freqref.setText(str(value/10).replace(".", ","))
        self.cmd_list.append(req)
        pass

    def signal_slider_changed(self):
        if len(self.cmd_list) > 1: return
        if len(self.srv.devices) == 0: return
        value = int(self.horizontalSlider.value()*self.srv.devices[0].holdings[5]/self.horizontalSlider.maximum())
        req = "write 0 3 " + str(value)
        self.cmd_list.append(req)
        self.marking_cell(3)
        self.tableWidget.cellWidget(3, 1).setText(str(value))
        self.lineEdit_freqref.setText(str(value/10).replace(".", ","))

    def signal_lineedit_freref_pressed(self):
        if len(self.srv.devices) == 0: return
        try:
            tmp = self.lineEdit_freqref.text()
            if ',' in tmp:
                tmp = tmp.replace(',', '.')
               # self.lineEdit_freqref.setText(tmp)
            tmp = float(tmp)
        except ValueError as e:
            self.lineEdit_freqref.clear()
        else:
            if self.srv.devices[0].holdings[5] > 0:
                tmp = self.horizontalSlider.maximum() * 10 * tmp/self.srv.devices[0].holdings[5]
            else: tmp = 0
            self.horizontalSlider.setValue(tmp)
            self.signal_slider_moved()

    def signal_lineedit_freqref_changed(self):
        pass


    def check_holding_table(self):
        if (len(self.cmd_list) == 0) & (len(self.ylwcells) > 0):
            formatter = ""
            for i in range(self.tableWidget.rowCount()):
                tmp2 = int(self.tableWidget.cellWidget(i, 1).text())
                if tmp2 != self.srv.devices[0].holdings[i]:
                    formatter = "QLineEdit {background-color: Red; font: 14pt;}"
                    print("Warning: \n"
                          "Cell wrong value adr=", i, " cell=", tmp2, " dev=", self.srv.devices[0].holdings[i])
                    self.tableWidget.cellWidget(i, 1).setText(str(self.srv.devices[0].holdings[i]))
                else:
                    if i in self.ylwcells:
                        formatter = "QLineEdit {background-color: LightGreen; font: 14pt;}"
                    else:
                        formatter = "QLineEdit {background-color: White; font: 14pt;}"
                self.tableWidget.cellWidget(i, 1).setStyleSheet(formatter)
            self.ylwcells.clear()

    def marking_cell(self, row):
        ##
        # Marking holding table cells tobe checked
        # ##
        self.tableWidget.cellWidget(row, 1).setStyleSheet("QLineEdit {background-color: yellow; font: 14pt;}")
        self.ylwcells.append(row)

    # Table contmenu
    def signal_qtable_contmenu(self):
        if len(self.srv.devices) == 0: return
        menu = QMenu()
        act_load_from_dev = menu.addAction("Обновить в программе")
        act_load_from_dev.triggered.connect(self.action_loadformdev)
        act_load_to_dev = menu.addAction("Обновить на устройстве")

        def refratdev():
            for i in range(self.tableWidget.rowCount()-1):
                req = "write 0 " + str(i) + " " + self.tableWidget.cellWidget(i, 1).text()
                self.cmd_list.append(req)
                self.marking_cell(i)

        act_load_to_dev.triggered.connect(refratdev)
        act_save_to_dev = menu.addAction("Сохранить в память МПЧ")
        act_save_to_dev.triggered.connect(lambda: self.cmd_list.append("write 0 0 8"))
        # act_save_to_file = menu.addAction("Сохранить в файл")
        # act_load_from_flash = menu.addAction("Загрузить из памяти МПЧ")
        # act_load_from_default = menu.addAction("Сброс к заводским установкам")
        menu.exec(QCursor.pos())

    def action_loadformdev(self):
        # self.tableWidget.clear()
        # self.tableWidget.setRowCount(0)
        self.cmd_list.append("read 0 * 3")
        self.ylwcells.append(0)

    def widget_init(self):
        # combobox without scrolling
        class myComboBox(QComboBox):
            def wheelEvent(self, *args, **kwargs): pass

        # holding table refresh
        if self.tableWidget.rowCount() != len(self.srv.devices[0].holdings):
            # print device information
            print("holdings count=", len(self.srv.devices[0].holdings))
            print("inputs count=", len(self.srv.devices[0].inputs))
            # reading data from prm.json file
            with open('PRM.json', 'r', encoding='Windows-1251') as fh:  # открываем файл на чтение
                self.jsdtr = json.load(fh)  # загружаем из файла данные в словарь data
            # set table row value
            self.tableWidget.setRowCount(len(self.srv.devices[0].holdings))
            for x, el in enumerate(self.srv.devices[0].holdings):
                if x < len(self.jsdtr):
                    # writing parameter name from prm.json data to column 0, 2
                    item = QTableWidgetItem(self.jsdtr[x][0])
                    # disabling column 0 item changing
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.tableWidget.setItem(x, 0, item)
                    # additional combobox and button control at column 2 and 3
                    if len(self.jsdtr[x]) > 1:
                        tbtn = QPushButton()
                        tbtn.setMaximumSize(100, 75)
                        tbtn.setText("Задать")
                        self.tableWidget.setCellWidget(x, 3, tbtn)
                        #combox
                        cmb = myComboBox()
                        self.tableWidget.setCellWidget(x, 2, cmb)
                        for item in self.jsdtr[x][1]:
                            # adding item at combobox
                            self.tableWidget.cellWidget(x, 2).addItem(item[0])
                            # Switch combobox to current value
                            if self.srv.devices[0].holdings[x] < self.tableWidget.cellWidget(x, 2).count():
                                self.tableWidget.cellWidget(x, 2).setCurrentIndex(self.srv.devices[0].holdings[x])
                            else:
                                self.tableWidget.cellWidget(x, 2).setCurrentIndex(-1)

                            # Combobox index changing event
                            def signal_btnpressed():
                                try:
                                    # combobox current index
                                    tmp = self.tableWidget.cellWidget(self.tableWidget.currentRow(), 2).currentIndex()
                                    if tmp == -1: return
                                    # holding cell value
                                    tmp2 = int(self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).text())
                                    if tmp != tmp2:
                                        # marking cell
                                        self.marking_cell(self.tableWidget.currentRow())
                                        # request for server to write value
                                        if len(self.jsdtr[self.tableWidget.currentRow()]) > 1:
                                            if len(self.jsdtr[self.tableWidget.currentRow()][1][tmp]) == 2:
                                                # get cell value from json structure
                                                tmp = self.jsdtr[self.tableWidget.currentRow()][1][tmp][1]
                                        req = "write 0 " + str(self.tableWidget.currentRow()) + " " + str(tmp)
                                        self.cmd_list.append(req)
                                        # cell value changing
                                        self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).setText(str(tmp))
                                except AttributeError:
                                    pass

                            # connecting event to combobox
                            # self.tableWidget.cellWidget(x, 2).currentIndexChanged.connect(item_indCng)
                            # connecting event to button
                            self.tableWidget.cellWidget(x, 3).clicked.connect(signal_btnpressed)
                            tcmbx = QComboBox()
                            tcmbx.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding, )
                            self.tableWidget.cellWidget(x, 3).setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
                    # if no additional combobox
                    else:
                        # disabling cell changing at column 2
                        item = QTableWidgetItem("")
                        item.setFlags(QtCore.Qt.ItemIsEnabled)
                        self.tableWidget.setItem(x, 2, item)
                # if no data at prm.json
                else:
                    # disabling cell changing at column 0,2
                    item = QTableWidgetItem("")
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    # self.tableWidget.setItem(x, 2, item)
                    self.tableWidget.setItem(x, 0, item)
                # Set cell value at column 1
                item = QLineEdit(str(self.srv.devices[0].holdings[x]))
                item.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
                item.setMaxLength(6)
                item.setMaximumSize(100, 100)
                # Only int numbers
                item.setValidator(QIntValidator(-65536, 65536))

                # Cell value changing event
                def signal_cellpressed():
                    try:
                        # cell current value
                        tmp = int(self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).text())
                        # check for combobox item count
                        if tmp > self.tableWidget.cellWidget(self.tableWidget.currentRow(), 2).count(): tmp = -1
                        # changing combobox index
                        self.tableWidget.cellWidget(self.tableWidget.currentRow(), 2).setCurrentIndex(tmp)
                    except (ValueError, AttributeError) as e:
                        print(e)
                    # marking cell
                    self.marking_cell(self.tableWidget.currentRow())
                    # request for holding register changing
                    req = "write 0 " + str(self.tableWidget.currentRow()) + " " + \
                          self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).text()
                    self.cmd_list.append(req)

                def signal_cellchanged():
                    try:
                        self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).setStyleSheet(
                            "QLineEdit {background-color: Pink; font: 14pt;}"
                        )
                    except AttributeError:
                        pass

                # connecting event to QLineEdit
                item.returnPressed.connect(signal_cellpressed)
                item.textChanged.connect(signal_cellchanged)
                self.tableWidget.setCellWidget(x, 1, item)
            # self.tableWidget.setColumnWidth(1,50)
            self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
