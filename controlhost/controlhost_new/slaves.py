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
import json
import numpy as np

def is_msg_valid(msg):
    if "sender" in msg and "receiver" in msg and "type" in msg and "message" in msg:
        return True
    else:
        return False


class ExperimentHandler(threading.Thread):
    def __init__(self,
                 experiment_port = settings.experiment_port,
                 log_publish_port = settings.experiment_publish_log_port,
                 data_publish_port = settings.experiment_publish_data_port,
                 push_port = settings.experiment_push_port):

        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.experiment_port = experiment_port
        self.log_publish_port = log_publish_port
        self.data_publish_port = data_publish_port
        self.push_port = push_port

        self.experiment_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.experiment_socket.bind(("", self.experiment_port))

        self.end = False # kill switch for the run method
        self.lock = threading.RLock()

        context = zmq.Context()
        self.log_socket = context.socket(zmq.PUB)
        self.data_socket = context.socket(zmq.PUB)
        self.push_socket = context.socket(zmq.PUSH)
        self.log_socket.bind("tcp://*:"+str(self.log_publish_port))
        self.data_socket.bind("tcp://*:"+str(self.data_publish_port))
        self.push_socket.bind("tcp://*:"+str(self.push_port))

        self.blockNum=0
        self.blockID=0
        self.DataStream= None
        self.newBlock=False


    def run(self):
        time.sleep(1)
        self.experiment_socket.listen(1)
        self.create_log_entry("Experiment Handler is ready and waiting for the experiment")
        conn, addr = self.experiment_socket.accept()
        self.create_log_entry("Connection received from: " + str(addr))

        MESSAGE = "Peanut is so ready to start initialization!"
        print("Sending TCP message: " + MESSAGE+ " to IP: " + str(addr) + " on port " + str(self.experiment_port))
        conn.send(MESSAGE)

        recvMsg = conn.recv(1024) # <- "Ready Peanut!"
        print("Received message from control socket: " + recvMsg)


        while not self.end:
            try:
                jDat= conn.recv(1024)
                dDat=json.loads(jDat)
                self.create_log_entry("Received message from control socket: " + str(dDat['StreamDat']))
                self.create_log_entry("Received Packet from control socket:" + str(dDat) )
                #oldBlockNum = self.blockNum
                self.blockNum= dDat['BlockNum']
                self.blockID= dDat['BlockID']
                self.DataStream = dDat['StreamDat']

                if "StreamDat" in dDat:
                    data = np.array(dDat["StreamDat"])
                    self.send_data_msg(data.tolist())

                if self.blockID == "SETUP":
                    conn.send("hello experiment") #confirm the reception of the message block

                if self.blockID == "END":
                    self.create_log_entry("received end of experiment message")
                    self.send_push_message("kill")
                    break



            except Exception as e:
                self.create_log_entry(str(e),"error")


    def create_log_entry(self,msg,type="info"):
        message = {'sender':'experiment', 'receiver':'log', 'message':msg, 'type':type}
        self.log_socket.send_json(message)


    def send_push_message(self,msg, type='info'):
        message = {'sender':'experiment', 'receiver':'control host', 'message':msg, 'type':type}
        self.push_socket.send_json(message)

    def send_data_msg(self,msg):
        message = {'sender':'experiment', 'receiver':'control host', 'message':msg, 'type':'data'}
        self.data_socket.send_json(message)

    def shutdown(self):
        try:
            self.create_log_entry("Experiment Handler is shutting down")
            time.sleep(0.2)

            with self.lock:
                self.end = True
            self.experiment_socket.close()
            self.push_socket.close()
            self.log_socket.close()
        except Exception as e:
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
        self.setDaemon(True)
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

        self.end = False # kill switch for the run method

        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.subscribed_ports = [] # array of port numbers for reception of data

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

    def subscribe(self, publisher):
        for line in publisher:
            self.create_info_log_entry("LogWriter subscribes to: "+str(line[0])+":"+str(line[1]))
            self.socket.connect("tcp://"+str(line[0])+":"+str(line[1]))
            self.subscribed_ports.append(line[1])
        self.socket.setsockopt(zmq.SUBSCRIBE, '')


    def run(self):
        #self.socket.setsockopt(zmq.SUBSCRIBE, "12")
        self.create_info_log_entry("LogWriter Thread started")
        while not self.end:
            try:
                msg = self.socket.recv_json()
                if is_msg_valid(msg):
                    if msg['type'] == "info":
                        self.create_info_log_entry(str(msg['sender']+": "+str(msg['message'])))
                    elif msg['type'] == "error":
                        self.create_error_log_entry(str(msg['sender']+": "+str(msg['message'])))
                else:
                    self.create_error_log_entry("received invalid message ... I throw it away")

            except Exception as e:
                print(str(e))


    def shutdown(self):
        with self.lock:
            self.end = True

        self.create_info_log_entry("LogWriter is shutting down")
        self.socket.close()

        for hand in list(self.logger.handlers):
            hand.close()


class NumpyDataWriter(threading.Thread):
    """
    This class is responsible for the creation of the *.npy files
    It uses ZMQ based subscribe socket writes the incoming data in npy file
    """
    def __init__(self, filename, publish_port = settings.numpy_writer_publish_port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.filename = filename
        self.subscribed_ports = []  # array of port numbers for reception of data
        self.end = False # kill switch for the run method
        self.publish_port = publish_port

        #create target directory if neccessary
        target_dir = os.getcwd()+"/"+settings.log_subdirectory
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        context = zmq.Context()
        self.data_socket = context.socket(zmq.SUB)
        self.log_socket = context.socket(zmq.PUB)
        self.log_socket.bind("tcp://*:"+str(self.publish_port))


    def subscribe(self, publisher):
        for line in publisher:
            self.data_socket.connect("tcp://"+str(line[0])+":"+str(line[1]))
            self.subscribed_ports.append(line[1])
        self.data_socket.setsockopt(zmq.SUBSCRIBE, '')

    def run(self):
        self.create_log_entry("NumpyDataWriter is ready")

        while not self.end:
            try:
                message = self.data_socket.recv_json()
                if is_msg_valid(message):
                    print("got numpy data")
                    print(message)
                else:
                    self.create_log_entry("received invalid message ... I throw it away")

            except Exception as e:
                self.create_log_entry(str(e),"error")

    def create_log_entry(self,msg,type="info"):
        message = {'sender':'numpy data writer', 'receiver':'log', 'message':msg, 'type':type}
        self.log_socket.send_json(message)

    def shutdown(self):
        self.end = True



class OptoBoardCommunicationThread(threading.Thread):
    """
    This class communicates with the OptoBoards and sends the data from the boards to broker via ZMQ for further
    information processing
    """

    class Channel():
        """
        sub class for the physical channels of the board
        """
        def __init__(self,min, max, low,high,midi):
            self.min = min
            self.max = max
            self.low_threshold = low
            self.high_threshold = high
            self.midiID = midi


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
        self.pull_socket = context.socket(zmq.PULL)  # for messages from the host to the board
        self.push_socket = context.socket(zmq.PUSH)   # for messages from the board to the host
        self.push_socket.bind("tcp://127.0.0.1:"+str(push_port))


        # normal socket for TCP based communication with the board
        self.board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.board_port_active = False

        # serial interface for the configuration stuff
        self.serial_port=serial.Serial(self.device, writeTimeout=1, timeout=settings.serial_timeout)
        if not self.serial_port.isOpen():
            self.serial_port.open()

        self.ID = 0
        self.channels ={}
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

    def determine_channels(self):
        channels = {}

        midiID = []
        for i in range(0,4):
            response = self.send_and_receive("Sa"+ str(i))
            for line in response:
                if "Channel "+str(i)+" has name" in line:
                    midiID.append(int(line.split("Channel "+str(i)+" has name")[1]))

        response = self.send_and_receive("kC")
        for i in range(0,4):
            min = 0
            max = 0
            low = 0
            high = 0
            for line in response:
                if "Channel "+str(i)+" has min" in line:
                    line = line.replace("Channel "+str(i)+" has min","").rstrip()
                    values = line.split(" and max ")
                    min = values[0]
                    max = values[1]

                if "Channel "+str(i)+" has low" in line:
                    line = line.replace("Channel "+str(i)+" has low","").rstrip()
                    line = line.replace("thresholds","")
                    values = line.split(" and high ")
                    low = values[0]
                    high = values[1]

            channels[i] = OptoBoardCommunicationThread.Channel(min,max,low,high,midiID[i])

        self.channels = channels
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

    def update_ntp_time(self):
        response = self.send_and_receive("NN")
        for line in response:
            if "Calling ntp get time, returned 1" in line:
                return True
        return False

    def get_ntp_time(self):
        return self.send_and_receive("?t")

    def activate_board_port(self):
        self.serial_port.flushInput()

        self.serial_port.writelines("NSt\r\n")
        i=0
        while i < 100:
            line = ''.join(self.serial_port.readlines(1))
            if "opened for TCP streaming" in line:
                self.board_port_active = True
                return True
            i += 1

        return False


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