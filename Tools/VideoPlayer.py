from threading import Thread, Event

import vlc
from pythonosc import udp_client

"""
Control for vlc player from python
"""

class Player(Thread):
    def __init__(self):
        self._instance = vlc.Instance(
            '-q --video-wallpaper --video-on-top -f') #-q, --quiet, --no-quiet        Be quiet (default disabled) Turn off all messages on the console.
        self._player = self._instance.media_player_new()
        self._player.audio_set_volume(0)
        self.finished = Event()
        self.reaper_client = udp_client.SimpleUDPClient("172.23.170.2", 8000)

        em = self._player.event_manager()
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self.end_reached)

    def play(self, path):
        self.finished.clear()
        media = self._instance.media_new(path)
        self._player.set_media(media)
        self._player.play()
        print("play")

    def pause(self):
        self._player.pause()

    def resume(self):
        self._player.play()

    def stop(self):
        self._player.stop()
        print("stopped")

    def end_reached(self, event):
        if event.type.value == vlc.EventType.MediaPlayerEndReached.value:
            self.finished.set()
            self.reaper_client.send_message("/stop", 1)
            print("finished")
