#!/usr/bin/python

import argparse
import glob
import time
import slaves
import traceback
import atexit
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
        self.experiment_handler = slaves.ExperimentHandler()
        self.logger.create_info_log_entry("ExperimentHandler created successfully")
        self.npy_writer = slaves.NumpyDataWriter(experiment)
        self.logger.create_info_log_entry("NumpyDataWriter created successfully")
        self.ntp_client = slaves.NTPClient(ntp_server)
        self.logger.create_info_log_entry("NTP Client created successfully")
        self.obct = {}  # obct = OptoBoardCommunicationThread

        context = zmq.Context()

        self.control_receive_socket = context.socket(zmq.PULL)  # for messages from the boards to the host

        self.control_send_socket = context.socket(zmq.PUB)  # for logging messages from the host to the log writer
        self.control_send_socket.bind("tcp://127.0.0.1:"+str(settings.control_host_control_send_port))

        self.status = "ready"


    def find_boards(self,pattern):
        """
        method tries to find some serial interfaces with given pattern and creates for each match an instance of the
        OptoBoardCommunication class.
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
        push_port = settings.opto_board_control_send_port
        interface = ""
        try:
            for interface in matches:
                self.obct[interface] = slaves.OptoBoardCommunicationThread(interface, log_port=log_port,
                                                                           data_port=data_port,
                                                                           control_send_port=push_port)
                log_port += 1
                push_port += 1
                data_port += 1
        except Exception as e:
            print(traceback.format_exc())
            self.logger.create_error_log_entry("failed to create OptoBoardCommunicationThread for interface "+interface
                                               + ": " + str(e))
            return 0

        return len(self.obct)


    def configure_boards(self):
        """
        This method is responsible for the whole configuration and reading process of the board parameters.
        """
        self.logger.create_info_log_entry("start board configuration")
        for interface in self.obct:
            try:
                board = self.obct[interface]

                board.determine_ID()
                self.logger.create_info_log_entry("board "+interface+" has ID "+str(board.ID))

                board.determine_channels()
                self.logger.create_info_log_entry("channels of board "+interface+": ")
                for c in board.channels:
                    self.logger.create_info_log_entry("channel "+str(c)+" has name "+str(board.channels[c].midiID))
                    self.logger.create_info_log_entry("channel "+str(c)+" has min value "+str(board.channels[c].min))
                    self.logger.create_info_log_entry("channel "+str(c)+" has max value "+str(board.channels[c].max))
                    self.logger.create_info_log_entry("channel "+str(c)+" has low threshold "+
                                                      str(board.channels[c].threshold_off_state))
                    self.logger.create_info_log_entry("channel "+str(c)+" has high threshold "+
                                                      str(board.channels[c].threshold_on_state))

                board.determine_ip_address()
                self.logger.create_info_log_entry("IP of board "+interface+": "+board.boardIP)

                if not board.set_ntp_server(self.ntp_server):
                    raise Exception("could not set IP for NTP server")
                self.logger.create_info_log_entry("NTP server for board "+interface+": "+board.ntpIP)


                if not board.activate_network():
                    raise Exception("could activate the network interface")
                self.logger.create_info_log_entry("network interface of board "+interface+" is ready")

                time.sleep(0.5)

                i=0
                while not(board.update_time_sync() and board.update_counter3()):
                    i += 1
                    self.logger.create_info_log_entry("failed to update time settings for board "+str(interface)+".Try again.")
                    if i == 3:
                        raise Exception("could not update time settings")
                    time.sleep(0.2)

                self.logger.create_info_log_entry("time settings for board "+str(interface)+":")
                self.logger.create_info_log_entry("Counter 3 last Sync: "+str(board.counter3_lastSync))
                self.logger.create_info_log_entry("NTP sec int last Sync: "+str(board.ntp_sec_int_lastSync))
                self.logger.create_info_log_entry("NTP sec frac last Sync: "+str(board.ntp_frac_int_lastSync))
                self.logger.create_info_log_entry("NTP sec float last Sync: "+str(board.ntp_sec_float_lastSync))
                self.logger.create_info_log_entry("clock offset: "+str(board.clock_offset))

                if not board.activate_board_port():
                    raise Exception("could not activate TCP port")
                self.logger.create_info_log_entry("TCP port of the board "+interface+" is ready")
                time.sleep(0.5)
                self.logger.create_info_log_entry("Initialization done on "+interface+", ready to collect data!")

            except Exception as e:
                print(traceback.format_exc())
                self.logger.create_error_log_entry("failed to configure board "+interface+": "+str(e))
                return False
        return True


    def create_slave_subscriptions(self):
        """
        This method organizes and creates the subscriptions of the LogWriter, the NumpyWriter ... .
        """

        # create subscriptions for LogWriter
        log_publisher = []
        for i in range(0,len(self.obct)):
            log_publisher.append(["127.0.0.1", settings.opto_board_log_start_port + i])
        log_publisher.append(["127.0.0.1", settings.experiment_publish_log_port])
        log_publisher.append(["127.0.0.1", settings.control_host_control_send_port])
        log_publisher.append(["127.0.0.1", settings.numpy_writer_publish_port])
        self.logger.subscribe(log_publisher)

        # create subscriptions for NumpyDataWriter
        data_publisher = []
        for i in range(0,len(self.obct)):
            data_publisher.append(["127.0.0.1", settings.opto_board_data_start_port + i])
        data_publisher.append(["127.0.0.1", settings.experiment_publish_data_port])
        data_publisher.append(["127.0.0.1", settings.control_host_control_send_port])
        self.npy_writer.subscribe(data_publisher)

        # create subscriptions / targets to pull from
        hosts_to_pull_from = []
        for i in range(0,len(self.obct)):
            hosts_to_pull_from.append(["127.0.0.1",settings.opto_board_control_send_port + i])
        hosts_to_pull_from.append(["127.0.0.1",settings.experiment_push_port])
        self.subscribe(hosts_to_pull_from)


    def subscribe(self, publisher):
        for line in publisher:
            self.logger.create_info_log_entry("Control Host subscribes to: "+str(line[0])+":"+str(line[1]))
            self.control_receive_socket.connect("tcp://"+str(line[0])+":"+str(line[1]))


    def start_experiment(self):
        """
        This method contains the main loop of the program. After the start of all slaves the control host waits for
        incoming messages from the OptoBoardCommunicationThreads or the ExperimentHandler class. If a kill message
        arrives (message type = 'kill') the control host shuts all slaves down ends the main program.
        """
        self.status = "busy"
        self.logger.create_info_log_entry("start experiment environment")

        self.create_slave_subscriptions()

        self.logger.start()
        self.npy_writer.start()
        self.experiment_handler.start()
        for interface in self.obct:
            self.obct[interface].start()

        while self.status == "busy":
            try:
                msg = self.control_receive_socket.recv_json()
                if slaves.is_msg_valid(msg):
                    if msg['receiver'] == "control host" or msg['receiver'] == "all":
                        if msg['type'] == "kill":
                            print("received kill message")
                            self.shutdown()
                        if msg['type'] == "cmd":
                            if msg['message'] == "time sync":
                                print "got time sync message"
                                message = {'sender':'control host', 'receiver':'ttyACM*', 'message':'time sync', 'type':'cmd'}
                                self.control_send_socket.send_json(message)
                else:
                    self.create_log_entry("received invalid message... I throw it away","error")

            except KeyboardInterrupt:
                self.shutdown()
            except Exception as e:
                self.create_log_entry(str(e))

    def create_log_entry(self,msg, type="info"):
        message = {'sender':'control host', 'receiver':'log', 'message':msg, 'type':type}
        self.control_send_socket.send_json(message)


    def shutdown(self):
        print "[+] Shutting down"
        self.logger.create_info_log_entry("Shutting all slaves down")
        self.experiment_handler.shutdown()

        # kill the opto board threads
        message = {'sender':'control host', 'receiver':'ttyACM*', 'message':None, 'type':'shutdown'}
        self.control_send_socket.send_json(message)

        # kill the rest to ensure a nice shutdown order
        time.sleep(0.2)
        message['receiver'] = 'all'
        self.control_send_socket.send_json(message)

        exit(0)



if __name__ == "__main__":
    # the entire program starts HERE
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

    #exit(0)
    control_host.start_experiment()

