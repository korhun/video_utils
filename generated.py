# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'video.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(808, 637)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 2, 2, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 2, 4, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 1, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout.addWidget(self.pushButton_5, 2, 5, 1, 1)
        self.horizontalSlider_2 = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.gridLayout.addWidget(self.horizontalSlider_2, 1, 0, 1, 7)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setMaximumSize(QtCore.QSize(30, 16777215))
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 2, 3, 1, 1)
        self.imageLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageLabel.sizePolicy().hasHeightForWidth())
        self.imageLabel.setSizePolicy(sizePolicy)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLabel.setObjectName("imageLabel")
        self.gridLayout.addWidget(self.imageLabel, 0, 0, 1, 7)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 808, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuProcess = QtWidgets.QMenu(self.menubar)
        self.menuProcess.setObjectName("menuProcess")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionURL = QtWidgets.QAction(MainWindow)
        self.actionURL.setObjectName("actionURL")
        self.actionYouTube = QtWidgets.QAction(MainWindow)
        self.actionYouTube.setObjectName("actionYouTube")
        self.actionCam = QtWidgets.QAction(MainWindow)
        self.actionCam.setObjectName("actionCam")
        self.actionOutput_Dir = QtWidgets.QAction(MainWindow)
        self.actionOutput_Dir.setObjectName("actionOutput_Dir")
        self.actionSave_Current = QtWidgets.QAction(MainWindow)
        self.actionSave_Current.setObjectName("actionSave_Current")
        self.actionSave_All_Frames = QtWidgets.QAction(MainWindow)
        self.actionSave_All_Frames.setObjectName("actionSave_All_Frames")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionURL)
        self.menuFile.addAction(self.actionYouTube)
        self.menuFile.addAction(self.actionCam)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuProcess.addAction(self.actionOutput_Dir)
        self.menuProcess.addSeparator()
        self.menuProcess.addAction(self.actionSave_Current)
        self.menuProcess.addAction(self.actionSave_All_Frames)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuProcess.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Video"))
        self.pushButton_2.setText(_translate("MainWindow", "PushButton"))
        self.pushButton_4.setText(_translate("MainWindow", "PushButton"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.pushButton_5.setText(_translate("MainWindow", "PushButton"))
        self.pushButton_3.setText(_translate("MainWindow", "PushButton"))
        self.imageLabel.setText(_translate("MainWindow", "Video"))
        self.menuFile.setTitle(_translate("MainWindow", "&Open"))
        self.menuProcess.setTitle(_translate("MainWindow", "&Save"))
        self.actionOpen.setText(_translate("MainWindow", "&File"))
        self.actionURL.setText(_translate("MainWindow", "&Url"))
        self.actionYouTube.setText(_translate("MainWindow", "&YouTube"))
        self.actionCam.setText(_translate("MainWindow", "&Cam"))
        self.actionOutput_Dir.setText(_translate("MainWindow", "Output Dir"))
        self.actionOutput_Dir.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave_Current.setText(_translate("MainWindow", "Save Current Image"))
        self.actionSave_Current.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_All_Frames.setText(_translate("MainWindow", "Save All Frames"))
        self.actionSave_All_Frames.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionExit.setText(_translate("MainWindow", "&Exit"))
        self.actionExit.setIconText(_translate("MainWindow", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())