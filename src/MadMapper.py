"""OSC Commands for MadMapper"""
# default OSC Port: 8010

commands = {
    "play": ["/medias/[selected OR sourceName]/play_forward", True],
    "stop": ["/medias/selected/play_forward", False],
    "pause": ["/medias/selected/pause", True],
    "unpause": ["/medias/selected/pause", False],
    "loop_on": ["/medias/selected/loop", True],
    "loop_off": ["/medias/selected/loop", False],
    "restart": ["/medias/selected/restart"]
}