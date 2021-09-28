# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'video_player.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1270, 998)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.video_time_slider = QtWidgets.QSlider(self.centralwidget)
        self.video_time_slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.video_time_slider.setOrientation(QtCore.Qt.Horizontal)
        self.video_time_slider.setObjectName("video_time_slider")
        self.gridLayout.addWidget(self.video_time_slider, 1, 0, 1, 6)
        self.image_view = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_view.sizePolicy().hasHeightForWidth())
        self.image_view.setSizePolicy(sizePolicy)
        self.image_view.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.image_view.setStyleSheet("background-color: rgb(47, 47, 47);")
        self.image_view.setText("")
        self.image_view.setAlignment(QtCore.Qt.AlignCenter)
        self.image_view.setObjectName("image_view")
        self.gridLayout.addWidget(self.image_view, 0, 0, 1, 6)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_output_dir = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_output_dir.setMinimumSize(QtCore.QSize(66, 66))
        self.pushButton_output_dir.setMaximumSize(QtCore.QSize(66, 66))
        self.pushButton_output_dir.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_output_dir.setText("")
        self.pushButton_output_dir.setIconSize(QtCore.QSize(50, 50))
        self.pushButton_output_dir.setObjectName("pushButton_output_dir")
        self.gridLayout_2.addWidget(self.pushButton_output_dir, 0, 5, 1, 1)
        self.pushButton_save = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_save.setMinimumSize(QtCore.QSize(66, 66))
        self.pushButton_save.setMaximumSize(QtCore.QSize(66, 66))
        self.pushButton_save.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_save.setText("")
        self.pushButton_save.setIconSize(QtCore.QSize(50, 50))
        self.pushButton_save.setFlat(False)
        self.pushButton_save.setObjectName("pushButton_save")
        self.gridLayout_2.addWidget(self.pushButton_save, 0, 6, 1, 1)
        self.video_time_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Cascadia Code")
        font.setPointSize(16)
        self.video_time_label.setFont(font)
        self.video_time_label.setObjectName("video_time_label")
        self.gridLayout_2.addWidget(self.video_time_label, 0, 4, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 2, 4, 1, 2)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setMinimumSize(QtCore.QSize(0, 55))
        self.line.setMaximumSize(QtCore.QSize(16777215, 55))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 3, 1, 1)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setSpacing(6)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setMinimumSize(QtCore.QSize(100, 0))
        self.widget.setObjectName("widget")
        self.gridLayout_5.addWidget(self.widget, 0, 1, 1, 1)
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setMinimumSize(QtCore.QSize(100, 0))
        self.widget_2.setObjectName("widget_2")
        self.gridLayout_5.addWidget(self.widget_2, 0, 7, 1, 1)
        self.pushButton_fast_right = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_fast_right.setMinimumSize(QtCore.QSize(45, 45))
        self.pushButton_fast_right.setMaximumSize(QtCore.QSize(45, 45))
        self.pushButton_fast_right.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_fast_right.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton_fast_right.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/img/fast_play_right.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.pushButton_fast_right.setIcon(icon)
        self.pushButton_fast_right.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_fast_right.setFlat(False)
        self.pushButton_fast_right.setObjectName("pushButton_fast_right")
        self.gridLayout_5.addWidget(self.pushButton_fast_right, 0, 6, 1, 1)
        self.video_speed_slider = QtWidgets.QSlider(self.centralwidget)
        self.video_speed_slider.setMinimumSize(QtCore.QSize(0, 0))
        self.video_speed_slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.video_speed_slider.setOrientation(QtCore.Qt.Horizontal)
        self.video_speed_slider.setObjectName("video_speed_slider")
        self.gridLayout_5.addWidget(self.video_speed_slider, 1, 1, 1, 7)
        self.pushButton_fast_left = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_fast_left.setMinimumSize(QtCore.QSize(45, 45))
        self.pushButton_fast_left.setMaximumSize(QtCore.QSize(45, 45))
        self.pushButton_fast_left.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_fast_left.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/img/fast_play_left.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.pushButton_fast_left.setIcon(icon1)
        self.pushButton_fast_left.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_fast_left.setFlat(False)
        self.pushButton_fast_left.setObjectName("pushButton_fast_left")
        self.gridLayout_5.addWidget(self.pushButton_fast_left, 0, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem, 0, 8, 1, 1)
        self.pushButton_pause = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_pause.setMinimumSize(QtCore.QSize(45, 45))
        self.pushButton_pause.setMaximumSize(QtCore.QSize(45, 45))
        self.pushButton_pause.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_pause.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/img/pause.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.pushButton_pause.setIcon(icon2)
        self.pushButton_pause.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_pause.setDefault(False)
        self.pushButton_pause.setFlat(False)
        self.pushButton_pause.setObjectName("pushButton_pause")
        self.gridLayout_5.addWidget(self.pushButton_pause, 0, 4, 1, 1)
        self.pushButton_left = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_left.setMinimumSize(QtCore.QSize(45, 45))
        self.pushButton_left.setMaximumSize(QtCore.QSize(45, 45))
        self.pushButton_left.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_left.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/img/play_left.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.pushButton_left.setIcon(icon3)
        self.pushButton_left.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_left.setFlat(False)
        self.pushButton_left.setObjectName("pushButton_left")
        self.gridLayout_5.addWidget(self.pushButton_left, 0, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem1, 0, 0, 1, 1)
        self.pushButton_right = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_right.setMinimumSize(QtCore.QSize(45, 45))
        self.pushButton_right.setMaximumSize(QtCore.QSize(45, 45))
        self.pushButton_right.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_right.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/img/play_right.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.pushButton_right.setIcon(icon4)
        self.pushButton_right.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_right.setFlat(False)
        self.pushButton_right.setObjectName("pushButton_right")
        self.gridLayout_5.addWidget(self.pushButton_right, 0, 5, 1, 1)
        self.speed_spin_box = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.speed_spin_box.setMaximumSize(QtCore.QSize(100, 999))
        font = QtGui.QFont()
        font.setFamily("Cascadia Code")
        font.setPointSize(10)
        self.speed_spin_box.setFont(font)
        self.speed_spin_box.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.speed_spin_box.setAlignment(QtCore.Qt.AlignCenter)
        self.speed_spin_box.setMinimum(-999.0)
        self.speed_spin_box.setMaximum(999.0)
        self.speed_spin_box.setSingleStep(0.25)
        self.speed_spin_box.setObjectName("speed_spin_box")
        self.gridLayout_5.addWidget(self.speed_spin_box, 1, 8, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_5, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1270, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuProcess = QtWidgets.QMenu(self.menubar)
        self.menuProcess.setObjectName("menuProcess")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionFile = QtWidgets.QAction(MainWindow)
        self.actionFile.setObjectName("actionFile")
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
        self.actionControls = QtWidgets.QAction(MainWindow)
        self.actionControls.setObjectName("actionControls")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuFile.addAction(self.actionFile)
        self.menuFile.addAction(self.actionURL)
        self.menuFile.addAction(self.actionYouTube)
        self.menuFile.addAction(self.actionCam)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuProcess.addAction(self.actionOutput_Dir)
        self.menuProcess.addSeparator()
        self.menuProcess.addAction(self.actionSave_Current)
        self.menuProcess.addAction(self.actionSave_All_Frames)
        self.menuHelp.addAction(self.actionControls)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuProcess.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Orientis"))
        self.pushButton_output_dir.setToolTip(_translate("MainWindow", "Output Dir (Ctrl+D)"))
        self.pushButton_output_dir.setShortcut(_translate("MainWindow", "Ctrl+D"))
        self.pushButton_save.setToolTip(_translate("MainWindow", "Save Current Image (Ctrl+S)"))
        self.pushButton_save.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.video_time_label.setText(_translate("MainWindow", "0:00 / 0:00"))
        self.pushButton_fast_right.setToolTip(_translate("MainWindow", "NUM 9"))
        self.pushButton_fast_left.setToolTip(_translate("MainWindow", "NUM 7"))
        self.pushButton_pause.setToolTip(_translate("MainWindow", "NUM 5"))
        self.pushButton_left.setToolTip(_translate("MainWindow", "NUM 4"))
        self.pushButton_right.setToolTip(_translate("MainWindow", "NUM 6"))
        self.menuFile.setTitle(_translate("MainWindow", "&Open"))
        self.menuProcess.setTitle(_translate("MainWindow", "&Save"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionFile.setText(_translate("MainWindow", "&File"))
        self.actionFile.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionURL.setText(_translate("MainWindow", "&Url"))
        self.actionYouTube.setText(_translate("MainWindow", "&YouTube"))
        self.actionCam.setText(_translate("MainWindow", "&Cam"))
        self.actionOutput_Dir.setText(_translate("MainWindow", "Output Dir"))
        self.actionOutput_Dir.setShortcut(_translate("MainWindow", "Ctrl+D"))
        self.actionSave_Current.setText(_translate("MainWindow", "Save Current Image"))
        self.actionSave_Current.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_All_Frames.setText(_translate("MainWindow", "Save All Frames"))
        self.actionSave_All_Frames.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionExit.setText(_translate("MainWindow", "&Exit"))
        self.actionExit.setIconText(_translate("MainWindow", "Exit"))
        self.actionExit.setShortcut(_translate("MainWindow", "Ctrl+F4"))
        self.actionControls.setText(_translate("MainWindow", "Controls"))
        self.actionAbout.setText(_translate("MainWindow", "About"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
