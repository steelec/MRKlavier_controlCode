#!/usr/bin/python
import argparse
import traceback


def fill_matrix(matrix, parameters, filename):
    print("[*] fill the matrix")
    try:
        start_detection = False
        with open(filename,"r") as fh:
            for line in fh:
                line = line.rstrip()
                values = line.split(" ")
                boardID = int(float(values[0]))
                if boardID == 255:
                    start_detection = True
                    continue
                if boardID < 128 and start_detection:
                    timestamp = float(values[-1])
                    delta = timestamp - parameters['start']
                    if delta > 0:
                        print(line)
                        print("delta: "+str(delta))
                        row_number = int(delta/parameters['step size'])
                        print("put "+str(timestamp)+" in bucket with timestamp "+str(matrix[row_number][0]))
                    else:
                        print("delta < 0")
        return matrix
    except Exception as e:
        print(traceback.format_exc())
        return None


def create_matrix(config):
    print("[*] create the matrix")
    #print(config)
    try:
        matrix = []
        for i in range(0,config['length']):
            row = []
            timestamp = config['start'] + (i+1)*(config['step size']) - config['step size'] /2
            print("create row for timestamp "+str(timestamp))
            row.append(timestamp)
            for j in range(0,config['width']):
                board_data_array = []
                for k in range(0,4):
                    channel_data_array = []
                    board_data_array.append(channel_data_array)
                row.append(board_data_array)
            matrix.append(row)
        return matrix
    except Exception as e:
        print(traceback.format_exc())
        return None



def determine_matrix_parameters(filename, resolution):
    min_utc_time = 0
    max_utc_time = 0
    boards = {}
    start_detection = False
    try:
        with open(filename,"r") as fh:
            for line in fh:
                line = line.rstrip()
                values = line.split(" ")
                boardID = float(values[0])
                if int(boardID) == 255 and not start_detection:
                    print("[*] found start marker")
                    start_detection = True
                    min_utc_time = float(values[-1])
                    continue
                if start_detection:
                    timestamp = float(values[-1])
                    if timestamp > max_utc_time:
                        max_utc_time = timestamp

                    if boardID < 128 and boardID not in boards:
                        boards[boardID] = "foo"
                        print("[*] found board with the ID "+str(boardID))

        experiment_duration = max_utc_time - min_utc_time
        print("[*] start of the experiment: "+str(min_utc_time))
        print("[*] end of experiment: "+str(max_utc_time))
        print("[*] duration of the experiment: "+str(experiment_duration)+" seconds")
        matrix_length = int(experiment_duration/resolution) + 1
        matrix_width = len(boards) + 1
        print("[*] matrix length: "+str(matrix_length))
        print("[*] matrix width: "+str(matrix_width))

        return {'length':matrix_length,'width':matrix_width,'start':min_utc_time,'step size':resolution}

    except OSError:
        print("[!] Could not open the file")
        return None
    except Exception as e:
        print(traceback.format_exc())
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='data reduction and visualization script for the raw data of the MR Piano')
    parser.add_argument('-r', action="store", dest="resolution", type=int, help="resolution of the data in milliseconds",
                        default=100)
    parser.add_argument('-f', action="store", dest="rawfile", type=str, help="file with the raw data",
                        default=None)

    parser.add_argument('-p', action="store", dest="plot", type=bool, help="show a diagram with the reduced data",
                        default=False)

    parameters = parser.parse_args()


    if parameters.rawfile is None:
        print("[!] It was no file given. please enter a valid file name with -f parameter")
        print("[!] ABORT")
        exit(-1)

    print("[+] start down scale process with a resolution of "+str(parameters.resolution)+" ms")

    resolution = float(parameters.resolution) / 1000.0
    matrix_config = determine_matrix_parameters(parameters.rawfile, resolution)
    if matrix_config is None:
        exit(-1)

    matrix = create_matrix(matrix_config)
    if matrix is None:
        exit(-1)

    matrix = fill_matrix(matrix,matrix_config,parameters.rawfile)
    if matrix is None:
        exit(-1)