import random
import os
import numpy as np

# ret:  (Timestamp, Throughput in Mbps)
def line_parser(line:str):
    ts,tp = line.strip().split()
    return int(float(ts)),float(tp)

# suppose throughput in Mbps
def throughput_to_pkts_ms(throughput_mbps):
    return int(throughput_mbps/12)

# index to compensate
def compensate_pkts(throughput_mbps):
    k = int((throughput_mbps/12 % 1) *1000)
    return random.sample(range(0,1000),k)

# throughput to mahimahi series
#  Mahimahi series is like:
# [[0,0,0,0,0], 5 packets is permitted to be sent in time slot 0
# [1,1,1,1]] 4 packets is permitted to be sent in time slot 1
def parsed_line_to_mahimahi_series(time_bias_ms,throughput):
    series = [[i]*throughput_to_pkts_ms(throughput) for i in range(1000)]
    for i in compensate_pkts(throughput):
        series[i].append(i)
    # add time bias
    for i in range(1000):
        for j,element in enumerate(series[i]):
            series[i][j] = element + time_bias_ms
    return series


def lumous_file_converter(input_file,output_file):
    with open(input_file,"r") as f:
        with open(output_file,"w") as f_out:
            # duplicate line occurs in 4G trace file
            previous_timestamp = None
            for line in f.readlines():
                t, thpt = line_parser(line)
                if t==previous_timestamp:
                    continue

                else:
                    # [[t,t,t,t],[t+1,t+1,...,]]
                    for events in parsed_line_to_mahimahi_series(t*1000,thpt):
                        if len(events) > 0:
                            f_out.write("\n".join([str(e) for e in events])+"\n")

                    previous_timestamp = t

def file_verifier(file):
    # verify if it is monotonouly
    previous = 0
    with open(file) as f:
        for i,line in enumerate(f.readlines()):
            try:
                assert int(line) >= previous
                previous = int(line)
            except Exception:
                print("Error line index:",i)

def convert_all_traces():
    dir_paths = ["./lumous5G/4G"] # ,"./lumous5G/5G"
    output_dir_path = "./results"
    for dir in dir_paths:
        for file in os.listdir(dir):
            file_path = dir + "/" + file
            out_file_path = output_dir_path + "/" + file
            print(file_path)
            lumous_file_converter(file_path, out_file_path)
            file_verifier(out_file_path)

# Some error in original trace
def _check_error(file):
    with open(file) as f:
        time_stamp = []
        for line in f.readlines():
            time_stamp.append(float(line.strip().split()[0]))
    for i, e in enumerate(time_stamp):
        if i > 0:
            try:
                assert e > time_stamp[i - 1]
            except:
                print(e)
                print(file)

def _show_error_in_4G_files():
    dir_paths = ["./lumous5G/4G", "./lumous5G/5G"]
    output_dir_path = "./results"
    for dir in dir_paths:
        for file in os.listdir(dir):
            file_path = dir + "/" + file
            out_file_path = output_dir_path + "/" + file
            # print(file_path)
            # lumous_file_converter(file_path, out_file_path)
            _check_error(file_path)

def _calculate_mean_throughput(dir):
    tp_all = []
    for file in os.listdir(dir):
        file_path = dir + "/" + file
        with open(file_path) as f:
            for line in f.readlines():
                t,tp = line_parser(line)
                tp_all.append(tp)
    return np.mean(tp_all)

# convert all traces
if __name__ == '__main__':
    convert_all_traces()



