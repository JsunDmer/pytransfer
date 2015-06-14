#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 14:18:42 2014

@author: jian02.sun


featStat: 特征统计模块

"""

import yaml
import numpy as np

#####################################################
'''
FeatStat: 对特征进行统计计算
'''
#####################################################

class FeatStat:
    ''' 
    target: 该类主要用于更新config文件里的特征
        1. 获取数值型特征，进行一些基础性的统计，并更新config文件
        2. 计算一些统计指标
    '''
    def __init__(self, configfile):
        conf              = yaml.load(open(configfile))
        self.feat         = conf['feature']['field']
        self.bin_num      = conf['bin_num']
        self.skip_headers = conf['skip_headers']
        self.datafile     = conf['input_file']
        self.stats_file   = conf['statisic_file']   

        self.statsinfo    = {}

    def _get_nfeat(self):
        numeric_field = [ f for f in self.feature_filed if f['type'] == 'n' ]       
        return numeric_field

    def _stat_auto_bin(self, column_valist):
        # bin操作
        column_valist = np.asarray(column_valist)
        _numeric_bin = np.percentile( column_valist, range(100/self.bin_num,100,self.bin_num) )   
        _numeric_bin = list(set(_numeric_bin)) # 去除重复数据
        return sorted(_numeric_bin)

    def _stat_count(self, column_valist):
        # 分类型统计次数
        d = {}
        for val in column_valist:
            if val not in d.keys():
                d[val] = 1
            d[val] += 1
        return d

    def single_stat(self, **kwargs):
        if 'name' in kwargs.keys():
            f = [ f for f in self.feat if f['name'] == kwargs['name'] ][0]    
        elif 'idx' in kwargs.keys(): 
            f = [ f for f in self.feat if f['name'] == kwargs['name'] ][0]
        else:
            print "usage 参数名必须为name或者idx"
            exit
        column_valist = self._get_single_columns(f['id'])
        if f['type'] == 'n':  
            r = self._stat_auto_bin(column_valist)
        else:
            r = self._stat_count(column_valist)        
        return r
    
    def stat(self):
        for f in self.feat:
            column_valist = self._get_single_columns(f['id'])
            print "\n进行特征统计:{}, 类型为{}".format(f['name'],f['type'])
            if f['type'] == 'n': 
                # 过滤空值 
                len_total = len(column_valist)
                column_valist = [ c for c in column_valist if not self.check_NA(c) ]
                print "缺失值个数：{}".format( len_total - len(column_valist) )
                column_valist = [ float(c) for c in column_valist] 
                r = self._stat_auto_bin(column_valist)
            else:
                r = self._stat_count(column_valist)
            print "统计结果为：{}".format(r)
            self.statsinfo[str(f['id'])] = r
        print "finish statisic field"

    def _get_single_columns(self, idx):
        reader = csv.reader(  open(self.datafile) )
        if self.skip_headers:
            reader.next()        
        columns = [ line[idx - 1] for line in reader ]
        return columns

    def save_statsinfo(self):
        with open(self.stats_file,'w') as f:
            for k, v in self.statsinfo.items():
                content = k + ":" + v
                f.write(content + "\n")
        return

    def check_NA(self, val):
        if val == 'NA' or val == 'na' or val == ' ':          
            return 1
        else:
            return 0

    def update_config_file(self):
        return