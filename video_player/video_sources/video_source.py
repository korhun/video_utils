from abc import ABC, abstractmethod


# import logging
# from enum import Enum

# log = logging.getLogger("video_source")

# class VideoSourceType(Enum):
#     VIDEO_FILE = 1
#     PI_CAMERA = 2
#     CAMERA = 3
#     IP_CAMERA = 4
#     VIDEO_URL = 5
#     YOUTUBE = 6
#     IMAGE_FILE = 7


class VideoSource(ABC):

    @abstractmethod
    def reset(self) -> None:
        pass

    # returns ok, frame
    @abstractmethod
    def next(self, skip=0) -> (bool, any):
        pass

    # returns ok, frame
    @abstractmethod
    def previous(self, skip=0) -> (bool, any):
        pass

    # returns ok, frame
    @abstractmethod
    def goto(self, frame_index) -> (bool, any):
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def get_current_frame_index(self) -> int:
        pass

    @abstractmethod
    def get_time_text(self) -> str:
        pass

    @abstractmethod
    def fps(self) -> int:
        pass
