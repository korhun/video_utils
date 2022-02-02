import functools
import os
import sys

import qdarkstyle
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSettings, QSize, QPoint, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QPushButton, QInputDialog, QProgressDialog

if __name__ == '__main__':
    from player import Player
    from utils import file_helper, image_helper, misc_helper
    from video_player import Ui_MainWindow
    from video_download.video_download_dialog_main import show_youtube_download_dialog
else:
    from .player import Player
    from .utils import file_helper, image_helper, misc_helper
    from .video_player import Ui_MainWindow
    from .video_download.video_download_dialog_main import show_youtube_download_dialog


# noinspection PyBroadException
class VideoPlayerMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent_app, parent_window=None, default_font=None, settings: QSettings = None):
        self._can_navigate = True
        self.parent_app = parent_app
        self.parent_window = parent_window
        self.parent_controls_output = self.parent_window is not None
        self.default_font = default_font
        self.freeze_display_once = False
        self.out_prefix = ""
        self.saved_frames = []
        self.btns = None
        self.current_file = None

        super(VideoPlayerMainWindow, self).__init__(parent=parent_window)
        self.setupUi(self)

        self.settings = QSettings('Orientis', 'video_player') if settings is None else settings
        self.recentVideos = self.settings.value("recentVideos", []) or []
        self.updateFileMenu()

        current_dir = os.path.dirname(os.path.abspath(__file__))

        self._img_play = QtGui.QIcon(file_helper.path_join(current_dir, 'img/play_right.png'))
        self._img_pause = QtGui.QIcon(file_helper.path_join(current_dir, 'img/pause.png'))

        self.pushButton_fast_left.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/fast_play_left.png')))
        self.pushButton_left.setIcon(QtGui.QIcon(file_helper.path_join(current_dir, 'img/play_left.png')))
        self.pushButton_pause.setIcon(self._img_pause)
        self.pushButton_right.setIcon(self._img_play)
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
        self.actionCam.triggered.connect(self.clicked_camera)
        self.actionOutput_Dir.triggered.connect(self.clicked_output_dir)
        self.pushButton_output_dir.clicked.connect(self.clicked_output_dir)

        self.actionYouTube.triggered.connect(self.clicked_youtube)
        self.actionYouTube_Download_with_youtube_dl.triggered.connect(self.clicked_youtube_download_youtube_dl)
        self.actionYouTube_Download_with_yt_dlp.triggered.connect(self.clicked_youtube_download_yt_dlp)

        self.actionURL.triggered.connect(self.clicked_url)

        self.actionSave_Current.setShortcut('Ctrl+S')

        self.actionSave_Current.triggered.connect(self.save_current_frame)
        self.pushButton_save.clicked.connect(lambda: self.save_current_frame(False))
        self.pushButton_save_and_edit.clicked.connect(lambda: self.save_current_frame(True))
        self.actionSave_Current_Image_and_Edit.triggered.connect(lambda: self.save_current_frame(True))

        self.actionSave_All_Frames.triggered.connect(self.save_all_frames)

        self.actionExit.triggered.connect(self.close_me)

        # self.image_view.setScaledContents(True)
        self.image_view.mousePressEvent = self.on_image_view_mouse_pressed
        self.image_view.setMinimumSize(1, 1)

        self.centralwidget.mousePressEvent = self.on_mouse_pressed

        self.title = self.windowTitle()

        self.player = Player(self, self.video_time_slider, self.speed_dial, self.speed_spin_box)
        self.player.frame_changed_signal.connect(self.on_frame_changed)
        self.player.video_start_signal.connect(self.on_video_start)
        self.player.video_end_signal.connect(self.on_video_end)
        self.player.speed_changed.connect(self.on_speed_changed)
        self.player.start()

        self.disabled_play_button_exists = True
        self.on_video_start()
        self.just_loaded = 0
        self.auto_size = False

        self.output_dir = None
        if not self.parent_controls_output:
            self.set_output_dir(self.settings.value("output_dir", ""))

        try:
            last_video_type = self.settings.value("last_video_type", "")
            if last_video_type == "file":
                last_video_file = self.settings.value("last_video_file", "")
                if os.path.isfile(last_video_file):
                    self.load_video_file(last_video_file, change_size=False)
            # elif last_video_type == "camera":
            #     self.load_video_camera(change_size=False)
            # elif last_video_type == "youtube":
            #     self.load_url(self.settings.value("last_youtube_url"), is_youtube=True)
            # elif last_video_type == "stream":
            #     self.load_url(self.settings.value("last_stream_url"), is_youtube=False)
        except:
            self.settings.setValue("last_video_type", "")
            self.settings.setValue("last_video_file", "")

        self.resize(self.settings.value("size", QSize(600 * 1.61803398875, 600)))
        self.move(self.settings.value("pos", QPoint(200 * 1.61803398875, 200)))

        if self.parent_controls_output:
            self.pushButton_output_dir.setVisible(False)
        else:
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

        self._freeze_goto_frame_by_file_name = False

        self._txt_Open_Video_File = self.tr('Open Video File')
        self._txt_Select_Output_Directory = self.tr('Select Output Directory')
        self._txt_save_all_frames_title = self.tr('Save All Frames')
        self._txt_save_all_frames_label_text = self.tr('Set number of frames to be skipped between each frame to be saved. {0}For example, if you set {1}, a single frame for each second will be saved. {0}If you set the value as 0, every frame in the video will be extracted.')
        self._txt_progress_extracting_frames = self.tr("Extracting frames...")
        self._txt_progress_abort = self.tr("Abort")
        self._txt_cannot_load_file = self.tr("<p>Cannot load file!</p>\n<p><b>{}</b></p>")
        self._txt_warning_title = self.tr("Warning")

    def closeEvent(self, e):
        self.player.release()
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())

    def close_me(self):
        self.closeEvent(None)
        self.close()

    def is_closed(self):
        return not self.player.running()

    def showEvent(self, e):
        if self.player.get_frame_count() <= 0:
            self.player.play_right(forced=True)

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
                sliderMax = gr.bottom() - sliderLength + 1
            pr = pos - sr.center() + sr.topLeft()
            p = pr.x() if ctrl.orientation() == Qt.Horizontal else pr.y()
            return QtWidgets.QStyle.sliderValueFromPosition(ctrl.minimum(), ctrl.maximum(), p - sliderMin,
                                                            sliderMax - sliderMin, opt.upsideDown)

        e_type = e.type()
        update_required = False
        if obj == self.video_time_slider:
            if e_type == QEvent.MouseButtonRelease or e_type == QEvent.MouseButtonPress:
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

                        btn.clicked.connect(lambda state, index=frame_index: self.btn_clicked(index))
                        self.btns.append(btn)
                    except:
                        pass
                self.saved_frames.sort()
        finally:
            self.update_saved_frame_locations()
            self.video_time_slider.repaint()
            if self.parent_controls_output:
                self.parent_window.importDirImages(self.output_dir, load=False)

    def btn_clicked(self, index):
        self.player.pause()
        self.player.goto_frame(index)
        if self.parent_window is not None:
            fn = self._get_save_file_name(index)
            if fn and os.path.isfile(fn):
                self.parent_window.loadFile(fn)

    def on_mouse_pressed(self, _):
        self.update_saved_frame_locations()
        focused_widget = self.focusWidget()
        if focused_widget is not None:
            focused_widget.clearFocus()

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
        if not self._can_navigate:
            self.player.toggle()
        else:
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
        dialog.setWindowTitle(self._txt_Open_Video_File)
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
                self.load_video_file(file_names[0])

    def load_video_file(self, file_name, change_size=True):
        if self.player.load_video_file(file_name):
            self.statusbar.clearMessage()
            self.current_file = file_name
            self._can_navigate = self.player.get_frame_count() > 0
            self.update_buttons()
            if change_size:
                self.just_loaded = 1
            self.settings.setValue("last_video_file", file_name)
            self.settings.setValue("last_video_type", "file")
            title = "{} - {}".format(self.title, file_name)
            self.setWindowTitle(title)
            _, name, _ = file_helper.get_file_name_extension(file_name)
            self.out_prefix = "{}_".format(name)
            self.check_saved_frames()
            self.addRecentVideos(filename=file_name)
        else:
            return QtWidgets.QMessageBox.warning(self, self._txt_warning_title, self._txt_cannot_load_file.format(file_name))

    def clicked_camera(self):
        self.load_video_camera()

    def load_video_camera(self, change_size=True):
        if self.player.load_video_camera():
            self._can_navigate = False
            self.update_buttons()
            if change_size:
                self.just_loaded = 1
            self.settings.setValue("last_video_type", "camera")
            title = "{} - {}".format(self.title, "cam")
            self.setWindowTitle(title)
            name = "cam"
            self.out_prefix = "{}_".format(name)
            self.check_saved_frames()
            self.player.play_right(forced=True)

    def load_url(self, url, is_youtube, change_size=True):
        if self.player.load_url(url, is_youtube=is_youtube):
            self._can_navigate = False
            self.update_buttons()
            if change_size:
                self.just_loaded = 1
            if is_youtube:
                self.settings.setValue("last_video_type", "youtube")
                self.settings.setValue("last_youtube_url", url)
            else:
                self.settings.setValue("last_video_type", "stream")
                self.settings.setValue("last_stream_url", url)
            name = "youtube" if is_youtube else "url"
            title = "{} - {}".format(self.title, name)
            self.setWindowTitle(title)
            self.out_prefix = "{}_".format(name)
            self.check_saved_frames()
            self.player.play_right(forced=True)

    def update_buttons(self):
        self.pushButton_fast_left.setVisible(self._can_navigate)
        self.pushButton_left.setVisible(self._can_navigate)
        self.pushButton_right.setVisible(self._can_navigate)
        self.pushButton_fast_right.setVisible(self._can_navigate)
        self.video_time_slider.setVisible(self._can_navigate)
        self.speed_dial.setVisible(self._can_navigate)
        self.speed_spin_box.setVisible(self._can_navigate)
        if self._can_navigate:
            self.pushButton_pause.setIcon(self._img_pause)

    def on_speed_changed(self, speed):
        if not self._can_navigate:
            if speed == 0:
                self.pushButton_pause.setIcon(self._img_play)
            else:
                self.pushButton_pause.setIcon(self._img_pause)

    def clicked_output_dir(self):
        self.select_out_dir()

    def select_out_dir(self):
        self.player.pause()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setWindowTitle(self._txt_Select_Output_Directory)
        if self.current_file:
            cur_dir = file_helper.get_parent_dir_path(self.current_file)
        else:
            cur_dir = ""
        last_out_dir = self.settings.value("last_out_dir", cur_dir)
        dir_name = dialog.getExistingDirectory(self, self._txt_Select_Output_Directory, last_out_dir)
        if dir_name:
            dir_name = os.path.realpath(dir_name)
            self.settings.setValue("last_out_dir", dir_name)
            self.set_output_dir(dir_name)

    def _get_save_file_name(self, index):
        if self.output_dir:
            name = '{prefix}{num:0{width}}'.format(prefix=self.out_prefix, num=index, width=6)
            return file_helper.path_join(self.output_dir, name + ".png")

    def _get_frame_index_by_file_name(self, file_name):
        try:
            if file_name is not None:
                dir_name, name, extension = file_helper.get_file_name_extension(file_name)
                if name.startswith(self.out_prefix):
                    name = name.replace(self.out_prefix, "")
                    return misc_helper.try_parse_int(name, -1)
            return -1
        except:
            return -1

    def goto_frame_by_file_name(self, file_name):
        if not self._freeze_goto_frame_by_file_name:
            index = self._get_frame_index_by_file_name(file_name)
            if index >= 0:
                self.player.pause()
                self.player.goto_frame(index)

    def cursor_wait(self):
        self.parent_app.setOverrideCursor(Qt.WaitCursor)
        if self.parent_window is not None:
            self.parent_window.setCursor(Qt.WaitCursor)
        self.setCursor(Qt.WaitCursor)

    def cursor_restore(self):
        self.parent_app.restoreOverrideCursor()
        if self.parent_window is not None:
            self.parent_window.setCursor(Qt.ArrowCursor)
        self.setCursor(Qt.ArrowCursor)

    def save_current_frame(self, edit):
        play_speed = 0
        if edit:
            play_speed = self.player.speed()
            self.player.pause()
        if self.output_dir is None or not os.path.isdir(self.output_dir):
            self.select_out_dir()
        try:
            self.cursor_wait()
            if self.output_dir is not None and os.path.isdir(self.output_dir):
                frame, index = self.player.get_current_frame_and_index()
                if frame is not None:
                    fn = self._get_save_file_name(index)
                    image_helper.write(frame, fn, save_thumbnail=True)
                    if edit:
                        self.parent_window.importDirImages(self.output_dir, load=False)
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
                    elif self.parent_window is not None:
                        old_val = self._freeze_goto_frame_by_file_name
                        self._freeze_goto_frame_by_file_name = True
                        try:
                            self.parent_window.loadFile(fn)
                        finally:
                            self._freeze_goto_frame_by_file_name = old_val
        finally:
            self.check_saved_frames()
            self.cursor_restore()

    def on_frame_changed(self, frame, current_frame_index, time_text):
        if self.disabled_play_button_exists:
            self.pushButton_fast_left.setDisabled(False)
            self.pushButton_left.setDisabled(False)
            self.pushButton_right.setDisabled(False)
            self.pushButton_fast_right.setDisabled(False)
            self.disabled_play_button_exists = False

        if self.freeze_display_once:
            self.freeze_display_once = False
            return
        else:
            h0, w0 = frame.shape[:2]
            self.statusbar.showMessage("{} x {} - FPS: {}".format(w0, h0, int(round(self.player.fps()))))

            w, h = self.image_view.width(), self.image_view.height()
            frame = image_helper.resize_keep_aspect_ratio(frame, w, h)

            h1, w1 = frame.shape[:2]
            image = QtGui.QImage(frame.data, w1, h1, 3 * w1, QtGui.QImage.Format_BGR888)
            pixmap = QtGui.QPixmap.fromImage(image)
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
            if not self.parent_controls_output:
                self.settings.setValue("output_dir", dir_name)
            self.check_saved_frames()
            if self.parent_window is not None:
                self.parent_window.importDirImages(self.output_dir, load=False)
        else:
            self.output_dir = None

    def addRecentVideos(self, filename):
        if filename in self.recentVideos:
            self.recentVideos.remove(filename)
        elif len(self.recentVideos) >= 8:
            self.recentVideos.pop()
        self.recentVideos.insert(0, filename)
        self.settings.setValue("recentVideos", self.recentVideos)
        self.updateFileMenu()

    def updateFileMenu(self):
        menu = self.menuRecent_Files
        menu.clear()
        files = [f for f in self.recentVideos if os.path.exists(f)]
        for i, f in enumerate(files):
            action = QtWidgets.QAction("&%d %s" % (i + 1, QtCore.QFileInfo(f).fileName()), self)
            action.triggered.connect(functools.partial(self.load_video_file, f))
            menu.addAction(action)

    # region youtube - url
    def clicked_url(self):
        self._clicked_stream(url=self.settings.value("last_stream_url"), title="Stream", label_text="URL", is_youtube=False)

    def clicked_youtube(self):
        self._clicked_stream(url=self.settings.value("last_youtube_url"), title="YouTube", label_text="URL", is_youtube=True)

    def _clicked_stream(self, url, title, label_text, is_youtube):
        dlg = QInputDialog(self)
        dlg.setInputMode(QInputDialog.TextInput)
        dlg.setWindowTitle(title)
        dlg.setLabelText(label_text)
        dlg.setTextValue(url)
        dlg.resize(600, 100)
        dlg.setMaximumSize(5500, 100)
        ok = dlg.exec_()
        if ok:
            url = dlg.textValue()
            if url:
                self.load_url(url, is_youtube=is_youtube)

    def clicked_youtube_download_youtube_dl(self):
        self._clicked_youtube_download("youtube_dl")

    def clicked_youtube_download_yt_dlp(self):
        self._clicked_youtube_download("yt_dlp")

    def _clicked_youtube_download(self, style: str):
        self.player.pause()
        url = self.settings.value("youtube_url")
        outdir = self.settings.value("youtube_outdir")
        file_name = self.settings.value("youtube_file_name")
        ok, url, outdir, file_name, downloaded_file = show_youtube_download_dialog(self.parent_app, self, self.default_font, url=url, outdir=outdir, file_name=file_name, style=style)
        self.settings.setValue("youtube_url", url)
        self.settings.setValue("youtube_outdir", outdir)
        self.settings.setValue("youtube_file_name", file_name)
        if ok:
            self.load_video_file(downloaded_file)

    # endregion

    def save_all_frames(self):
        self.player.pause()
        dlg = QInputDialog(self)
        dlg.setInputMode(QInputDialog.TextInput)
        dlg.setWindowTitle(self._txt_save_all_frames_title)
        fps = int(round(self.player.fps()))
        txt = self._txt_save_all_frames_label_text.format(os.linesep, str(fps))
        dlg.setLabelText(txt)
        dlg.setIntMinimum(0)
        dlg.setIntMaximum(999999999)
        dlg.setIntValue(fps)
        dlg.setIntStep(fps)
        dlg.resize(300, 100)
        dlg.setMaximumSize(5500, 100)
        dlg.setWhatsThis(txt)
        ok = dlg.exec_()
        if ok:
            step = dlg.intValue()
            if step >= 0:
                if self.output_dir is None or not os.path.isdir(self.output_dir):
                    self.select_out_dir()
                self._save_every_frame(step)

    def _save_every_frame(self, step):
        try:
            num = self.player.get_frame_count()
            if step > 0:
                num = int(num / step)
            progress = QProgressDialog(self._txt_progress_extracting_frames, self._txt_progress_abort, 0, num, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumWidth(460)
            i = 0
            for frame, index in self.player.enumerate_frames(start_index=0, step=step):
                progress.setValue(i)
                i += 1
                if progress.wasCanceled():
                    break
                image_helper.write(frame, self._get_save_file_name(index), save_thumbnail=True)
            progress.setValue(num)
        finally:
            self.check_saved_frames()
            self.cursor_restore()


def create_video_player_window(parent_app, parent_window, output_dir, default_font, settings) -> VideoPlayerMainWindow:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    translator = QtCore.QTranslator()
    qm_file = file_helper.path_join(current_dir, 'video_player-tr.qm')
    translator.load(qm_file)
    parent_app.installTranslator(translator)

    win = VideoPlayerMainWindow(parent_app=parent_app, parent_window=parent_window, default_font=default_font, settings=settings)
    # win.setWindowModality(Qt.WindowModal)
    win.set_output_dir(output_dir)
    return win


if __name__ == "__main__":
    # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app1 = QtWidgets.QApplication(sys.argv)
    win1 = create_video_player_window(app1, None, "", None, None)

    # # https://stackoverflow.com/a/56550014/1266873
    # win1.setWindowFlags(win1.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    # win1.show()
    # win1.setWindowFlags(win1.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
    # win1.show()

    win1.raise_()
    win1.show()
    win1.activateWindow()

    sys.exit(app1.exec_())
