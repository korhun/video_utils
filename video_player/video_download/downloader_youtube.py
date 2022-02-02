import youtube_dl
# pip install --upgrade yt-dlp
import yt_dlp
from PyQt5.QtCore import QThread, pyqtSignal

if __package__ is None or __package__ == '':
    from downloader import Downloader
else:
    from .downloader import Downloader


class YoutubeDownloader(QThread, Downloader):
    download_progress = pyqtSignal(float)
    download_finished = pyqtSignal(str)
    download_warning = pyqtSignal(str)
    download_error = pyqtSignal(str)

    def __init__(self, style: str):
        if style == "yt_dlp":
            self._is_yt_dlp = True
        elif style == "youtube_dl":
            self._is_yt_dlp = False
        else:
            raise NotImplementedError()
        super(YoutubeDownloader, self).__init__()
        self._url = None
        self._file_name = None
        self._downloading = False

    def is_downloading(self):
        return self._downloading

    def stop_download(self):
        if self._downloading:
            self.terminate()
            self._downloading = False

    def start_download(self, url: str, file_name: str):
        self.stop_download()
        self._downloading = True
        self._url = url
        self._file_name = file_name
        self.start()

    def run(self):
        try:
            ydl_opts = {
                # 'format': 'bestaudio/best',
                # 'format': 'best',
                'format': 'bestvideo*+bestaudio/best',
                # 'postprocessors': [{
                #     'key': 'FFmpegExtractAudio',
                #     'preferredcodec': 'mp3',
                #     'preferredquality': '192',
                # }],
                'logger': self,
                'progress_hooks': [self._on_progress],
                'outtmpl': self._file_name
            }
            if self._is_yt_dlp:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self._url])
            else:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self._url])
        except Exception as e:
            self.download_error.emit(str(e))

    # region logger
    def debug(self, msg):
        pass

    def warning(self, msg):
        # self.download_warning.emit(msg)
        pass

    def error(self, msg):
        self.download_error.emit(msg)

    # endregion

    def _on_progress(self, info):
        status = info['status']
        if status == 'downloading':
            try:
                downloaded_bytes = info['downloaded_bytes']
                total_bytes = None
                if 'total_bytes' in info:
                    total_bytes = info['total_bytes']
                elif 'total_bytes_estimate' in info:
                    total_bytes = info['total_bytes_estimate']
                if total_bytes is not None:
                    pr = 100.0 * downloaded_bytes / total_bytes
                    self.download_progress.emit(pr)
            except Exception as e:
                self.download_error.emit(str(e))
        elif status == 'finished':
            self.download_finished.emit(info['filename'])
        else:
            print(status)

    def get_name(self, url):
        try:
            ydl_opts = {}
            if self._is_yt_dlp:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url=url, download=False, process=False)
                    return info.get("title")
            else:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url=url, download=False, process=False)
                    return info.get("title")
        except Exception as e:
            self.download_error.emit(str(e))
            return None
