# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form_consetup.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(220, 250)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(200, 250))
        Dialog.setMaximumSize(QtCore.QSize(240, 280))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.comboBox_portlist = QtWidgets.QComboBox(Dialog)
        self.comboBox_portlist.setObjectName("comboBox_portlist")
        self.comboBox_portlist.addItem("")
        self.verticalLayout.addWidget(self.comboBox_portlist)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.comboBox_speedlist = QtWidgets.QComboBox(Dialog)
        self.comboBox_speedlist.setObjectName("comboBox_speedlist")
        self.comboBox_speedlist.addItem("")
        self.comboBox_speedlist.addItem("")
        self.comboBox_speedlist.addItem("")
        self.comboBox_speedlist.addItem("")
        self.comboBox_speedlist.addItem("")
        self.verticalLayout.addWidget(self.comboBox_speedlist)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setMinimumSize(QtCore.QSize(0, 0))
        self.label_3.setMaximumSize(QtCore.QSize(200, 250))
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.lineEdit_ID = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_ID.setObjectName("lineEdit_ID")
        self.verticalLayout.addWidget(self.lineEdit_ID)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setText("")
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_OK = QtWidgets.QPushButton(Dialog)
        self.pushButton_OK.setObjectName("pushButton_OK")
        self.horizontalLayout.addWidget(self.pushButton_OK)
        self.pushButton_CN = QtWidgets.QPushButton(Dialog)
        self.pushButton_CN.setObjectName("pushButton_CN")
        self.horizontalLayout.addWidget(self.pushButton_CN)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Настройки порта"))
        self.label.setText(_translate("Dialog", "Порт"))
        self.comboBox_portlist.setItemText(0, _translate("Dialog", "поиск"))
        self.label_2.setText(_translate("Dialog", "Скорость"))
        self.comboBox_speedlist.setItemText(0, _translate("Dialog", "поиск"))
        self.comboBox_speedlist.setItemText(1, _translate("Dialog", "9600"))
        self.comboBox_speedlist.setItemText(2, _translate("Dialog", "38400"))
        self.comboBox_speedlist.setItemText(3, _translate("Dialog", "115200"))
        self.comboBox_speedlist.setItemText(4, _translate("Dialog", "230400"))
        self.label_3.setText(_translate("Dialog", "Адрес"))
        self.pushButton_OK.setText(_translate("Dialog", "Ok"))
        self.pushButton_CN.setText(_translate("Dialog", "Отмена"))
