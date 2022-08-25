import argparse
import time
from threading import Thread

from VideoPlayer import Player
from pythonosc import dispatcher
from pythonosc import osc_server

"""
Commands for controlling vlc player from python
"""

def vlc_start(unused_addr, args):
    print(args)
    if args == 1: # TODO testen
        pl.resume()
    else:
        pl.play(args)
    print("status: play")

def vlc_stop(unused_addr, args):
    pl.pause()
    print("status: pause")

def vlc_finish(unused_addr, args):
    video_thread = Thread(target=pl.play, args=("./2019-07-04_PreTest/Video/Hauptstudie/output_b.mp4",))
    video_thread.run()
    print("status: finish")

def vlc_still(unused_addr, args):
    print(args)
    video_thread = Thread(target=pl.play, args=("./2019-07-04_PreTest/Video/Hauptstudie/output.mp4",))
    video_thread.run()
    print("status: still")

if __name__ == "__main__":
    pl = Player()    
    vlc_still("", "./2019-07-04_PreTest/Video/Hauptstudie/output.mp4")

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="172.23.170.2", help="IPv4 from this computer.")
    parser.add_argument("--port", type=int, default=5005, help="The port to listen on.")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/vlc_start", vlc_start) # play given video
    dispatcher.map("/vlc_stop", vlc_stop) # stop the current video/audio (set video to pause to keep still image)
    dispatcher.map("/vlc_finish", vlc_finish) # close the player alltogether
    dispatcher.map("/vlc_still", vlc_still) # show a still image

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
