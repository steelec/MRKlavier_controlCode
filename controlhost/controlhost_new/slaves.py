import socket
import threading
import logging
import zmq
import os
import datetime
import settings
import ntplib
import serial
import subprocess
import time

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
        target_dir = os.getcwd()+"/"+settings.log_subdirectory
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        logfile = target_dir+"/"+filename+".log"

        self.logger = logging.getLogger('LogWriter')
        self.logger.setLevel(logging.DEBUG)
        self.fh=logging.FileHandler(logfile)
        self.fh.setLevel(logging.DEBUG)
        self.sh=logging.StreamHandler()
        self.sh.setLevel(logging.DEBUG)
        self.formatter = LogWriter.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                             datefmt='%Y-%m-%d,%H:%M:%S.%f')
        self.formatter.datefmt='%Y-%m-%d,%H:%M:%S--%s.%f'
        self.fh.setFormatter(self.formatter)
        self.sh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.sh)
        self.logger.propagate = False

        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.publisher_ports = [] # array of port numbers for reception of data

        self.lock = threading.RLock()


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
        self.filename = filename
        self.publisher_ports = []  # array of port numbers for reception of data

        #create target directory if neccessary
        target_dir = os.getcwd()+"/"+settings.log_subdirectory
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)


        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)


    def run(self):
        pass


class OptoBoardCommunicationThread(threading.Thread):
    """
    This class communicates with the OptoBoards and sends the data from the boards to broker via ZMQ for further
    information processing
    """
    def __init__(self,
                 device,
                 log_port=settings.opto_board_log_start_port,
                 data_port=settings.opto_board_data_start_port,
                 control_port=settings.control_host_push_port,
                 push_port=settings.opto_board_push_port):

        threading.Thread.__init__(self)
        self.log_port = int(log_port)
        self.data_port = int(data_port)
        self.control_port = int(control_port)
        self.device = device

        # zmq stuff
        context = zmq.Context()
        self.log_socket = context.socket(zmq.PUB)  # for messages from the board to the log writer
        self.log_socket.bind("tcp://*:%s" % self.log_port)
        self.data_socket = context.socket(zmq.PUB)   # for messages from the board to the data writer
        self.data_socket.bind("tcp://*:%s" % self.data_port)
        self.control_socket = context.socket(zmq.PULL)  # for messages from the host to the board
        self.push_socket = context.socket(zmq.PUSH)   # for messages from the board to the host
        self.push_socket.bind("tcp://127.0.0.1:"+str(push_port))


        # normal socket for TCP based communication with the board
        self.board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # serial interface for the configuration stuff
        self.serial_port=serial.Serial(self.device, writeTimeout=1, timeout=settings.serial_timeout)
        if not self.serial_port.isOpen():
            self.serial_port.open()

        self.ID = 0
        self.midi_channels = {}
        self.boardIP = ""
        self.ntpIP = ""


    def shutdown(self):
        if self.serial_port.isOpen():
            self.serial_port.close()


    def send_and_receive(self,cmd):
        cmd += "\r\n"
        try:
            if not self.serial_port.isOpen():
                self.serial_port.open()
            self.serial_port.writelines(cmd)

            line_list = []
            while self.serial_port.inWaiting():
                line_list.append(''.join(self.serial_port.readlines(1)))

            return line_list


        except Exception as e:
            print(e)
            return None

    def determine_ID(self):
        response = self.send_and_receive("!A")
        for line in response:
            if "Current addr is:" in line:
                id = int(line.split("Current addr is:\t")[1].rstrip())
                self.ID = id
                return id
        raise Exception("could not determine ID of the board")

    def determine_midi_channels(self):
        channels = {}
        for i in range(0,4):
            response = self.send_and_receive("Sa"+ str(i))
            for line in response:
                if "Channel "+str(i)+" has name" in line:
                    channels[i] = int(line.split("Channel "+str(i)+" has name")[1])

        self.midi_channels = channels
        return channels


    def test_leds(self):
        for i in range(0,8):
            self.send_and_receive("Sl"+str(i)+",0")
        time.sleep(0.5)
        for i in range(0,8):
            self.send_and_receive("Sl"+str(i)+",1")
            time.sleep(0.5)
        time.sleep(2)
        for i in range(0,8):
            self.send_and_receive("Sl"+str(i)+",0")

    def determine_ip_address(self):
        response = self.send_and_receive("Ni")
        for line in response:
            if "IP stored: " in line:
                ip = line.split("IP stored: ")[1].rstrip()
                self.boardIP = ip
                return ip
            elif "IP :" in line:
                ip = line.split("IP :")[1].rstrip()
                self.boardIP = ip
                return ip

        raise Exception("could not find ip address")

    def set_ntp_server(self,ip):
        self.ntpIP = ip
        resp = self.send_and_receive("Nn "+ip)
        for line in resp:
            if "NTP address is: " in line:
                rx_ip = line.split("NTP address is: ")[1].rstrip()
                if ip in rx_ip:
                    return True
                else:
                    return False
        return False

    def activate_network(self):
        self.send_and_receive("NE")
        time.sleep(0.5)
        es = subprocess.call("ping -c 1 %s" % self.boardIP, shell=True, stdout=open('/dev/null', 'w'),
                             stderr=subprocess.STDOUT)
        if es < 1:
            return True



    def run(self):
        pass


class NTPClient(object):
    """
    simple ntp client for the time synchronisation of the boards
    """
    def __init__(self,ip):
        self.server_ip = ip
        self.ntpc = ntplib.NTPClient()

    def get_NTP_time(self):
        try:
            return self.ntpc.request(self.server_ip)
        except Exception as e:
            print(str(e))
            return None

    def get_UTC_time(self):
        ntp_time = self.get_NTP_time()
        if ntp_time is not None:
            return (response.tx_timestamp-float(2208988800))
        else:
            return None