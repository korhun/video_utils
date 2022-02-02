from __future__ import unicode_literals

import os
import sys

import qdarkstyle
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox

if __name__ == '__main__':
    from video_download_dialog import Ui_VideoDownloadDialog
    from downloader import Downloader
    from downloader_youtube import YoutubeDownloader
else:
    from .video_download_dialog import Ui_VideoDownloadDialog
    from .downloader import Downloader
    from .downloader_youtube import YoutubeDownloader

if __package__ is None or __package__ == '':
    from labelme.video_player.utils import file_helper
elif __package__ == 'video_download':
    from utils import file_helper
else:
    from ..utils import file_helper


class VideoDownloadDialogWindow(QDialog, Ui_VideoDownloadDialog):

    def __init__(self, downloader: Downloader, parent_app, parent_window=None, default_font=None, style: str = ""):
        self.downloader = downloader
        self._style = style
        self.downloader.download_finished.connect(self.on_download_finished)
        self.downloader.download_error.connect(self.on_download_error)
        self.downloader.download_warning.connect(self.on_download_warning)
        self.downloader.download_progress.connect(self.on_download_progress)

        self.parent_app = parent_app
        self.parent_window = parent_window
        self.default_font = default_font
        self.freeze_display_once = False
        self.out_prefix = ""
        self.saved_frames = []
        self.btns = None

        super().__init__(parent=parent_window)
        # self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setupUi(self)

        title = "{} ({})".format(self.windowTitle(), self._style)
        self.setWindowTitle(title)

        self._outdir_dialog_title = self.tr('Output Directory')

        self.pushButtonDownload.setDisabled(True)
        self.pushButtonStop.hide()
        self.progressBar.hide()

        self.pushButtonOutdir.clicked.connect(self.clicked_outdir)
        self.pushButtonName.clicked.connect(self.download_name)
        self.pushButtonDownload.clicked.connect(self.download_start)
        self.pushButtonStop.clicked.connect(self.download_stop)

        self.lineEditUrl.textChanged.connect(self.update)
        self.lineEditOutdir.textChanged.connect(self.update)
        self.lineEditName.textChanged.connect(self.update)

        self.pushButtonCancel.clicked.connect(self.clicked_cancel)

        self.last_url = None
        self.last_name = None
        self.downloaded_file = None
        self.closed_with_ok = False

    def closeEvent(self, e):
        self.download_stop()

    def url(self):
        return self.lineEditUrl.text()

    def setUrl(self, url):
        self.lineEditUrl.setText(url)
        self.update()

    def outdir(self):
        return self.lineEditOutdir.text()

    def setOutdir(self, dir):
        self.lineEditOutdir.setText(dir)
        self.update()

    def filename(self):
        return self.lineEditName.text()

    def setFilename(self, name):
        self.lineEditName.setText(name)
        self.update()

    def clicked_outdir(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        # dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setWindowTitle(self._outdir_dialog_title)
        dir_name = self.outdir()
        if file_helper.dir_exists(dir_name):
            dialog.setDirectory(dir_name)
        if dialog.exec_():
            dir_name = dialog.directory().absolutePath()
            dir_name = os.path.realpath(dir_name)
            self.setOutdir(dir_name)
        self.update()

    def download_start(self):
        self.progressBar.setValue(0)
        self.pushButtonDownload.hide()
        self.pushButtonStop.show()
        self.progressBar.show()

        outdir = self.outdir()
        name = self.filename()
        if self._style == "youtube_dl":
            file_full_name = file_helper.path_join(outdir, name + ".mp4")
        else:
            file_full_name = file_helper.path_join(outdir, name)
        self.downloader.start_download(self.url(), file_full_name)
        self.update()
        self.set_cursor_wait()

    def download_stop(self):
        self.downloader.stop_download()
        self.pushButtonStop.hide()
        self.pushButtonDownload.show()
        self.progressBar.hide()
        self.update()
        self.set_cursor_restore()

    def on_download_finished(self, file_name: str):
        self.downloaded_file = file_name
        self.download_stop()
        self.update()
        if file_helper.file_exists(file_name):
            self.close_ok()

    def on_download_error(self, text: str):
        self.set_cursor_restore()
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setInformativeText('More information')
        msg.setWindowTitle("Error")
        msg.exec_()
        self.download_stop()

    def on_download_warning(self, text: str):
        self.set_cursor_restore()
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)
        msg.setInformativeText('More information')
        msg.setWindowTitle("Warning")
        msg.exec_()
        self.set_cursor_wait()
        # self.download_stop()

    def on_download_progress(self, value: float):
        self.progressBar.setValue(value)

    def update(self):
        url = self.url()
        outdir = self.outdir()
        name = self.filename()
        self.pushButtonDownload.setDisabled(not url or not outdir or not name)
        not_downloading = not self.downloader.is_downloading()
        self.lineEditUrl.setEnabled(not_downloading)
        self.lineEditName.setEnabled(not_downloading)
        self.lineEditOutdir.setEnabled(not_downloading)
        self.pushButtonName.setEnabled(not_downloading)
        self.pushButtonOutdir.setEnabled(not_downloading)

    def download_name(self):
        try:
            self.set_cursor_wait()
            url = self.url()
            if url and self.last_url != url:
                self.last_url = url
                self.last_name = self.downloader.get_name(url)
            self.setFilename(self.last_name)
        finally:
            self.set_cursor_restore()

    def set_cursor_wait(self):
        self.parent_app.setOverrideCursor(QtCore.Qt.WaitCursor)
        if self.parent_window is not None:
            self.parent_window.setCursor(QtCore.Qt.WaitCursor)
        self.setCursor(QtCore.Qt.WaitCursor)

    def set_cursor_restore(self):
        self.parent_app.restoreOverrideCursor()
        if self.parent_window is not None:
            self.parent_window.setCursor(QtCore.Qt.ArrowCursor)
        self.setCursor(QtCore.Qt.ArrowCursor)

    def clicked_cancel(self):
        self.closed_with_ok = False
        self.close()

    def close_ok(self):
        self.closed_with_ok = True and file_helper.file_exists(self.downloaded_file)
        self.close()


def show_youtube_download_dialog(parent_app, parent_window, default_font, url, outdir, file_name, style: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    translator = QtCore.QTranslator()
    qm_file = file_helper.path_join(current_dir, 'video_download_dialog-tr.qm')
    translator.load(qm_file)
    parent_app.installTranslator(translator)

    downloader = YoutubeDownloader(style)
    win = VideoDownloadDialogWindow(downloader, parent_app=parent_app, parent_window=parent_window, default_font=default_font, style=style)
    win.setWindowModality(QtCore.Qt.ApplicationModal)
    win.setUrl(url)
    win.setOutdir(outdir)
    win.setFilename(file_name)
    if parent_window is None:
        win.setStyleSheet(qdarkstyle.load_stylesheet(palette=qdarkstyle.DarkPalette))
    win.show()
    win.exec_()
    ok = win.closed_with_ok
    downloaded_file = win.downloaded_file if ok else None
    return ok, win.url(), win.outdir(), win.filename(), downloaded_file


if __name__ == "__main__":
    # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    settings = QSettings('video_download_dialog_test', 'video_download')
    app1 = QtWidgets.QApplication(sys.argv)
    # win1 = VideoDownloadDialogWindow(parent_app=app1, parent_window=None)

    from labelme.video_player.video_download.downloader_youtube import YoutubeDownloader

    ok1, url1, outdir1, name1 = show_youtube_download_dialog(parent_app=app1, parent_window=None, default_font=None, url=settings.value("youtube_url"), outdir=settings.value("youtube_outdir"), file_name=settings.value("youtube_name"))
    settings.setValue("youtube_url", url1)
    settings.setValue("youtube_outdir", outdir1)
    settings.setValue("youtube_name", name1)
