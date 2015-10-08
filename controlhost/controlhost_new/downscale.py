#!/usr/bin/python
import argparse
import traceback
import datetime


def fill_matrix(matrix,filename,settings):

    start_detection = False
    timestamp_experiment_start = 0

    with open(filename,"r") as fh:
        for line in fh:
            line = line.rstrip()
            values = line.split(" ")

            if float(values[0]) > 254 and not start_detection:
                start_detection = True
                timestamp_experiment_start = float(values[-1])
                continue

            if start_detection and float(values[0]) < 128:

                timestamp = float(values[-1])
                if timestamp >= timestamp_experiment_start:
                    delta = timestamp - timestamp_experiment_start
                    row_number = int(delta/settings['resolution'])
                    #print("put line with timestamp "+str(timestamp)+" in bucket with timestamp "+str(matrix[row_number][0]))
                    boardID = int(float(values[0]))
                    for i in range(1,5):
                        matrix[row_number][(boardID-1)*4+i].append(values[i])
                else:
                    pass
                    #print("ignore line with timestamp "+str(timestamp))


    print(matrix)

    return matrix

def generate_matrix(properties):
    print("generate "+str(properties['length'])+" x "+str(properties['width'])+" matrix")
    matrix = []
    for i in range(0,properties['length']+1):
        row = [properties['start utc']+(i+1)*properties['resolution']- properties['resolution']/2]
        for j in range(1,properties['width']):
            row.append([])
        print(row)
        matrix.append(row)
    return matrix

def analyze_raw_data(filename,res):
    detected_boards = {}
    min_utc = 2e11
    max_utc = 0
    start_detection = False
    with open(filename,"r") as fh:
        for line in fh:
            line = line.rstrip()
            values = line.split(" ")
            if float(values[0]) > 254 and not start_detection:
                start_detection = True
                min_utc = float(values[-1])
                print("Experiment start marker at "+datetime.datetime.fromtimestamp(float(values[-1])).strftime("%Y-%m-%d %H:%M:%S.%f"))
                continue

            if start_detection:
                boardID = float(values[0])
                if boardID < 128 and boardID not in detected_boards:
                    print("add board with ID "+str(int(boardID)))
                    detected_boards[boardID] = True

                if float(values[-1]) > max_utc:
                    max_utc = float(values[-1])

    print("Experiment start: "+str(min_utc)+" : "+datetime.datetime.fromtimestamp(min_utc).strftime("%Y-%m-%d %H:%M:%S.%f"))
    print("Experiment stop: "+str(max_utc)+" : "+datetime.datetime.fromtimestamp(max_utc).strftime("%Y-%m-%d %H:%M:%S.%f"))
    print("Experiment duration: "+str(max_utc-min_utc))

    return {'length':int((max_utc-min_utc)/res),'width':len(detected_boards)*4 + 1,'start utc':min_utc, 'resolution':resolution}



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

    foo = analyze_raw_data(parameters.rawfile,resolution)

    matrix = generate_matrix(foo)

    matrix = fill_matrix(matrix, parameters.rawfile,foo)

