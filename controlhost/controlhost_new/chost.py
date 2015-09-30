#!/usr/bin/python

import argparse
import glob
import time
import slaves
import traceback
import atexit
import socket
import settings
import zmq

class ControlHost(object):
    """
    main class of the application
    """
    def __init__(self, ntp_server, experiment):
        self.ntp_server = ntp_server

        print "[+] create slaves"
        self.logger = slaves.LogWriter(experiment)
        self.logger.create_info_log_entry("LogWriter created successfully")
        self.npy_writer = slaves.NumpyDataWriter(experiment)
        self.logger.create_info_log_entry("NumpyDataWriter created successfully")
        self.ntp_client = slaves.NTPClient(ntp_server)
        self.logger.create_info_log_entry("NTP Client created successfully")
        self.obct = {}  # obct = OptoBoardCommunicationThread

        self.experiment_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.experiment_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        context = zmq.Context()

        self.control_socket = context.socket(zmq.PUSH)  # for messages from the host to the boards
        self.control_socket.bind("tcp://127.0.0.1:"+str(settings.control_host_push_port))

        self.pull_socket = context.socket(zmq.PULL)  # for messages from the boards to the host

        self.publish_socket = context.socket(zmq.PUB)  # for logging messages from the host to the log writer
        self.publish_socket.bind("tcp://127.0.0.1:"+str(settings.control_host_publish_port))

        self.status = "ready"


    def find_boards(self,pattern):
        """
        method tries to find some serial interfaces with given pattern
        :return: number of successfully created OptoBoardCommunicationThreads (equals the number of matches)
        """
        self.logger.create_info_log_entry("try to find some boards with the pattern: "+str(pattern))

        matches = glob.glob(pattern)
        if len(matches) < 1:
            self.logger.create_error_log_entry("could not find any boards -> ABORT!")
            return 0

        self.logger.create_info_log_entry("Boards found at: "+str(matches))
        log_port = settings.opto_board_log_start_port
        data_port = settings.opto_board_data_start_port
        interface = ""
        try:
            for interface in matches:
                self.obct[interface] = slaves.OptoBoardCommunicationThread(interface,
                                                                           log_port=log_port, data_port=data_port)
                log_port += 1
                data_port += 1
        except Exception as e:
            print(str(e))
            self.logger.create_error_log_entry("failed to create OptoBoardCommunicationThread for interface "+interface
                                               + ": " + str(e))
            return 0

        return len(self.obct)


    def configure_boards(self):
        self.logger.create_info_log_entry("start board configuration")
        for interface in self.obct:
            try:
                board = self.obct[interface]

                board.determine_ID()
                self.logger.create_info_log_entry("board "+interface+" has ID "+str(board.ID))

                board.determine_midi_channels()
                self.logger.create_info_log_entry("channels of board "+interface+": "+str(board.midi_channels))

                board.determine_ip_address()
                self.logger.create_info_log_entry("IP of board "+interface+": "+board.boardIP)

                if not board.set_ntp_server(self.ntp_server):
                    raise Exception("could not set IP for NTP server")
                self.logger.create_info_log_entry("NTP server for board "+interface+": "+board.ntpIP)

                if not board.activate_network():
                    raise Exception("could activate the network interface")
                self.logger.create_info_log_entry("network interface of board "+interface+" is ready")


            except Exception as e:
                print(traceback.format_exc())
                self.logger.create_error_log_entry("failed to configure board "+interface+": "+str(e))
                return False
        return True


    def start_experiment(self):
        self.status = "busy"
        self.logger.create_info_log_entry("start experiment environment")
        while True:
            time.sleep(1)


    def shutdown(self):
        self.logger.create_info_log_entry("control host is shutting down")
        for interface in self.obct:
            board = self.obct[interface]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='control and logging application for the MR Piano')
    parser.add_argument('--ntp', action="store", dest="server_ip", type=str, help="IP address of the NTP server",
                        default="127.0.0.1")
    parser.add_argument('--name', action="store", dest="name", type=str, help="name of the expirement",
                        default="experiment1")
    parameters = parser.parse_args()

    print "[+] start control host for MR Piano"
    control_host = None

    try:
        # try to create the control host
        control_host = ControlHost(parameters.server_ip, parameters.name)
        atexit.register(control_host.shutdown)

    except Exception as e:
        print(traceback.format_exc())
        control_host.logger.create_error_log_entry("failed to initialize control host -> ABORT!")
        exit(-1)

    # try to find some boards

    if control_host.find_boards(settings.board_interface_pattern) < 1 or not control_host.configure_boards():
        exit(-1)

    #control_host.start_experiment()

