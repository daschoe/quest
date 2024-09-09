"""
Commands for controlling vlc player from python
"""
import argparse
import socket
from threading import Thread

from VideoPlayer import Player
from pythonosc import dispatcher
from pythonosc import osc_server


def vlc_start(unused_addr, args):
    """
    Start or resume a video in the current player.

    Parameters
    ----------
    unused_addr : any
    args : str or any
        if str: path of file to play
    """
    if args == "{}":
        pl.resume()
        print("status: resume")
    else:
        pl.play(args)
    print("status: play")


def vlc_stop(unused_addr, unused_args):
    """
    Stop the video in the current player (by pausing it).

    Parameters
    ----------
    unused_addr : any
    unused_args : any
    """
    pl.pause()
    print("status: pause")


def vlc_finish(unused_addr, unused_args):
    """
        Set an all black still image, e.g. when currently no video needs to be played.

        Parameters
        ----------
        unused_addr : any
        unused_args : any
    """
    video_thread = Thread(target=pl.play, args=("./Examples/black_3screens.mp4",))
    video_thread.run()
    print("status: finish")


def vlc_still(unused_addr, unused_args):
    """
        Set an all blue still image.
        Example use: Signal that the questionnaire is done.

        Parameters
        ----------
        unused_addr : any
        unused_args : any
    """
    video_thread = Thread(target=pl.play, args=("./Examples/blue_3screens.mp4",))
    video_thread.run()
    print("status: still")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5005, help="The port to listen on.")
    parser.add_argument("--reaper", type=bool, default=True, help="Flag to use Reaper (default: True).")
    parser.add_argument("--reaper_ip", default="127.0.0.1", help="IPv4 the computer hosting Reaper.")
    parser.add_argument("--reaper_port", type=int, default=8000, help="The port of Reaper.")
    arguments = parser.parse_args()

    pl = Player(reaper=arguments.reaper, reaper_ip=arguments.reaper_ip, reaper_port=arguments.reaper_port)
    vlc_still("", None)

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/vlc_start", vlc_start)  # play given video
    dispatcher.map("/vlc_pause", vlc_stop)  # pause given video
    dispatcher.map("/vlc_stop", vlc_stop)  # stop the current video/audio (set video to pause to keep still image)
    dispatcher.map("/vlc_finish", vlc_finish)  # close the player all together
    dispatcher.map("/vlc_still", vlc_still)  # show a still image

    ip = socket.gethostbyname(socket.gethostname())
    server = osc_server.ThreadingOSCUDPServer((ip, arguments.port), dispatcher)
    print(f'Serving on {server.server_address}')
    server.serve_forever()
