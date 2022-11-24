"""
Control for vlc player from python
"""

from threading import Thread, Event

import vlc
from pythonosc import udp_client


class Player(Thread):
    """Python-callable instance of a VLC media player."""
    def __init__(self, reaper=True, reaper_ip="127.0.0.1", reaper_port=8000):
        self._instance = vlc.Instance(
            '-q --video-wallpaper --video-on-top -f')
        # -q, --quiet, --no-quiet : Be quiet (default disabled) Turn off all messages on the console.
        self._player = self._instance.media_player_new()
        self._player.audio_set_volume(0)
        self.finished = Event()
        if reaper:
            self.reaper_client = udp_client.SimpleUDPClient(reaper_ip, reaper_port)
        else:
            self.reaper_client = None

        em = self._player.event_manager()
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self.end_reached)

    def play(self, path):
        """
        Play a new video from the beginning.

        Parameters
        ----------
        path : str
            path+filename of video to play
        """
        self.finished.clear()
        media = self._instance.media_new(path)
        self._player.set_media(media)
        self._player.play()
        print("play")

    def pause(self):
        """
        Pauses the currently playing video.
        """
        self._player.pause()
        print("pause")

    def resume(self):
        """
        Resume the current video after pause from the same position.
        """
        self._player.play()
        print("resume")

    def stop(self):
        """
        Stop the currently playing video.
        """
        self._player.stop()
        print("stopped")

    def end_reached(self, event):
        """
        When the end of the video was reached stop the audio as well (if Reaper is used).

        Parameters
        ----------
        event : vlc.event
            event that happened
        """
        if event.type.value == vlc.EventType.MediaPlayerEndReached.value:
            self.finished.set()
            if self.reaper_client is not None:
                self.reaper_client.send_message("/stop", 1)
            print("finished")
