#!/usr/bin/python

import argparse
import slaves


control_host = None
board_interface_pattern = "/dev/ttyACM*"


class ControlHost(object):
    """
    main class of the application
    """
    def __init__(self, ntp_server, experiment):
        self.ntp_server = ntp_server
        print "[+] create and start logging slaves"
        self.logger = slaves.LogWriter(experiment)
        self.logger.start()
        self.npy_writer = slaves.NumpyDataWriter(experiment)
        self.obct = {}  # obct = OptoBoardCommunicationThread





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='control and logging application for the MR Piano')
    parser.add_argument('--ntp', action="store", dest="server_ip", type=str, help="IP address of the NTP server",
                        default="127.0.0.1")
    parser.add_argument('--name', action="store", dest="name", type=str, help="name of the expirement",
                        default="experiment1")
    parameters = parser.parse_args()


    print "[+] start control host for MR Piano"
    control_host = ControlHost(parameters.server_ip, parameters.name)
