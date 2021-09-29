import datetime
import os
import time

import cv2

from video_sources.video_source import VideoSource


# class FileVideoSource(VideoSource):
class FileVideoSource():
    def __init__(self, file_path):
        super().__init__()
        # self.stopped = False
        self.__video_path = file_path
        if self.__video_path is None:
            raise ValueError("Video file path is empty")

        if os.path.isfile(self.__video_path) is False:
            raise ValueError("Video file is not exist : %s", self.__video_path)
        self._set_capture()

    # def get_frames(self):
    #     count = 0
    #     self.stopped = False
    #     while not self.stopped and self.__capture.isOpened():
    #         ret, frame = self.__capture.read()
    #         if ret is False:
    #             break
    #
    #         yield count, frame
    #         count += 1
    #     self.stopped = True
    #     self.__capture.release()
    #     cv2.destroyAllWindows()
    #
    #     try:
    #         count = 0
    #         while self.__capture.isOpened():
    #             ok, frame = self.__capture.read()
    #             if not ok:
    #                 break
    #             yield count, frame
    #             count += 1
    #     except Exception as e:
    #         print(e)
    #     finally:
    #         print("video finished..")
    #         self.__capture.release()
    #         cv2.destroyAllWindows()

    def reset(self):
        self.stop()
        self._set_capture()

    # def stop(self):
    #     self.stopped = True

    # returns ok, frame
    def next(self, skip=0):
        if self.__capture.isOpened():
            if skip > 0:
                return self.goto(self.get_current_frame_index() + skip)
            else:
                return self.__capture.read()
        else:
            return False, None

    # returns ok, frame
    def previous(self, skip=0):
        if self.__capture.isOpened():
            if skip > 0:
                return self.goto(self.get_current_frame_index() - skip - 1)
            else:
                next_frame = self.__capture.get(cv2.CAP_PROP_POS_FRAMES)
                current_frame = next_frame - 1
                previous_frame = current_frame - 1
                return self.goto(previous_frame)
        else:
            return False, None

    # returns ok, frame
    def goto(self, frame_index):
        if frame_index >= 0:
            self.__capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            return self.__capture.read()
        else:
            return False, None

    def stop(self):
        try:
            self.__capture.release()
        except:
            pass

    def _set_capture(self):
        if os.path.isfile(self.__video_path) is False:
            raise ValueError("Video file is not exist")
        self.__capture = cv2.VideoCapture(self.__video_path)
        self.fps = self.__capture.get(cv2.CAP_PROP_FPS)
        self.frame_count = self.__capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.time_text_suffix = f" / {self.get_time_formatted(self.frame_count / self.fps)}"

    def get_current_frame_index(self):
        return int(self.__capture.get(cv2.CAP_PROP_POS_FRAMES) - 1)

    def get_time_text(self):
        cur_sec = self.get_current_frame_index() / self.fps
        return f"{self.get_time_formatted(cur_sec)}{self.time_text_suffix}"

    @staticmethod
    def get_time_formatted(seconds):
        s, ms = divmod(seconds * 1000, 1000)
        if s < 3600:
            return '{}.{}'.format(time.strftime('%M:%S', time.gmtime(s)), "{0:02d}".format(int(ms / 10)))
        else:
            return '{}.{}'.format(time.strftime('%H:%M:%S', time.gmtime(s)), "{0:02d}".format(int(ms / 10)))
