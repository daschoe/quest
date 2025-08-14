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

HOST = "127.0.0.1"
WAIT_TIME_SECONDS = 60
TIMEOUT = 0.75

tl = Timeloop()
SERVER = None


def request(unused_addr, opt_args):
    """ The participant pressed the help button.

    Parameters
    ----------
    unused_addr : str
        address of the sender
    opt_args : str or list[str]
        optional arguments
    """
    print(Back.YELLOW + "Help requested.")


def page(unused_addr, opt_args):
    """ The participant pressed the help button.

    Parameters
    ----------
    unused_addr : str
        address of the sender
    opt_args : str or list[str]
        optional arguments, here page number
    """
    print(f'Page {opt_args}')


def connection(unused_addr, opt_args):
    """ The GUI has lost the connection to pupil.

    Parameters
    ----------
    unused_addr : str
        address of the sender
    opt_args : str or list[str]
        optional arguments
    """
    print(Back.RED + "Connection to pupil capture lost.")


def finished(unused_addr, opt_args):
    """ The participant finished the questionnaire.

        Parameters
        ----------
        unused_addr : str
            address of the sender
        opt_args : str or list[str]
            optional arguments
        """
    print(Back.GREEN + "Questionnaire finished.")
    tl.stop()
    # server.server_close()  # close the window manually, as this statement will throw exceptions


@tl.job(interval=timedelta(seconds=WAIT_TIME_SECONDS))
def send_ping():
    """Send a ping to the GUI's machine."""
    # noinspection PyTypeChecker
    print(f'Pinging {HOST} every {WAIT_TIME_SECONDS} seconds with timeout {TIMEOUT}.')
    response = ping(HOST, timeout=TIMEOUT)
    if response is None:
        print(Back.RED + "Connection to GUI lost.")
    else:
        print("Everything is fine :)")


if __name__ == "__main__":
    init(autoreset=True)
    own_ip = socket.gethostbyname(socket.gethostname())
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5005, help="The port to listen on.")
    parser.add_argument("--ping_ip", type=str, default=HOST, help="IP of the GUI to ping to.")  # TODO testen
    parser.add_argument("--ping_timeout", type=float, default=TIMEOUT, help="Timeout for ping back of GUI.")  # TODO testen
    args = parser.parse_args()
    if args.ping_ip is not None:
        HOST = args.ping_ip
    if args.ping_timeout is not None:
        TIMEOUT = args.ping_timeout
    print(f'Pinging {HOST} every {WAIT_TIME_SECONDS} seconds with timeout {TIMEOUT}.')
    tl.start(block=False)

    dispatcher = dispatcher.Dispatcher()
    # noinspection PyTypeChecker
    dispatcher.map("/help_request", request)
    # noinspection PyTypeChecker
    dispatcher.map("/page", page)
    # noinspection PyTypeChecker
    dispatcher.map("/connection_lost", connection)
    # noinspection PyTypeChecker
    dispatcher.map("/questionnaire_finished", finished)

    SERVER = osc_server.ThreadingOSCUDPServer((own_ip, args.port), dispatcher)
    print(f'Serving on {SERVER.server_address}')
    SERVER.serve_forever()
