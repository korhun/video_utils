import os
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtWidgets import QFileDialog, QMainWindow

from video_sources.file_video_source import FileVideoSource
import pickle


class Player(QtCore.QThread):
    def __init__(self, image_view, video_time_slider):
        self.image_view = image_view
        self.video_time_slider = video_time_slider
        self.video_source = None
        self.reversed = False
        self.skip = -1
        self.goto_frame_index = -1
        QtCore.QThread.__init__(self)
        # self.video_time_slider.valueChanged.connect(self.sliderChanged)
        self.video_time_slider.sliderMoved.connect(self.sliderMoved)
        self.video_time_slider.sliderPressed.connect(self.sldDisconnect)
        self.video_time_slider.sliderReleased.connect(self.sldReconnect)
        self.timer_id = -1
        self._prev = 0
        self.slow_motion = False

    def sldDisconnect(self):
        # self.sender().valueChanged.disconnect()
        self.pause()

    def sldReconnect(self):
        # self.sender().valueChanged.connect(self.sliderChanged)
        # self.sender().valueChanged.emit(self.sender().value())
        self.pause()

    # def sliderChanged(self):
    #     # print(self.sender().objectName() + " : " + str(self.sender().value()))
    #     # if self.skip == -1:
    #     #     self.goto_frame_index = self.sender().value()
    #     pass

    def sliderMoved(self):
        if self.skip == -1 and self.goto_frame_index == -1:
            time_elapsed = time.time() - self._prev
            if time_elapsed > 0.2:
                self._prev = time.time()
                self.goto_frame_index = self.sender().value()

    def load_video(self, file_name):
        try:
            self.video_source = FileVideoSource(file_name)
            self.video_time_slider.setMaximum(self.video_source.frame_count)
            self.video_time_slider.setTickInterval(1)
            self.video_time_slider.setValue(self.video_source.get_current_frame_index())
            self.skip = 0
        except:
            self.skip = -1

    def play_next_frame(self, skip=1):
        self.pause()
        self.goto_frame_index = self.video_source.get_current_frame_index() + (5*skip if self.slow_motion else skip)

    def play_previous_frame(self, skip=1):
        self.pause()
        self.goto_frame_index = self.video_source.get_current_frame_index() - (5*(skip+1)+1 if self.slow_motion else skip+1)

    def play_left_fast(self, forced=False):
        if not forced and self.skip > 0 and self.reversed:
            self.skip = -1
        else:
            self.reversed = True
            self.skip = 5

    def play_left(self, forced=False):
        if not forced and self.skip == 0 and self.reversed:
            self.skip = -1
        else:
            self.reversed = True
            self.skip = 0

    def pause(self):
        self.skip = -1

    def toggle(self):
        if self.skip == -1:
            self.play_right(True)
        else:
            self.pause()

    def play_right(self, forced=False):
        if not forced and self.skip == 0 and not self.reversed:
            self.skip = -1
        else:
            self.reversed = False
            self.skip = 0

    def play_right_fast(self, forced=False):
        if not forced and self.skip > 0 and not self.reversed:
            self.skip = -1
        else:
            self.reversed = False
            self.skip = 5

    def run(self):
        prev = 0
        while True:
            try:
                if self.goto_frame_index >= 0:
                    ok, frame = self.video_source.goto(self.goto_frame_index)
                    if ok:
                        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
                        self.image_view.setPixmap(QtGui.QPixmap.fromImage(image))
                        self.video_time_slider.setValue(self.video_source.get_current_frame_index())
                    self.goto_frame_index = -1
                elif self.skip >= 0:
                    time_elapsed = time.time() - prev

                    # modifiers = QtWidgets.QApplication.keyboardModifiers()
                    # if modifiers == QtCore.Qt.ShiftModifier:  # shift pressed
                    if self.slow_motion:
                        time_elapsed *= 0.1

                    if time_elapsed > 1. / self.video_source.fps:
                        prev = time.time()
                        ok, frame = self.video_source.previous(self.skip) if self.reversed else self.video_source.next(self.skip)
                        if ok:
                            image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()

                            self.image_view.setPixmap(QtGui.QPixmap.fromImage(image))
                            # pixmap = QtGui.QPixmap.fromImage(image)
                            # pixmap = pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio)
                            # self.image_view.setPixmap(pixmap)

                            self.video_time_slider.setValue(self.video_source.get_current_frame_index())
            except:
                self.pause()


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(808, 637)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.pushButton_fast_left = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_fast_left.setObjectName("pushButton_fast_left")
        self.gridLayout.addWidget(self.pushButton_fast_left, 2, 1, 1, 1)

        self.pushButton_left = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_left.setObjectName("pushButton_left")
        self.gridLayout.addWidget(self.pushButton_left, 2, 2, 1, 1)

        self.pushButton_pause = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_pause.setObjectName("pushButton_pause")
        self.gridLayout.addWidget(self.pushButton_pause, 2, 3, 1, 1)

        self.pushButton_right = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_right.setObjectName("pushButton_right")
        self.gridLayout.addWidget(self.pushButton_right, 2, 4, 1, 1)

        self.pushButton_fast_right = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_fast_right.setObjectName("pushButton_fast_right")
        self.gridLayout.addWidget(self.pushButton_fast_right, 2, 5, 1, 1)

        self.video_time_slider = QtWidgets.QSlider(self.centralwidget)
        self.video_time_slider.setOrientation(QtCore.Qt.Horizontal)
        self.video_time_slider.setObjectName("video_time_slider")
        self.gridLayout.addWidget(self.video_time_slider, 1, 0, 1, 7)

        self.image_view = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_view.sizePolicy().hasHeightForWidth())
        self.image_view.setSizePolicy(sizePolicy)
        self.image_view.setAlignment(QtCore.Qt.AlignCenter)
        self.image_view.setObjectName("image_view")
        self.gridLayout.addWidget(self.image_view, 0, 0, 1, 7)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 808, 21))
        self.menubar.setObjectName("menubar")
        self.menuOpen = QtWidgets.QMenu(self.menubar)
        self.menuOpen.setObjectName("menuOpen")
        self.menuProcess = QtWidgets.QMenu(self.menubar)
        self.menuProcess.setObjectName("menuProcess")
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
        self.menuOpen.addAction(self.actionFile)
        self.menuOpen.addAction(self.actionURL)
        self.menuOpen.addAction(self.actionYouTube)
        self.menuOpen.addAction(self.actionCam)
        self.menuOpen.addSeparator()
        self.menuOpen.addAction(self.actionExit)
        self.menuProcess.addAction(self.actionOutput_Dir)
        self.menuProcess.addSeparator()
        self.menuProcess.addAction(self.actionSave_Current)
        self.menuProcess.addAction(self.actionSave_All_Frames)
        self.menubar.addAction(self.menuOpen.menuAction())
        self.menubar.addAction(self.menuProcess.menuAction())

        self.retranslateUi(MainWindow)
        self.initialize(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Video"))
        self.menuOpen.setTitle(_translate("MainWindow", "&Open"))
        self.menuProcess.setTitle(_translate("MainWindow", "&Save"))
        self.actionFile.setText(_translate("MainWindow", "&File"))
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

    def initialize(self, win):
        # baseDir = os.path.dirname(os.path.realpath(__file__))
        # imgDir = os.path.join(baseDir, "img")
        # win.setWindowIcon(QtGui.QIcon(os.path.join(imgDir, "video.png")))
        win.setWindowIcon(QtGui.QIcon("img/video.png"))

        btnSize = QtCore.QSize(45, 45)
        self.pushButton_fast_left.setFixedSize(btnSize)
        self.pushButton_left.setFixedSize(btnSize)
        self.pushButton_pause.setFixedSize(btnSize)
        self.pushButton_right.setFixedSize(btnSize)
        self.pushButton_fast_right.setFixedSize(btnSize)

        iconSize = QtCore.QSize(30, 30)
        self.pushButton_fast_left.setIconSize(iconSize)
        self.pushButton_left.setIconSize(iconSize)
        self.pushButton_pause.setIconSize(iconSize)
        self.pushButton_right.setIconSize(iconSize)
        self.pushButton_fast_right.setIconSize(iconSize)

        self.pushButton_fast_left.setIcon(QtGui.QIcon('img/fast_play_left.png'))
        self.pushButton_left.setIcon(QtGui.QIcon('img/play_left.png'))
        self.pushButton_pause.setIcon(QtGui.QIcon('img/pause.png'))
        self.pushButton_right.setIcon(QtGui.QIcon('img/play_right.png'))
        self.pushButton_fast_right.setIcon(QtGui.QIcon('img/fast_play_right.png'))

        self.pushButton_fast_left.setToolTip("<html><center>NUM 7</center><br>Press SHIFT for slow motion</html>")
        self.pushButton_left.setToolTip("<html><center>NUM 4</center><br>Press SHIFT for slow motion</html>")
        self.pushButton_pause.setToolTip("<html><center>NUM 5</center></html>")
        self.pushButton_right.setToolTip("<html><center>NUM 6</center><br>Press SHIFT for slow motion</html>")
        self.pushButton_fast_right.setToolTip("<html><center>NUM 9</center><br>Press SHIFT for slow motion</html>")

        self.pushButton_fast_left.clicked.connect(self.clicked_fast_left)
        self.pushButton_left.clicked.connect(self.clicked_left)
        self.pushButton_pause.clicked.connect(self.clicked_pause)
        self.pushButton_right.clicked.connect(self.clicked_right)
        self.pushButton_fast_right.clicked.connect(self.clicked_fast_right)

        self.actionFile.triggered.connect(self.clicked_file)

        self.player = Player(self.image_view, self.video_time_slider)
        self.player.start()
        try:
            with open(r"_last_video.pickle", "rb") as last_video:
                last_video_file_name = pickle.load(last_video)
                if os.path.isfile(last_video_file_name):
                    self.load_video(last_video_file_name)
        except:
            pass

    def key_pressed(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_7:
            self.player.play_left_fast(True)
        elif e.key() == Qt.Key_4:
            self.player.play_left(True)
        elif e.key() == Qt.Key_5:
            self.player.pause()
        elif e.key() == Qt.Key_8:
            self.player.pause()
        elif e.key() == Qt.Key_Enter:
            self.player.toggle()
        elif e.key() == Qt.Key_6:
            self.player.play_right(True)
        elif e.key() == Qt.Key_9:
            self.player.play_right_fast(True)
        elif e.key() == Qt.Key_Shift:
            self.player.slow_motion = True

        elif e.key() == Qt.Key_Left:
            self.player.play_previous_frame()
        elif e.key() == Qt.Key_Right:
            self.player.play_next_frame()
        elif e.key() == Qt.Key_Down:
            self.player.play_previous_frame(5)
        elif e.key() == Qt.Key_Up:
            self.player.play_next_frame(5)

        # else:
        #     print(e.key())

    def key_released(self, e):
        if e.key() == Qt.Key_Shift:
            self.player.slow_motion = False

        elif e.key() == Qt.Key_Space:
            self.player.toggle()

        elif e.key() == Qt.Key_Left:
            self.player.play_previous_frame()
        elif e.key() == Qt.Key_Right:
            self.player.play_next_frame()
        elif e.key() == Qt.Key_Down:
            self.player.play_previous_frame(5)
        elif e.key() == Qt.Key_Up:
            self.player.play_next_frame(5)


    def clicked_fast_left(self):
        self.player.play_left_fast()

    def clicked_left(self):
        self.player.play_left()

    def clicked_pause(self):
        self.player.pause()

    def clicked_right(self):
        self.player.play_right()

    def clicked_fast_right(self):
        self.player.play_right_fast()

    def clicked_file(self):
        file_names = self.select_file()
        if file_names and len(file_names) > 0:
            self.load_video(file_names[0])

    def select_file(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setWindowTitle('Open Video File')
        # dialog.setNameFilter('Video Fle (*.mov *.avi *.mp4)')
        # dialog.setFilter(QDir.Files)
        try:
            with open(r"_last_dir.pickle", "rb") as load_file:
                dialog.setDirectory(pickle.load(load_file))
        except:
            pass
        if dialog.exec_():
            dir_name = dialog.directory().dirName()
            with open(r"_last_dir.pickle", "wb") as save_file:
                pickle.dump(dir_name, save_file)
            return dialog.selectedFiles()

    def load_video(self, file_name):
        self.player.load_video(file_name)
        with open(r"_last_video.pickle", "wb") as save_file:
            pickle.dump(file_name, save_file)

    def play_right(self):
        self.player.play_right()


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = Ui_MainWindow()
#     ui.setupUi(MainWindow)
#     MainWindow.show()
#     sys.exit(app.exec_())

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)
        self.setupUi(self)

    def keyPressEvent(self, event):
        # if not event.isAutoRepeat():
        self.key_pressed(event)

    def keyReleaseEvent(self, event):
        self.key_released(event)

    # def setChildrenFocusPolicy(self, policy):
    #     def recursiveSetChildFocusPolicy(parentQWidget):
    #         for childQWidget in parentQWidget.findChildren(QtGui.QWidget):
    #             childQWidget.setFocusPolicy(policy)
    #             recursiveSetChildFocusPolicy(childQWidget)
    #
    #     recursiveSetChildFocusPolicy(self)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
