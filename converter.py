import random
import os

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
            for line in f.readlines():
                t,thpt = line_parser(line)
                # [[t,t,t,t],[t+1,t+1,...,]]
                for events in parsed_line_to_mahimahi_series(t*1000,thpt):
                    if len(events) > 0:
                        f_out.write("\n".join([str(e) for e in events])+"\n")

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

# convert all traces
if __name__ == '__main__':
    dir_paths = ["./lumous5G/4G","./lumous5G/5G"]
    output_dir_path = "./results"
    for dir in dir_paths:
        for file in os.listdir(dir):
            file_path = dir+"/"+file
            out_file_path = output_dir_path+"/"+file
            print(file_path)
            lumous_file_converter(file_path,out_file_path)

