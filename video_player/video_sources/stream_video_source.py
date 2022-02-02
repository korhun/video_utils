import time
from vidgear.gears import CamGear

if __package__ is None or __package__ == '':
    from video_source import VideoSource
else:
    from .video_source import VideoSource


class StreamVideoSource(VideoSource):
    def __init__(self, url, youtube_mode):
        self._youtube_mode = youtube_mode
        self._fps = 0
        self._current_frame_index = 1
        super(StreamVideoSource, self).__init__()

        self._url = url
        if self._url is None:
            raise ValueError("Video url is empty")
        self._set_capture()

    def _set_capture(self):
        self._stream = CamGear(source=self._url, stream_mode=self._youtube_mode, time_delay=1, logging=False)
        self._stream.start()
        self._fps = self._stream.framerate

    def fps(self):
        return self._fps

    def reset(self):
        self.stop()
        self._set_capture()

    # returns ok, frame
    def next(self, skip=0):
        frame = self._stream.read()
        ok = frame is not None
        self._current_frame_index += 1
        return ok, frame

    # returns ok, frame
    def previous(self, skip=0):
        return False, None

    # returns ok, frame
    def goto(self, frame_index):
        return False, None

    def stop(self):
        try:
            self._stream.stop()
        except:
            pass

    def get_current_frame_index(self):
        return self._current_frame_index

    def get_time_text(self):
        cur_sec = self.get_current_frame_index() / self._fps
        return f"{self.get_time_formatted(cur_sec)}"

    @staticmethod
    def get_time_formatted(seconds):
        s, ms = divmod(seconds * 1000, 1000)
        if s < 3600:
            return '{}.{}'.format(time.strftime('%M:%S', time.gmtime(s)), "{0:02d}".format(int(ms / 10)))
        else:
            return '{}.{}'.format(time.strftime('%H:%M:%S', time.gmtime(s)), "{0:02d}".format(int(ms / 10)))

