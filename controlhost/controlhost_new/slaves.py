import threading
import logging

class Broker(threading.Thread):
    """
    class for the message forwarding and processing from the OptoBoardCommunicationThreads to the
    subscribed WriterThreads
    """
    def __init__(self):
         threading.Thread.__init__(self)

    def run(self):
        pass


class ExperimentHandler(threading.Thread):
    """
    class for the information exchange with sender / experiment script
    """
    def __init__(self):
         threading.Thread.__init__(self)

    def run(self):
        pass

class LogWriter(threading.Thread):
    """
    This class is responsible for the creation of the *.log files
    It uses ZMQ based subscribe socket writes the incoming data in a log file
    """
    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger('PianoLogger')
        self.logger.setLevel(logging.DEBUG)
        
    def run(self):
        pass


class NumpyDataWriter(threading.Thread):
    """
    This class is responsible for the creation of the *.npy files
    It uses ZMQ based subscribe socket writes the incoming data in npy file
    """
    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.filename = filename

    def run(self):
        pass

class OptoBoardCommunicationThread(threading.Thread):
    """
    This class communicates with the OptoBoards and sends the data from the boards to broker via ZMQ for further
    information processing
    """
    def __init__(self, port, device):
        threading.Thread.__init__(self)
        self.port = int(port)
        self.device = device

    def run(self):
        pass