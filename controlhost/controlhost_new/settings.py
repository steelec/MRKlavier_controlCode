"""
this module contains all relevant configuration parameters
"""

board_interface_pattern = "/dev/ttyACM*"
log_subdirectory = "data"

# number of values which have to be higher or lower then the threshold to indicate a
# status change
probe_counter = 8

experiment_port = 4999
experiment_publish_log_port = 5000
experiment_publish_data_port = 5001
experiment_push_port = 5002

numpy_writer_publish_port = 5003

board_tcp_port = 9004

control_host_control_recv_port = 5005
control_host_control_send_port = 5006
control_host_ip = "127.0.0.1"


opto_board_control_send_port = 8000
opto_board_log_start_port = 6000
opto_board_data_start_port = 7000

serial_timeout = 0.1


