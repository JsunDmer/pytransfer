#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cPickle as pickle
import csv
import multiprocessing
import sys
import random
import os
import shutil
import argparse
from featureMap import *


def save_feat_mapping(filename, feature_map):
    with open(filename, 'w') as f:
        picklestring = pickle.dump(feature_map, f)

def load_feat_mapping(filename):
    with open(filename, 'r') as f:
        feat_map = pickle.load(f)
        return feat_map

def parse_libsvm_line(line, feature_map):
    target = line[ feature_map.feat['target']['id'] ]
    query_str = '-1' if target == '0' else target
    dc_feat_parse  = {}
    for feat in feature_map.feature_filed:
        column_idx = feat['id']
        field = line[ column_idx ]
        if feat['type'] == 'n':           
            binset_str = feature_map._get_which_binset(column_idx, field)
            field = binset_str  
            k = str(column_idx) + "_" + str(field)
            if k in feature_map.dc_feat.keys():
                fid = feature_map.dc_feat[k] 
                dc_feat_parse[fid] = 1            
        else:
            field_list = field.split(',')              
            for f in field_list:
                k = str(column_idx) + "_" + str(f)
                if k in feature_map.dc_feat.keys():
                    fid = feature_map.dc_feat[k] 
                    dc_feat_parse[fid] = 1              
    sorted_feat_parse = sorted(dc_feat_parse.iteritems(), key=lambda x : int(x[0]))         
    feature_str = " ".join( [ "%s:%s"%(f[0],f[1]) for f in sorted_feat_parse ] )
    return query_str + " " + feature_str
 
def transfer_raw2libsvm(infile, outfile, modelfile):
    i = open( infile )
    o = open(outfile,'w')  
    reader = csv.reader(i , delimiter='\t')      
    headers = reader.next() 
    feat_map = load_feat_mapping(modelfile)
    for line in reader:
        new_line = parse_libsvm_line(line, feat_map)
        #print new_line
        o.write( new_line + "\n" )

def split_file(rawfile, split_num):
    reader = csv.reader( open( rawfile ) , delimiter='\t')
    headers = reader.next() 
    ofile_list = list()
    path , basename = os.path.split(os.path.abspath(rawfile))
    basename = basename.split('.')[0]
    print "path = {}, basename = {}".format(path, basename)
    if os.path.exists( path + '/tmp' ):
        shutil.rmtree(path + '/tmp')
    os.mkdir( path + '/tmp' )   
    for i in range(split_num):
        of = open( path +'/tmp/' + basename + '__tmp__' + str(i),'w')
        ofile_list.append(of)
        of.write('\t'.join(headers) + "\n" )
    for line in reader:
        rid = random.randint(0, split_num -1)
        ofile_list[rid].write('\t'.join(line) + "\n" )       

def merge_file(path, outfile):
    o = open(outfile,'w')
    flist = [ path + '/' + l for l in os.listdir(path) if '__tmp__t__' in l]
    for f in flist:
        print f
        with open(f) as of:
            for line in of:
                o.write(line)
        of.close()


def parse_args():
    ''' 参数解析 '''
    if len(sys.argv) < 4:
        print "usage: python transjob_pallel.py <-c vonf> <-i input.csv> <-o output.csv> | <-s 10> <-p 4>"
        print "ERROR args input\nEXIT!"
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='conf', type=str)
    parser.add_argument('-i', dest='rawfile', type=str)
    parser.add_argument('-o', dest='outfile', type=str)
    parser.add_argument('-s', dest='split_file_num', default=10, type=int)
    parser.add_argument('-p', dest='processes_num', default=4, type=int)

    args = vars(parser.parse_args())
    return args

def main():

    args = parse_args()
    conf      = args['conf']
    rawfile   = args['rawfile']
    outfile   = args['outfile']
    split_file_num = args['split_file_num']
    processes_num  = args['processes_num']

    print '\n进行特征mapping过程: ..............'
    feature_map  = featureMap(conf)
    feat_stat = FeatStat(conf)
    feat_stat.stat()
    feature_map.get_numeric_bin(feat_stat)
    feature_map.create_featmapping(feat_stat)
    modelfile = feature_map.feaure_save_file
    save_feat_mapping(modelfile, feature_map)

    print '\n进行文件分割处理: ..............'
    split_file(rawfile, split_file_num)
    path, basename = os.path.split(os.path.abspath(rawfile))
    basename = basename.split('.')[0]
    infile_list  = [ path +'/tmp/' + basename + '__tmp__' + str(i) for i in range(split_file_num) ]
    outfile_list = [ path +'/tmp/' + basename + '__tmp__t__' + str(i) for i in range(split_file_num) ]  
    
    print '\n并行执行文件转换: ..............'    
    pool = multiprocessing.Pool(processes = processes_num)
    for i in range(split_file_num):
        pool.apply_async(transfer_raw2libsvm, args =(infile_list[i],outfile_list[i],modelfile,))
    pool.close()
    pool.join()
    print 'SUCCESS: 执行转换完成'

    print '\n开始进行文件合并处理: .............'
    merge_file(path + '/tmp', outfile)
    print 'SUCCESS: all job finish'

if __name__ == '__main__':
    main()
