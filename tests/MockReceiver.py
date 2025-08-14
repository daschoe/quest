"""A mocked receiver to emulate sending/receiving of OSC messages for the testcases."""
import threading
from threading import Thread
from pythonosc import dispatcher, osc_server

SLEEP_TIME = 0.1


class MockReceiver(Thread):
    """The receiver runs in his own thread."""
    def __init__(self, port):
        super(MockReceiver, self).__init__()
        self._stop_event = threading.Event()
        self.port = port
        self.server = None
        self.message_stack = []
        self.paused = False

    def run(self):
        """Start and be a server. Kill self after shutdown."""
        while not self._stop_event.is_set():
            self.start_server(self.port)
            self._stop_event.wait(SLEEP_TIME)
        # clean-up before exit

    def stop(self, timeout):
        """Stop the server and initiate shutting down the thread."""
        print("stopping......")
        self.server.shutdown()
        self.server.server_close()
        self._stop_event.set()
        self.join(timeout)

    def message_handler(self, addr, args):
        """Handle the received OSC messages"""
        # print("message received....",addr, args)
        if addr == "/play":
            self.message_stack.append(("/stop", 0.0))
            self.message_stack.append((addr, 1.0))
        elif addr.find("/track") > -1:
            self.message_stack.append((addr, float(args)))
        elif addr == "/stop":
            self.message_stack.append((addr, 1.0))
            self.message_stack.append(("/play", 0.0))
        elif addr == "/pause":
            if not self.paused:
                self.message_stack.append(("/stop", 1.0))
                self.message_stack.append((addr, 1.0))
                self.message_stack.append(("/play", 0.0))
                self.paused = True
            else:
                self.message_stack.append(("/stop", 0.0))
                self.message_stack.append((addr, 0.0))
                self.message_stack.append(("/play", 1.0))
                self.paused = False
        elif addr == "/action" and args == 40341:  # mute all
            self.message_stack.append(("/track/1/mute", 1.0))
            self.message_stack.append(("/track/2/mute", 1.0))
            self.message_stack.append(("/track/3/mute", 1.0))
            self.message_stack.append(("/track/4/mute", 1.0))
        else:
            self.message_stack.append((addr, args))
        # print("Message stack afterwards.....", self.message_stack)

    def start_server(self, port):
        """Start OSC listener."""
        dispat = dispatcher.Dispatcher()
        dispat.set_default_handler(self.message_handler)
        print("Starting Server")
        try:
            self.server = osc_server.ThreadingOSCUDPServer(('127.0.0.1', port), dispat)
        except Exception as e:
            print(e)
        print(f'Serving on {self.server.server_address}')
        self.server.serve_forever()
