#!/usr/bin/python
'''
Input:  filename containing raw csv measured using nvidia-smi utility
Output: multiple timeseries files
        1) individual gpu utilization, mem utilization, and power usage CSV and JSON
        2) average GPU and memory utilization (CSV)
'''

import sys
import json
import re
from datetime import datetime
from common import csv_to_json

def validate(csv_str):
    '''
    Verify a consistent number of columns in the csv string
    Strip last record if incomplete
    '''
    lines = csv_str.split('\n')
    len0 = len(lines[0].split(','))
    len1 = len(lines[-1].split(','))
    while len0 != len1:
        lines.pop()
        len1 = len(lines[-1].split(','))
    return '\n'.join(lines)

def mean(numbers):
    ''' Calculate mean of array of numbers '''
    return float(sum(numbers)) / max(len(numbers), 1)

def calc_avg(gpu_str, mem_str):
    '''
    Input (example for 4 GPUs):
        gpu_str = "t1,0,0,100,0\nt2,0,0,40,0\n"
        mem_str = "t1,0,0,8,0\nt2,0,0,20,0\n"
    Output (tstamp, gpu_avg, mem_avg):
        avg_str = "t1,25,2\nt2,10,5"
    '''
    avg_str = ''
    gpu_lines = gpu_str.split('\n')
    mem_lines = mem_str.split('\n')
    while gpu_lines:
        line = gpu_lines.pop(0)
        fields = line.split(',')
        avg_str += '%s,%.1f,' % (fields[0], mean([float(i) for i in fields[1:]]))
        line = mem_lines.pop(0)
        fields = line.split(',')
        avg_str += '%.1f\n' % (mean([float(i) for i in fields[1:]]))
    return avg_str


def parse_raw_gpu(raw_fn):
    '''
    Read gpu data from nvidia-smi utility and return individual CSV strings
    for GPU utilization, memory utilization, and power usage
    '''
    with open(raw_fn, 'r') as fid:
        lines = fid.readlines()
    line = lines.pop(0)  # discard header
    time0 = False
    while lines:
        line = lines.pop(0)
        try:
            (time, idx, _, util_gpu, util_mem, power_gpu, perf_stat, gpu_temp) = line.split(',')
            util_gpu = util_gpu.strip().split()[0]
            util_mem = util_mem.strip().split()[0]
            power_gpu = power_gpu.strip().split()[0]
            time = datetime.strptime(time, '%Y/%m/%d %H:%M:%S.%f')
            perf_stat = perf_stat.strip().split('P')[1]
            gpu_temp = gpu_temp.strip().split()[0]
            if not time0:
                time0 = time
                gpu_str = '0'
                mem_str = '0'
                pow_str = '0'
                perf_str = '0'
                temp_str = '0'
            elif int(idx) == 0:
                t_sec = round((time - time0).total_seconds(), 1)
                gpu_str += '\n%g' % t_sec
                mem_str += '\n%g' % t_sec
                pow_str += '\n%g' % t_sec
                perf_str += '\n%g' % t_sec
                temp_str += '\n%g' % t_sec
            gpu_str += ',' + util_gpu
            mem_str += ',' + util_mem
            pow_str += ',' + power_gpu
            perf_str += ',' + perf_stat
            temp_str += ',' + gpu_temp
        except Exception as err:
            print(str(err))
            print(line)
            pass
    return (gpu_str, mem_str, pow_str, perf_str, temp_str)

def main(raw_fn):
    '''
    Parse each line of input file and construct CSV strings, then convert to JSON
    '''
    gpu_str, mem_str, pow_str, perf_str, temp_str = parse_raw_gpu(raw_fn)
    # Often the last set of data is incomplete. Clean the csv records
    gpu_str = validate(gpu_str)
    mem_str = validate(mem_str)
    pow_str = validate(pow_str)
    perf_str = validate(perf_str)
    temp_str = validate(temp_str)
    ext = ['.gpu', '.mem', '.pow', 'perf', 'temp']
    num_gpu = len(gpu_str.split('\n')[0].split(',')) - 1
    header = 'time_sec,' + ','.join(['gpu' + str(i) for i in range(num_gpu)])
    header += '\n'
    # Save data for all individual gpu traces
    for csv_str in [gpu_str, mem_str, pow_str, perf_str, temp_str]:
        csv_str = header + csv_str
        ext_str = ext.pop(0)
        out_fn = raw_fn.replace('data/raw', 'data/final') + ext_str + '.csv'
        with open(out_fn, 'w') as fid:
            fid.write(csv_str)
        obj = csv_to_json(csv_str)
        out_fn = raw_fn.replace('data/raw', 'data/final') + ext_str + '.json'
        with open(out_fn, 'w') as fid:
            fid.write(json.dumps(obj))
    # Now calculate average GPU & Memory usage for all traces and save
    header = 'time_sec,GPU,MEMORY\n'
    avg_str = calc_avg(gpu_str, mem_str)
    out_fn = raw_fn.replace('data/raw', 'data/final') + '.avg.csv'
    with open(out_fn, 'w') as fid:
        fid.write(header + avg_str)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("USAGE: {} <raw_fn>\n".format(sys.argv[0]))
        sys.exit(1)
    main(sys.argv[1])
