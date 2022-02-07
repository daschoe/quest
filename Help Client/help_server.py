""" OSC Connection to listen for a help request from the participant and display progress report.
    default port: 5005
"""
import argparse
import socket
from datetime import timedelta
from colorama import Back, init
from ping3 import ping
from pythonosc import dispatcher
from pythonosc import osc_server
from timeloop import Timeloop

HOST = "127.0.0.1"  # TODO change to your GUI's address
WAIT_TIME_SECONDS = 60  # TODO change this to your liking
TIMEOUT = 0.75  # TODO change this to your liking

tl = Timeloop()


def request(unused_addr, opt_args):
    """ The participant pressed the help button.

    Parameters
    ----------
    unused_addr : str
        address of the sender
    opt_args : str or list[str]
        optional arguments
    """
    print(Back.YELLOW+"Help requested.")


def page(unused_addr, opt_args):
    """ The participant pressed the help button.

    Parameters
    ----------
    unused_addr : str
        address of the sender
    opt_args : str or list[str]
        optional arguments, here page number
    """
    print("Page {}".format(opt_args))


def connection(unused_addr, opt_args):
    """ The GUI has lost the connection to pupil.

    Parameters
    ----------
    unused_addr : str
        address of the sender
    opt_args : str or list[str]
        optional arguments
    """
    print(Back.RED+"Connection to pupil capture lost.")


def finished(unused_addr, opt_args):
    """ The participant finished the questionnaire.

        Parameters
        ----------
        unused_addr : str
            address of the sender
        opt_args : str or list[str]
            optional arguments
        """
    print(Back.GREEN+"Questionnaire finished.")
    tl.stop()
    # server.server_close()  # close the window manually, as this statement will throw exceptions


@tl.job(interval=timedelta(seconds=WAIT_TIME_SECONDS))
def send_ping():
    """Send a ping to the GUI's machine."""
    # noinspection PyTypeChecker
    response = ping(HOST, timeout=TIMEOUT)
    if response is None:
        print(Back.RED+"Connection to GUI lost.")
    else:
        print("Everything is fine :)")


if __name__ == "__main__":
    init(autoreset=True)
    own_ip = socket.gethostbyname(socket.gethostname())
    print("Own IP:", own_ip)
    tl.start(block=False)
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default=own_ip, help="IPv4 of this computer.")
    parser.add_argument("--port", type=int, default=5005, help="The port to listen on.")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    # noinspection PyTypeChecker
    dispatcher.map("/help_request", request)
    # noinspection PyTypeChecker
    dispatcher.map("/page", page)
    # noinspection PyTypeChecker
    dispatcher.map("/connection_lost", connection)
    # noinspection PyTypeChecker
    dispatcher.map("/questionnaire_finished", finished)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
