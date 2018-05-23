"""
This module contains all helper classes that are responsible for the exchange of information between the control host,
the opto boards of the piano and the sender/ experiment program.
"""


import socket
import threading
import logging
import zmq
import os
import settings
import ntplib
import serial
import subprocess
import time
import json
import numpy as np
import traceback
import struct
import datetime

def is_msg_valid(msg):
    """
    simple method to check if the received message has a valid structure
    """
    if "sender" in msg and "receiver" in msg and "type" in msg and "message" in msg:
        return True
    else:
        return False


class ExperimentHandler(threading.Thread):
    """
    This class is responsible for information exchange between sender/ experiment and the control host components.
    It receives data from experiment socket, creates an entry in the log and numpy file via the publication sockets and
    pushs if necessary a message to the control host class (e.g. end of experiment).
    """
    def __init__(self,
                 experiment_port = settings.experiment_port,
                 log_publish_port = settings.experiment_publish_log_port,
                 data_publish_port = settings.experiment_publish_data_port,
                 push_port = settings.experiment_push_port,):

        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.experiment_port = experiment_port
        self.log_port = log_publish_port
        self.data_port = data_publish_port
        self.control_send_port = push_port

        self.experiment_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.experiment_socket.bind(("", self.experiment_port))

        self.end = False # kill switch for the run method
        self.lock = threading.RLock()

        context = zmq.Context()
        self.log_socket = context.socket(zmq.PUB)
        self.data_socket = context.socket(zmq.PUB)
        self.control_send_socket = context.socket(zmq.PUSH)
        self.log_socket.bind("tcp://*:"+str(self.log_port))
        self.data_socket.bind("tcp://*:"+str(self.data_port))
        self.control_send_socket.bind("tcp://*:"+str(self.control_send_port))

        self.blockNum=0
        self.blockID=0
        self.DataStream= None
        self.newBlock=False


    def run(self):
        """
        run method of thread class
        """
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


        while True:
            jDat = ""
            try:
                jDat= conn.recv(2048)  # conn.recv(1024) is to small for some information from the sender
                dDat=json.loads(jDat)
                self.create_log_entry("Received message from control socket: " + str(dDat['StreamDat']))
                self.create_log_entry("Received Packet from control socket:" + str(dDat) )
                #oldBlockNum = self.blockNum
                self.blockNum= dDat['BlockNum']
                self.blockID= dDat['BlockID']
                self.DataStream = dDat['StreamDat']

                if "StreamDat" in dDat:
                    data = [dDat["StreamDat"]]  # make a two dimensional array for the numpy data writer
                    self.send_data_msg(data)

                if self.blockID == "SETUP" or self.blockID == "START":
                    conn.send("ready")  # confirm the reception of the message block

                if self.blockID == "END":
                    self.create_log_entry("received end of experiment message")
                    break

                if "FeedbackID" in dDat and dDat['FeedbackID'] == "TIME_SYNC":
                    self.send_control_message("time sync","cmd")

            except ValueError:
                print(traceback.format_exc())
                try:
                    print("jDat: "+str(jDat))
                    conn.send("hello?")  # did we receive invalid data or is the connection broken?
                except:
                    self.create_log_entry("lost connection to the experiment","error")
                    break

            except Exception as e:
                print(traceback.format_exc())
                self.create_log_entry(str(e),"error")

        self.send_control_message(None,"kill")
        #self.shutdown()


    def create_log_entry(self,msg,type="info"):
        """
        method publishs a message in the JSON format via the log socket
        """
        message = {'sender':'experiment', 'receiver':'log', 'message':msg, 'type':type}
        self.log_socket.send_json(message)


    def send_control_message(self,msg, type='info'):
        """
        method sends a message in the JSON format to the control host
        """
        message = {'sender':'experiment', 'receiver':'control host', 'message':msg, 'type':type}
        self.control_send_socket.send_json(message)


    def send_data_msg(self,msg):
        """
        method publishs a message in the JSON format via the data socket
        """
        message = {'sender':'experiment', 'receiver':'npy writer', 'message':msg, 'type':'data'}
        self.data_socket.send_json(message)


    def shutdown(self):
        try:
            self.create_log_entry("Experiment Handler is shutting down")
            time.sleep(0.2)

            with self.lock:
                self.end = True
            self.experiment_socket.close()
            self.control_send_socket.close()
            self.log_socket.close()
        except Exception as e:
            pass


class LogWriter(threading.Thread):
    """
    This class is responsible for the creation of the *.log files.
    It uses a ZMQ based subscription socket and saves the incoming data in the log file.
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

        # create a new log file if the file filename.log already exits
        i=1
        while os.path.exists(logfile):
            logfile = target_dir+"/"+filename+"_"+str(i)+".log"
            i += 1

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
        """
        This method connects the subscription socket to the given list of publishers
        """
        for line in publisher:
            self.create_info_log_entry("LogWriter subscribes to: "+str(line[0])+":"+str(line[1]))
            self.socket.connect("tcp://"+str(line[0])+":"+str(line[1]))
            self.subscribed_ports.append(line[1])
        self.socket.setsockopt(zmq.SUBSCRIBE, '')  # remove the subscription filter


    def run(self):
        self.create_info_log_entry("LogWriter Thread started")
        while True:
            try:
                msg = self.socket.recv_json()
                if is_msg_valid(msg):
                    if msg['receiver'] == "all" or msg['receiver'] == "log":
                        if msg['type'] == "info":
                            self.create_info_log_entry(str(msg['sender']+": "+str(msg['message'])))

                        elif msg['type'] == "error":
                            self.create_error_log_entry(str(msg['sender']+": "+str(msg['message'])))

                        elif msg['type'] == "shutdown":
                            break
                else:
                    self.create_error_log_entry("received invalid message ... I throw it away")

            except Exception as e:
                print(str(e))

        self.end = True
        self.create_info_log_entry("LogWriter is shutting down")
        self.socket.close()
        for hand in list(self.logger.handlers):
            hand.close()


class NumpyDataWriter(threading.Thread):
    """
    This class is responsible for the creation of the *.npy files.
    It uses a ZMQ based subscription socket and stores the incoming data in a text based numpy file.
    """
    def __init__(self, filename, log_port = settings.numpy_writer_publish_port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.subscribed_ports = []  # array of port numbers for reception of data
        self.end = False # kill switch for the run method
        self.log_port = log_port

        #create target directory if neccessary
        target_dir = os.getcwd()+"/"+settings.log_subdirectory
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        npyfile = target_dir+"/"+filename+".npy"

        # modify the file name if a file with the given name already exits
        i=1
        while os.path.exists(npyfile):
            npyfile = target_dir+"/"+filename+"_"+str(i)+".npy"
            i += 1

        os.mknod(npyfile)
        self.file_handle = open(npyfile,'a')


        context = zmq.Context()
        self.data_socket = context.socket(zmq.SUB)
        self.log_socket = context.socket(zmq.PUB)
        self.log_socket.bind("tcp://*:"+str(self.log_port))


    def subscribe(self, publisher):
        """
        This method connects the subscription socket to the given list of publishers
        """
        for line in publisher:
            self.data_socket.connect("tcp://"+str(line[0])+":"+str(line[1]))
            self.subscribed_ports.append(line[1])
        self.data_socket.setsockopt(zmq.SUBSCRIBE, '')


    def run(self):
        self.create_log_entry("NumpyDataWriter is ready")

        while True:
            try:
                message = self.data_socket.recv_json()
                if is_msg_valid(message):
                    if message['receiver'] == "all" or message['receiver'] == "npy writer":
                        if message['type'] == "data":
                            # message['message'] is still a normal two dimensional array
                            np.savetxt(self.file_handle,np.array(message['message']))
                        elif message['type'] == "shutdown":
                            break
                else:
                    self.create_log_entry("received invalid message ... I throw it away")

            except Exception as e:
                self.create_log_entry(str(e),"error")

        #self.create_log_entry("NumpyDataWriter is shutting down")
        self.file_handle.close()


    def create_log_entry(self,msg,type="info"):
        message = {'sender':'numpy data writer', 'receiver':'log', 'message':msg, 'type':type}
        self.log_socket.send_json(message)



class OptoBoardCommunicationThread(threading.Thread):
    """
    This class communicates with the opto boards and is responsible for the data forwarding and configuration of the
    boards.
    """

    class Channel():
        """
        sub class for the physical channels of the board
        """
        def __init__(self,min, max, off_th,on_th,midi):
            self.min = min
            self.max = max
            self.threshold_off_state = off_th
            self.threshold_on_state = on_th
            self.midiID = midi
            self.pressed = False

    def __init__(self,
                 device,
                 log_port=settings.opto_board_log_start_port,
                 data_port=settings.opto_board_data_start_port,
                 control_recv_port=settings.control_host_control_send_port,
                 control_send_port=settings.opto_board_control_send_port,
                 pull_ip=settings.control_host_ip):

        threading.Thread.__init__(self)
        self.log_port = int(log_port)
        self.data_port = int(data_port)
        self.control_recv_port = int(control_recv_port)
        self.device = device

        # zmq stuff
        context = zmq.Context()
        self.log_socket = context.socket(zmq.PUB)  # for messages from the board to the log writer
        self.log_socket.bind("tcp://*:%s" % self.log_port)

        self.data_socket = context.socket(zmq.PUB)   # for messages from the board to the data writer
        self.data_socket.bind("tcp://*:%s" % self.data_port)

        self.control_recv_socket = context.socket(zmq.SUB)  # for messages from the host to the board
        self.control_recv_socket.connect("tcp://"+str(pull_ip)+":"+str(self.control_recv_port))
        self.control_recv_socket.setsockopt(zmq.SUBSCRIBE, '')

        self.control_send_socket = context.socket(zmq.PUSH)   # for messages from the board to the host
        self.control_send_socket.bind("tcp://127.0.0.1:"+str(control_send_port))

        # normal socket for TCP based communication with the board
        self.board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.board_port_active = False

        # serial interface for the configuration stuff
        self.serial_port=serial.Serial(self.device, writeTimeout=1, timeout=settings.serial_timeout)
        if not self.serial_port.isOpen():
            self.serial_port.open()
        self.serial_port.flushOutput()
        self.serial_port.flushInput()

        self.ID = 0
        self.channels ={}
        self.boardIP = ""
        self.ntpIP = ""

        # parameters for the time synchronization
        self.counter3_lastSync = None
        self.ntp_sec_int_lastSync = None
        self.ntp_frac_int_lastSync = None
        self.ntp_sec_float_lastSync = None
        self.clock_offset = None

    def shutdown(self):
        """
        method for a clean shutdown of the communication interfaces
        """
        self.serial_port.flushOutput()
        self.serial_port.flushInput()
        try:
            self.create_log_entry("Communication Thread is shutting down")
        except:
            pass
        if self.serial_port.isOpen():
            self.serial_port.close()
        self.board_socket.close()
        self.data_socket.close()
        self.log_socket.close()
        self.send_and_receive("NSd")
        self.board_port_active = False


    def send_and_receive(self,cmd):
        """
        generic method for the communication with the board via the serial interface.
        This method returns a list of strings with the response of the board.
        """
        cmd += "\r\n"
        try:
            if not self.serial_port.isOpen():
                self.serial_port.open()
            self.serial_port.writelines(cmd)

            time.sleep(0.2)

            line_list = []
            while self.serial_port.inWaiting():
                line_list.append(''.join(self.serial_port.readlines(1)))

            self.serial_port.flushOutput()
            self.serial_port.flushInput()

            return line_list
        except Exception as e:
            print(e)
            return None


    def determine_ID(self):
        """
        method determines the ID of the board
        """
        response = self.send_and_receive("!A")
        for line in response:
            if "Current addr is:" in line:
                id = int(line.split("Current addr is:\t")[1].rstrip())
                self.ID = id
                return id
        raise Exception("could not determine ID of the board")


    def determine_channels(self):
        """
        method determines the channel configurations like thresholds, max, min, ...
        """
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
                    min = int(values[0])
                    max = int(values[1])

                if "Channel "+str(i)+" has low" in line:
                    line = line.replace("Channel "+str(i)+" has low","").rstrip()
                    line = line.replace("thresholds","")
                    values = line.split(" and high ")
                    low = int(values[0])
                    high = int(values[1])

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


    def update_time_sync(self):
        """
        This method is responsible for the time synchronization of the board. It starts a NTP time synchronization and
        stores the offset values for the correct utc time stamp calculations.
        TO DO: The time stamp calculation in the get_data method is not working properly at the moment. I think that the
        cause of this bug is in this function. The old code for this function was really hard to understand.
        """
        try:
            # repeat the NTP time synchronization until the clock offset is 0
            zero_offset = 1
            while zero_offset != 0:
                response = self.send_and_receive("NN")
                for line in response:
                    line = line.rstrip()
                    if "Counter3 last update count: " in line:
                        substring = line.split("Counter3 last update count: ")[1]
                        self.counter3_lastSync=int(substring.split(",")[0])

                    if "Last NTP update secs,fracs:" in line:
                        substring = line.split("Last NTP update secs,fracs: ")[1]
                        substring = substring.split(", Counter3")[0]
                        substring = substring.replace(",",".")
                        self.ntp_sec_int_lastSync = int(float(substring))
                        self.ntp_frac_int_lastSync = int(substring.split(".")[1])
                        self.ntp_sec_float_lastSync = float(substring)


                    if "clock offset (seconds):" in line:
                        substring = line.split("clock offset (seconds):")[1]
                        substring = substring.split("\t and us: ")
                        self.clock_offset = float(substring[0])+(float(substring[1])/1000.0/1000.0)
                        zero_offset = int(float(substring[0]))

            if self.counter3_lastSync is not None and self.ntp_sec_int_lastSync is not None and \
                self.ntp_frac_int_lastSync is not None and self.ntp_sec_float_lastSync is not None \
                and self.clock_offset is not None:
                    return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False


    def update_counter3(self):
        """
        This method updates the value of the variable counter3_lastSync
        """
        try:
            response = self.send_and_receive("?t")
            for line in response:
                line = line.rstrip()
                if "Counter3 last update count: " in line:
                    substring = line.split("Counter3 last update count: ")[1]
                    self.counter3_lastSync=int(substring.split(",")[0])
                    return True
            return False
        except Exception as e:
            print(str(e))
            return False


    def activate_board_port(self):
        """
        This method activates the TCP data port of the board
        """
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
        self.board_socket.connect((self.boardIP, settings.board_tcp_port))
        self.board_socket.send("hello board")

        # seems that the reading loop is necessary to continue the TCP communication
        while self.serial_port.inWaiting():
            self.serial_port.readline()

        self.create_log_entry("Communication Thread connected with board")

        while True:
            # ask for control messages from the host
            try:
                message = self.control_recv_socket.recv_json(flags=zmq.NOBLOCK)
                if is_msg_valid(message):
                    # all -> broadcast message for all slaves
                    # ttyACM* -> multicast message for opto board communication slaves
                    # ttyACM1,2,3, ... unicast message
                    if message['receiver'] == "all" or message['receiver'] == "ttyACM*" or message['receiver'] == str(self.device):
                        if message['type'] == "shutdown":
                            break
                        elif message['type'] == "cmd":
                            self.execute_command(message['message'])
                else:
                    self.create_log_entry("received invalid message ... I throw it away")
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    pass
                else:
                    self.create_log_entry(str(e),"error")

            # get and publish the channel values
            data = self.get_data()
            if data is not None:
                self.create_data_entry(data)
                self.check_thresholds(data)
        self.shutdown()


    def check_thresholds(self,data):
        """
        This method compares the received and transformed channel data with the threshold values to detect key pressed/
        key released events. I had some toggle problems with channel 1 and 3 of board 7 sometimes. So, I excluded
        channel 3 (MIDI 0). I also implemented a counter and defined a threshold to avoid these toggle messages for
        short peaks.
        """
        on_counter = []
        off_counter = []
        for i in range(0,len(data[0])-3):
            on_counter.append(0)
            off_counter.append(0)

        for j in range(0,len(data)):
            for i in range(0,len(self.channels)):
                if self.channels[i].midiID != 0:
                    # Channel 1 of Board 7 (midiID 83 toggles sometimes)
                    if self.channels[i].midiID == 83:
                        if data[j][i+1] > self.channels[i].threshold_on_state + 42:
                            on_counter[i] += 1
                            if on_counter[i] > settings.probe_counter + 7 and not self.channels[i].pressed:
                                on_counter[i] = 0
                                self.channels[i].pressed = True
                                self.create_log_entry("Channel "+str(i)+" with MIDI ID "+str(self.channels[i].midiID)+" is now ON")
                                # structure: 255 - boardID, channel, value, velocity, 1=key pressed/ 0= key released, timestamp1, timestamp2
                                entry = [255 - data[j][0], i, data[j][i+1], 0, 1, data[j-4][5], data[j-4][6]]
                                self.create_log_entry(str(entry))
                                self.create_data_entry([entry])
                        else:
                            on_counter[i] = 0

                    else:
                        if data[j][i+1] > self.channels[i].threshold_on_state:
                            on_counter[i] += 1
                            if on_counter[i] > settings.probe_counter and not self.channels[i].pressed:
                                on_counter[i] = 0
                                self.channels[i].pressed = True
                                self.create_log_entry("Channel "+str(i)+" with MIDI ID "+str(self.channels[i].midiID)+" is now ON")
                                # structure: 255 - boardID, channel, value, velocity, 1=key pressed/ 0= key released, timestamp1, timestamp2
                                entry = [255 - data[j][0], i, data[j][i+1], 0, 1, data[j][5], data[j][6]]
                                self.create_log_entry(str(entry))
                                self.create_data_entry([entry])
                        else:
                            on_counter[i] = 0

                    if data[j][i+1] <= self.channels[i].threshold_off_state:
                        off_counter[i] += 1
                        if off_counter[i] > settings.probe_counter and self.channels[i].pressed:
                            off_counter[i] = 0
                            self.channels[i].pressed = False
                            self.create_log_entry("Channel "+str(i)+" with MIDI ID "+str(self.channels[i].midiID)+" is now OFF")
                            # structure: 255 - boardID, channel, value, velocity, 1=key pressed/ 0= key released, timestamp1, timestamp2
                            entry = [255 - data[j][0], i, data[j][i+1], 0, 0, data[j][5], data[j][6]]
                            self.create_log_entry(str(entry))
                            self.create_data_entry([entry])
                    else:
                        off_counter[i] = 0


    def create_log_entry(self,msg,type="info"):
        message = {'sender':'Board '+str(self.ID), 'receiver':'log', 'message':msg, 'type':type}
        self.log_socket.send_json(message)


    def execute_command(self, cmd):
        self.create_log_entry("execute cmd: "+str(cmd))


    def get_data(self):
        """
        This method receives a certain amount of bytes from the board and tries to convert them into an array of integers.
        If the block size is not a multiple of 20 it is not possible to convert these bytes because each 'data block' of
        the board consists of five 4 byte integer values (C0, C1, C2, C3, board time stamp)
        TO DO: The correct calculation of the utc time stamps is not working at moment!!!! I think the reading of some
        timer offset values in the method update_time_sync is not correct.
        """
        raw = self.board_socket.recv(6000)

        if len(raw) % 20 != 0:
            self.create_log_entry("received block size of "+str(len(raw))+" mod 20 != 0. Skip block",type="error")
            return None

        data = []
        for i in range(0,len(raw)/20):
            row = [self.ID]
            # structure; C0 C1 C2 C3 BoardTime
            values = list(struct.unpack('iiiiI',raw[i*20:(i+1)*20]))

            row = row + values
            # some wired time conversion / synchronisation
            # something is wrong here
            board_time = row[-1]
            utc_time = (float(board_time) - float(self.counter3_lastSync))/100000 + self.ntp_sec_float_lastSync
            utc_time += self.clock_offset
            utc_time -= float(2208988800)
            #print(datetime.datetime.fromtimestamp(utc_time).strftime('%Y-%m-%d %H:%M:%S'))
            row.append(utc_time)
            data.append(row)

        return data


    def create_data_entry(self,data):
        message = {'sender':'Board '+str(self.device), 'receiver':'npy writer', 'message':data, 'type':'data'}
        self.data_socket.send_json(message)


class NTPClient(object):
    """
    simple ntp client
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
            return (ntp_time.tx_timestamp-float(2208988800))
        else:
            return None
