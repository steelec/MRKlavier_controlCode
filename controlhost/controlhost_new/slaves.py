import socket
import threading
import logging
import zmq
import os
import datetime

#some constants and value definitions
log_subdirectory = "data"
broker_subscriber_port = 5000
broker_publisher_port = 5001
log_writer_port = 5002
numpy_writer_port = 5003
opto_board_start_port = 5004

# 'global' variables for external access
logger = None
broker = None
experiment_handler = None
numpy_writer = None
opto_board_communication_thread = {}


class Broker(threading.Thread):
    """
    class for the message forwarding and processing from the OptoBoardCommunicationThreads to the
    subscribed WriterThreads
    """
    def __init__(self):
        threading.Thread.__init__(self)
        context = zmq.Context()
        self.subscriber_socket = context.socket(zmq.SUB)
        self.publisher_socket = context.socket(zmq.PUB)

    def run(self):
        pass


class LogWriter(threading.Thread):
    """
    This class is responsible for the creation of the *.log files
    It uses ZMQ based subscribe socket writes the incoming data in a log file
    """

    class Formatter(logging.Formatter):
        """
        sub class of logging.Formater for the individual log format
        """
        converter=datetime.datetime.fromtimestamp
        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            if datefmt:
                s = ct.strftime(datefmt)
            else:
                t = ct.strftime("%Y-%m-%d %H:%M:%S")
                s = "%s,%03d" % (t, record.msecs)
            return s


    def __init__(self, filename):
        threading.Thread.__init__(self)

        #create log directory and file if neccessary
        target_dir = os.getcwd()+"/"+log_subdirectory
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        logfile = target_dir+"/"+filename+".log"

        self.logger = logging.getLogger('LogWriter')
        self.logger.setLevel(logging.DEBUG)
        self.fh=logging.FileHandler(logfile)
        self.fh.setLevel(logging.DEBUG)
        self.sh=logging.StreamHandler()
        self.sh.setLevel(logging.DEBUG)
        self.formatter = LogWriter.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d,%H:%M:%S.%f')
        self.formatter.datefmt='%Y-%m-%d,%H:%M:%S--%s.%f'
        self.fh.setFormatter(self.formatter)
        self.sh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.sh)
        self.logger.propagate = False

        #create the zmq socket, we bind it later
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)

        self.lock = threading.RLock()
        global logger
        logger = self


    def create_info_log_entry(self,msg,sender="LogWriter"):
        """
        method provides the possibility to create an info log entry
        """
        with self.lock:
            self.logger.info(msg)

    def create_error_log_entry(self,msg,sender="LogWriter"):
        """
        method provides the possibility to create an error log entry
        """
        with self.lock:
            self.logger.error(msg)

        
    def run(self):
        pass


class NumpyDataWriter(threading.Thread):
    """
    This class is responsible for the creation of the *.npy files
    It uses ZMQ based subscribe socket writes the incoming data in npy file
    """
    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.basefilename = filename
        self.block_counter = 0

        #create target directory if neccessary
        target_dir = os.getcwd()+"/"+log_subdirectory
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        #create the zmq socket, we bind it later
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)

        self.lock = threading.RLock()

        global numpy_writer
        numpy_writer = self

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

        global opto_board_communication_thread
        opto_board_communication_thread[device] = self

    def run(self):
        pass


class NTPClient(object):
    """
    simple ntp client for the time synchronisation of the boards
    """
    def __init__(self,ip):
        self.server_ip = ip
