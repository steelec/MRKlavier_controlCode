#!/usr/bin/python

import argparse
import glob
import time
import slaves
import traceback
import atexit
import socket

control_host = None
board_interface_pattern = "/dev/ttyACM*"
experiment_port = 4999


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
        self.broker = slaves.Broker()
        self.logger.create_info_log_entry("Broker created successfully")
        self.ntp_client = slaves.NTPClient(ntp_server)
        self.logger.create_info_log_entry("NTP Client created successfully")
        self.obct = {}  # obct = OptoBoardCommunicationThread

        self.experiment_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.experiment_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.status = "ready"


    def find_boards(self,pattern):
        """
        method tries to find some serial interfaces with given pattern
        :return: number of successfully created OptoBoardCommunicationThreads (equals the number of matches)
        """
        self.logger.create_info_log_entry("try to find some boards with the pattern: "+str(pattern))

        matches=glob.glob(pattern)
        if len(matches) < 1:
            self.logger.create_error_log_entry("could not find any boards -> ABORT!")
            return 0
        self.logger.create_info_log_entry("Boards found at: "+str(matches))
        port = slaves.opto_board_start_port
        for interface in matches:
            self.obct[interface] = slaves.OptoBoardCommunicationThread(port,interface)
            port += 1

        return len(self.obct)

    def configure_boards(self):
        return True

    def start_experiment(self):
        self.status = "busy"
        while True:
            time.sleep(1)


    def shutdown(self):
        self.logger.create_info_log_entry("control host is shutting down")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='control and logging application for the MR Piano')
    parser.add_argument('--ntp', action="store", dest="server_ip", type=str, help="IP address of the NTP server",
                        default="127.0.0.1")
    parser.add_argument('--name', action="store", dest="name", type=str, help="name of the expirement",
                        default="experiment1")
    parameters = parser.parse_args()

    print "[+] start control host for MR Piano"
    global control_host, board_interface_pattern
    try:
        # try to create the control host
        control_host = ControlHost(parameters.server_ip, parameters.name)
        atexit.register(control_host.shutdown)

    except Exception as e:
        print(traceback.format_exc())
        control_host.logger.create_error_log_entry("failed to initialize control host -> ABORT!")
        exit(-1)

    # try to find some boards
    if control_host.find_boards(board_interface_pattern) < 1 and not control_host.configure_boards():
        exit(-1)

    control_host.start_experiment()

