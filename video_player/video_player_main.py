import os
import sys

import cv2
import qdarkstyle
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSettings, QSize, QPoint, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QPushButton


if __name__ == '__main__':
    from player import Player
    from utils import file_helper
    from video_player import Ui_MainWindow
    from dialogs.download_video_dialog import show_download_video_dialog
else:
    from .player import Player
    from .utils import file_helper
    from .video_player import Ui_MainWindow
    from .dialogs.download_video_dialog import show_download_video_dialog


class VideoPlayerMainWindow(QMainWindow, Ui_MainWindow):
    resized = QtCore.pyqtSignal()

    def resizeEvent(self, event):
        self.resized.emit()
        super(QMainWindow, self).resizeEvent(event)
        # QMainWindow.resizeEvent(self, event)
        # self.check_saved_frames()

    # def on_window_resized(self):
    #     pass

    def __init__(self, parent_app, parent_window=None, default_font=None):
        self.parent_app = parent_app
        self.parent_window = parent_window
        self.default_font = default_font
        self.freeze_display_once = False
        self.out_prefix = ""
        self.saved_frames = []
        self.btns = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        translator = QtCore.QTranslator()
        qm_file = file_helper.path_join(current_dir, 'video_player-tr.qm')
        translator.load(qm_file)
        parent_app.installTranslator(translator)

        super().__init__(parent=parent_window)
        # self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setupUi(self)

        # self.resized.connect(self.on_window_resized)

        self.pushButton_fast_left.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/fast_play_left.png')))
        self.pushButton_left.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/play_left.png')))
        self.pushButton_pause.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/pause.png')))
        self.pushButton_right.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/play_right.png')))
        self.pushButton_fast_right.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/fast_play_right.png')))
        self.pushButton_save.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/snapshot.png')))
        self.pushButton_save_and_edit.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/editing.png')))
        self.pushButton_output_dir.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/folder.png')))

        self.setWindowIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/icon.ico')))

        self.pushButton_fast_left.clicked.connect(self.clicked_fast_left)
        self.pushButton_left.clicked.connect(self.clicked_left)
        self.pushButton_pause.clicked.connect(self.clicked_pause)
        self.pushButton_right.clicked.connect(self.clicked_right)
        self.pushButton_fast_right.clicked.connect(self.clicked_fast_right)

        self.actionFile.triggered.connect(self.clicked_file)
        self.actionOutput_Dir.triggered.connect(self.clicked_output_dir)
        self.pushButton_output_dir.clicked.connect(self.clicked_output_dir)

        self.actionYouTube.triggered.connect(self.clicked_youtube)

        self.actionSave_Current.setShortcut('Ctrl+S')

        self.actionSave_Current.triggered.connect(self.save_current_frame)
        self.pushButton_save.clicked.connect(lambda: self.save_current_frame(False))
        self.pushButton_save_and_edit.clicked.connect(lambda: self.save_current_frame(True))

        self.actionExit.triggered.connect(self.close_me)

        # self.image_view.setScaledContents(True)
        self.image_view.mousePressEvent = self.on_image_view_mouse_pressed
        self.image_view.setMinimumSize(1, 1)

        self.centralwidget.mousePressEvent = self.on_mouse_pressed

        self.title = self.windowTitle()

        self.player = Player(self, self.video_time_slider, self.speed_dial, self.speed_spin_box)
        self.player.list_of_dict_signals.connect(self._load_frame)
        self.player.video_start_signal.connect(self.on_video_start)
        self.player.video_end_signal.connect(self.on_video_end)
        self.player.start()

        self.disabled_play_button_exists = True
        self.on_video_start()
        self.just_loaded = 0

        self.settings = QSettings('Orientis', 'video_player')

        self.output_dir = None
        self.set_output_dir(self.settings.value("output_dir", ""))

        last_video = self.settings.value("last_video", "")
        if os.path.isfile(last_video):
            self.load_video(last_video, change_size=False)

        self.settings.setFallbacksEnabled(False)  # File only, not registry
        self.resize(self.settings.value("size", QSize(800, 800)))
        self.move(self.settings.value("pos", QPoint(200, 200)))

        if self.parent_window is None:
            self.pushButton_save_and_edit.setVisible(False)
            self.setStyleSheet(qdarkstyle.load_stylesheet(palette=qdarkstyle.DarkPalette))
            # self.setStyleSheet(qdarkstyle.load_stylesheet(palette=qdarkstyle.LightPalette))

        self.video_time_slider.setStyleSheet("""
                .QSlider {
                    background: #00000000;
                    border: 0px solid #ff0000;
                }
            """)
        # self.video_time_slider.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.video_time_slider.setMouseTracking(True)
        self.video_time_slider.installEventFilter(self)
        self.installEventFilter(self)

        if default_font is not None:
            self.setFont(default_font)
            self.menubar.setFont(default_font)
            self.menuFile.setFont(default_font)
            self.menuHelp.setFont(default_font)
            self.menuProcess.setFont(default_font)

    def eventFilter(self, obj, e):
        def pixelPosToRangeValue(ctrl, pos):
            # ref: https://stackoverflow.com/a/52690011/1266873
            opt = QtWidgets.QStyleOptionSlider()
            ctrl.initStyleOption(opt)
            gr = ctrl.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderGroove, self)
            sr = ctrl.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderHandle, self)

            if ctrl.orientation() == Qt.Horizontal:
                sliderLength = sr.width()
                sliderMin = gr.x()
                sliderMax = gr.right() - sliderLength + 1
            else:
                sliderLength = sr.height()
                sliderMin = gr.y()
                sliderMax = gr.bottom() - sliderLength + 1;
            pr = pos - sr.center() + sr.topLeft()
            p = pr.x() if ctrl.orientation() == Qt.Horizontal else pr.y()
            return QtWidgets.QStyle.sliderValueFromPosition(ctrl.minimum(), ctrl.maximum(), p - sliderMin,
                                                            sliderMax - sliderMin, opt.upsideDown)

        e_type = e.type()
        update_required = False
        if obj == self.video_time_slider:
            if e_type == QEvent.MouseButtonRelease:
                val = pixelPosToRangeValue(self.video_time_slider, e.pos())
                self.video_time_slider.setValue(val)
            if e_type == QEvent.Move:
                update_required = True
        if e_type == QEvent.Resize:
            update_required = True
        if update_required:
            self.update_saved_frame_locations()
        return super().eventFilter(obj, e)

    def update_saved_frame_locations(self):
        w = self.video_time_slider.width()
        frame_count = self.player.get_frame_count()
        y = self.video_time_slider.y() + self.menubar.height() + 15
        x0 = self.video_time_slider.x() + 2
        w1 = w - 4
        x0mult = (w1 - x0) / w1
        i = 0
        for index in self.saved_frames:
            if self.btns is not None and len(self.btns) > i:
                btn = self.btns[i]
                x = index * w / frame_count
                x = int(x0 + x * x0mult)
                btn.move(x, y)
                btn.show()
                i += 1

    def check_saved_frames(self):
        if self.btns and len(self.btns) > 0:
            for btn in self.btns:
                btn.deleteLater()
        try:
            self.btns = []
            self.saved_frames = []
            frame_count = self.player.get_frame_count()
            if frame_count > 0 and self.output_dir is not None and os.path.isdir(self.output_dir) and self.out_prefix is not None and len(self.out_prefix) > 0:
                for fn in file_helper.enumerate_files(self.output_dir, False, "{}*.png".format(self.out_prefix)):
                    try:
                        _, name, _ = file_helper.get_file_name_extension(fn)
                        name = name.replace(self.out_prefix, "")
                        frame_index = int(name)
                        self.saved_frames.append(frame_index)

                        btn = QPushButton(self)
                        btn.setFixedSize(QSize(8, 10))
                        btn.setStyleSheet("background-color: #80808040; border:0px solid #ff0000;")
                        btn.setCursor(QCursor(Qt.PointingHandCursor))

                        btn.clicked.connect(lambda state, index=frame_index: self.player.goto_frame(index))
                        self.btns.append(btn)
                    except:
                        pass
                self.saved_frames.sort()
        finally:
            self.update_saved_frame_locations()
            self.video_time_slider.repaint()

    def on_mouse_pressed(self, event):
        self.update_saved_frame_locations()
        focused_widget = self.focusWidget()
        if focused_widget is not None:
            focused_widget.clearFocus()

    def closeEvent(self, e):
        self.player.running = False
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())

    def close_me(self):
        self.closeEvent(None)
        self.close()

    def is_closed(self):
        return not self.player.running

    # def on_comboBox_speed_changed(self, text):
    #     if text == "Normal":
    #         self.player.set_speed(1)
    #     else:
    #         self.player.set_speed(float(text))

    def on_image_view_mouse_pressed(self, _):
        self.player.toggle()

    # region key press
    def keyPressEvent(self, event):
        # if not event.isAutoRepeat():
        self.key_pressed(event)

    def keyReleaseEvent(self, event):
        self.key_released(event)

    def key_pressed(self, e):
        if e.key() == Qt.Key_Escape:
            self.speed_dial.setFocus()
        elif e.key() == Qt.Key_7:
            self.player.play_left_fast(True)
        elif e.key() == Qt.Key_4:
            self.player.play_left(True)
        elif e.key() == Qt.Key_5:
            self.player.pause()
        elif e.key() == Qt.Key_8:
            self.player.pause()

        elif e.key() == Qt.Key_Space:
            self.player.toggle()

        elif e.key() == Qt.Key_6:
            self.player.play_right(True)
        elif e.key() == Qt.Key_9:
            self.player.play_right_fast(True)
        elif e.key() == Qt.Key_Shift:
            self.player.shift_pressed = True

        elif e.key() == Qt.Key_Left:
            self.player.play_previous_frame()
        elif e.key() == Qt.Key_Right:
            self.player.play_next_frame()
        elif e.key() == Qt.Key_Down:
            self.player.play_previous_frame(5)
        elif e.key() == Qt.Key_Up:
            self.player.play_next_frame(5)

    def key_released(self, e):
        if e.key() == Qt.Key_Shift:
            self.player.shift_pressed = False

    # endregion

    # region youtube play buttons
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

    # endregion

    def clicked_file(self):
        self.select_file()

    def select_file(self):
        self.player.pause()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setWindowTitle('Open Video File')
        # dialog.setNameFilter('Video Fle (*.mov *.avi *.mp4)')
        # dialog.setFilter(QDir.Files)
        last_dir = self.settings.value("last_dir", "")
        if os.path.isdir(last_dir):
            dialog.setDirectory(last_dir)
        if dialog.exec_():
            dir_name = dialog.directory().absolutePath()
            dir_name = os.path.realpath(dir_name)
            self.settings.setValue("last_dir", dir_name)
            file_names = dialog.selectedFiles()
            if file_names and len(file_names) > 0:
                self.load_video(file_names[0])

    def load_video(self, file_name, change_size=True):
        if self.player.load_video(file_name):
            if change_size:
                self.just_loaded = 1
            self.settings.setValue("last_video", file_name)
            title = "{} - {}".format(self.title, file_name)
            self.setWindowTitle(title)
            _, name, _ = file_helper.get_file_name_extension(file_name)
            self.out_prefix = "{}_".format(name)
            self.check_saved_frames()

    def clicked_output_dir(self):
        self.select_out_dir()

    def select_out_dir(self):
        self.player.pause()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setWindowTitle('Select Output Directory')
        last_out_dir = self.settings.value("last_out_dir", "")
        if os.path.isdir(last_out_dir):
            dialog.setDirectory(last_out_dir)
        if dialog.exec_():
            dir_name = dialog.directory().absolutePath()
            dir_name = os.path.realpath(dir_name)
            self.settings.setValue("last_out_dir", dir_name)
            self.set_output_dir(dir_name)

    def save_current_frame(self, edit):
        play_speed = 0
        if edit:
            play_speed = self.player.speed()
            self.player.pause()
        if self.output_dir is None or not os.path.isdir(self.output_dir):
            self.select_out_dir()
        try:
            self.parent_app.setOverrideCursor(Qt.WaitCursor)
            if edit:
                self.parent_window.setCursor(Qt.WaitCursor)
            self.setCursor(Qt.WaitCursor)
            if self.output_dir is not None and os.path.isdir(self.output_dir):
                frame, index = self.player.get_current_frame_and_index()
                if frame is not None:
                    name = '{prefix}{num:0{width}}'.format(prefix=self.out_prefix, num=index, width=6)
                    fn = file_helper.path_join(self.output_dir, name + ".png")
                    cv2.imwrite(fn, frame)
                    if edit:
                        # if self.parent_window.lastOpenDir is None or not os.path.isdir(self.parent_window.lastOpenDir):
                        self.parent_window.importDirImages(self.output_dir)
                        self.parent_window.loadFile(fn)
                        self.parent_window.hide_video()
                        if play_speed < 0:
                            self.player.play_next_frame()
                            self.freeze_display_once = True
                        elif play_speed > 0:
                            self.player.play_previous_frame()
                            self.freeze_display_once = True
                        if self.player.speed_last() < 0:
                            self.player.play_previous_frame()
                        else:
                            self.player.play_next_frame()
        finally:
            self.parent_app.restoreOverrideCursor()
            self.setCursor(Qt.ArrowCursor)
            if edit:
                self.parent_window.setCursor(Qt.ArrowCursor)
            self.check_saved_frames()

    def _load_frame(self, frame, current_frame_index, time_text):
        if self.disabled_play_button_exists:
            self.pushButton_fast_left.setDisabled(False)
            self.pushButton_left.setDisabled(False)
            self.pushButton_right.setDisabled(False)
            self.pushButton_fast_right.setDisabled(False)

        if self.freeze_display_once:
            self.freeze_display_once = False
            return
        else:
            w, h = self.image_view.width(), self.image_view.height()
            if self.just_loaded == 1:
                self.just_loaded = 2
                w, h = frame.shape[1], frame.shape[0]
                self.image_view.setMinimumSize(w, h)
            elif self.just_loaded == 2:
                self.just_loaded = 0
                self.image_view.setMinimumSize(1, 1)

            h1, w1 = frame.shape[:2]
            image = QtGui.QImage(frame.data, w1, h1, QtGui.QImage.Format_BGR888)
            pixmap = QtGui.QPixmap.fromImage(image)
            pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio)
            self.image_view.setPixmap(pixmap)

            self.video_time_slider.setValue(current_frame_index)
            self.video_time_label.setText(time_text)

    def on_video_start(self):
        self.pushButton_fast_left.setDisabled(True)
        self.pushButton_left.setDisabled(True)
        self.disabled_play_button_exists = True

    def on_video_end(self):
        self.pushButton_right.setDisabled(True)
        self.pushButton_fast_right.setDisabled(True)
        self.disabled_play_button_exists = True

    def set_output_dir(self, dir_name):
        if dir_name is not None and os.path.isdir(dir_name):
            self.output_dir = dir_name
            self.settings.setValue("output_dir", dir_name)
            self.check_saved_frames()
        else:
            self.output_dir = None

    # region youtube
    def clicked_youtube(self):
        self.player.pause()
        res = show_download_video_dialog(self.parent_app, self.parent_window, self.default_font)
        print(res)
    # endregion


def show_video_player(parent_app, parent_window, output_dir, default_font):
    win = VideoPlayerMainWindow(parent_app=parent_app, parent_window=parent_window, default_font=default_font)
    # win.setWindowModality(Qt.WindowModal)
    win.set_output_dir(output_dir)
    win.show()
    return win


if __name__ == "__main__":
    # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app1 = QtWidgets.QApplication(sys.argv)
    win1 = VideoPlayerMainWindow(parent_app=app1, parent_window=None)
    win1.show()
    sys.exit(app1.exec_())
