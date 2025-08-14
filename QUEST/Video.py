"""OSC Commands for MadMapper"""
# default OSC Port: 8010

madmapper = {
    "play": ["/play", 1],  # use as madmapper["play"][0].format("cue")
    "select": ["/cues/Bank-1/scenes/by_name/{}", 1],  # use as madmapper["select"][0].format("cue")
    "stop": ["/pause", 1],
    "pause": ["/pause", 1],
    "unpause": ["/play", 1],
    "reset": ["/medias/selected/position_sec", 0.0]
    # "loop_on": ["/medias/selected/loop", True],  # TBC
    # "loop_off": ["/medias/selected/loop", False],  # TBC
    # "restart": ["/medias/selected/restart"]  # TBC
}

vlc = {
    "play": ["/vlc_start", "{}"],
    "pause": ["/vlc_pause", 1],
    "unpause": ["/vlc_play", 1],
    "stop": ["/vlc_stop", 1],
    "black_screen": ["/vlc_still", 1],
    "blue_screen": ["/vlc_finish", 1]
}
