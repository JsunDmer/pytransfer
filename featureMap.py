#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 14:18:42 2014

@author: jian02.sun


featureMap: 实现用于查找和创建特征
"""

import yaml
import csv
import numpy as np
import sys

#####################################################
'''
transJob：用于将原始R数据转换成01类型的特征
'''
#####################################################               
        
class transJob(object):
    """ 用于将原始R数据转换成01类型的特征 """
    def __init__(self, configPath):
        # 获取conf的字典对象
        conf               = yaml.load(open(configPath))
        self.infile        = conf['input_file']
        self.outfile       = conf['output_file']
        # opts
        self.isSvmRank     = True if conf['isSvmRank'] else False
        self.skip_headers  = conf['skip_headers']

    def run(self, feature_map):
        self._raw2modeldata(feature_map)
        return

    def _raw2modeldata(self, feature_map): 
        '''   处理csv数据格式，转换模型输入格式
        ==================================== 
            input:
                feature_map: (外部)特征类对象实例
        '''
        if not isinstance(feature_map, featureMap):
            raise TypeError("参数错误, 请输入featureMap对象")

        i = open( self.infile )
        o = open( self.outfile, 'w' )
        reader = csv.reader(i , delimiter='\t')
        # 是否跳过首行
        headers = None
        if self.skip_headers:
            headers = reader.next()
        print "========\n   文件输入的字段名：{}\n=======".format(headers)
        line_num = 0
        
        # 判定是否用libsvm还是ranksvm格式
        parse_fun = self._parse_libsvm_line_2
        if self.isSvmRank:
            parse_fun = self._parse_ranksvm_line            
            
        for line in reader:
            if line_num % 100000 == 0: 
                print "进行到 %d" %line_num
            new_line = parse_fun(line, feature_map)
            o.write( new_line + "\n" )
            line_num += 1
        return

    def _parse_ranksvm_line(self, line, feature_map):
        '''
        function: 处理每一个行形成ranksvm格式
        input:
            line: 每一行
            self.feat_type：  特征类型（’g‘: 类似qid，’t‘: 目标值，’n‘: float型 ’c‘: 离散型）
            # headers： 特征类名，暂时没用
        output:
            ranksvm的每一行data格式
        '''
        # query_str: 每一行target field
        # dc_feat_parse: 每一行feature field的dict对象
        query_str      = line[ feature_map.feat['target']['id'] - 1 ]
        query_str      = query_str + ' ' + line[ feature_map.feat['group']['id'] - 1 ]
        dc_feat_parse  = {}

        for feat in feature_map.feature_filed:
            column_idx = int(feat['id'])
            field = line[ column_idx - 1 ]
            # 1. 判定字段类型
            if feat['type'] == 'n': # ------数值型的情况（对数值型分段处理）            
                # 计算value对应的bin段: demo 0.6_0.8
                binset_str = feature_map._get_which_binset(column_idx, field)
                field = binset_str          
            # 2. 搜索特征列表，是否已经注册了该特征
            fid = feature_map._search_cfeat(column_idx, field)
            # 3. 如果不存在，则注册该特征
            if fid == None:
                fid = feature_map._create_cfeat(column_idx, field)
            dc_feat_parse[fid] = 1 
        #!!! 按照次序排列   
        sorted_feat_parse = sorted(dc_feat_parse.iteritems(), key=lambda x : int(x[0]))         
        feature_str = " ".join( [ "%s:%s"%(f[0],f[1]) for f in sorted_feat_parse ] )
        return query_str + " " + feature_str
    
    def _parse_libsvm_line(self, line, feature_map):
        '''
        function: 处理每一个行形成liblinear格式,并且对数值型进行分段(自动)
        input:
            line: 每一行
            feature_map: 特征对象(获取特征dict)
        output:
            liblinear的每一行data格式
        '''
        # query_str: 每一行target field
        # dc_feat_parse: 每一行feature field的dict对象
        target = line[ feature_map.feat['target']['id'] - 1 ]
        query_str      = '-1' if target == '0' else target
        dc_feat_parse  = {}

        for feat in feature_map.feature_filed:
            column_idx = int(feat['id'])
            field = line[ column_idx - 1 ]
            # 1. 判定字段类型
            if feat['type'] == 'n': # ------数值型的情况（对数值型分段处理）            
                # 计算value对应的bin段: demo 0.6_0.8
                binset_str = feature_map._get_which_binset(column_idx, field)
                field = binset_str   
                # 2. 搜索特征列表，是否已经注册了该特征     
                fid = feature_map._search_cfeat(column_idx, field)
                # 3. 如果不存在，则注册该特征
                if fid == None:
                    fid = feature_map._create_cfeat(column_idx, field)
                dc_feat_parse[fid] = 1 
            else: # ------分类型的情况（对分类型分段处理） 
                field_list = field.split(',')
                for f in field_list:          
                    fid = feature_map._search_cfeat(column_idx, f)
                    if fid == None:
                        fid = feature_map._create_cfeat(column_idx, f)
                    dc_feat_parse[fid] = 1                
        #!!! 按照次序排列   
        sorted_feat_parse = sorted(dc_feat_parse.iteritems(), key=lambda x : int(x[0]))         
        feature_str = " ".join( [ "%s:%s"%(f[0],f[1]) for f in sorted_feat_parse ] )
        return query_str + " " + feature_str

    def _parse_libsvm_line_2(self, line, feature_map):
        '''
        function: 处理每一个行形成liblinear格式,并且对数值型进行分段(自动)
        input:
            line: 每一行
            feature_map: 特征对象(获取特征dict)
        output:
            liblinear的每一行data格式
        '''
        # query_str: 每一行target field
        # dc_feat_parse: 每一行feature field的dict对象
        target = line[ feature_map.feat['target']['id'] ]
        query_str      = '-1' if target == '0' else target
        dc_feat_parse  = {}

        for feat in feature_map.feature_filed:
            column_idx = feat['id']
            field = line[ column_idx ]
            #print "column_idx = {},  field = {}".format(column_idx, field)
            # 1. 判定字段类型
            if feat['type'] == 'n': # ------数值型的情况（对数值型分段处理）            
                #print "数值型的情况"
                # 计算value对应的bin段: demo 0.6_0.8
                binset_str = feature_map._get_which_binset(column_idx, field)
                field = binset_str  
                #print "field = {}".format(field) 
                # 2. 搜索特征列表，是否已经注册了该特征     
                k = str(column_idx) + "_" + str(field)
                if k in feature_map.dc_feat.keys():
                    fid = dc_feat[k] 
                    dc_feat_parse[fid] = 1                 
            else: # ------分类型的情况（对分类型分段处理）
                #print "分类型的情况"
                field_list = field.split(',')
                #print "field_list = {}".format(field_list)                 
                for f in field_list:          
                    k = str(column_idx) + "_" + str(f)
                    if k in feature_map.dc_feat.keys():
                        fid = dc_feat[k] 
                        dc_feat_parse[fid] = 1
        #!!! 按照次序排列   
        sorted_feat_parse = sorted(dc_feat_parse.iteritems(), key=lambda x : int(x[0]))         
        feature_str = " ".join( [ "%s:%s"%(f[0],f[1]) for f in sorted_feat_parse ] )
        return query_str + " " + feature_str

 
#####################################################
'''
featureMap: 实现用于查找和创建特征
'''
#####################################################

class featureMap:
    '''
    featureMap: 实现用于查找和创建特征
    '''
    def __init__(self, configPath):
        ''' 从配置文件中获取特征filed 
            特征类型（’n‘: float型 ’c‘: 离散型）
            =========================
        '''
        conf                  = yaml.load(open(configPath))
        self.feat             = conf['feature']
        self.feature_filed    = self.feat['field']
        self.feaure_save_file = conf['feaure_save_file']
        # 数值型bin分段
        self.numeric_bin_flag = {}
        # 特征mapping
        self.dc_feat          = {}
        self.feature_length   = 0

    def get_numeric_bin(self, feat_stat):
        numeric_field = [ f for f in self.feature_filed if f['type'] == 'n' ]
        for nf in numeric_field:
            field = str(nf['id'])
            print "nf: {}".format(nf)
            print "field: {}".format(field)
            if nf['bin'] != 'auto':# 从配置中获取bin分段
               self.numeric_bin_flag[field] = nf['bin']
            else: #否则,从统计模块中获取bin分段
               self.numeric_bin_flag[field] = feat_stat.statsinfo[field]

    def _get_which_binset(self, column_idx, value):
        ''' 计算属于哪个bin段 '''
        bsets = self.numeric_bin_flag[ str(column_idx) ]
        # 简单的二分查找
        length = len(bsets)
        if length == 1:
            if value == bsets[0]:
                return str(bsets[0])
            else:
                return "other"        
        if value >= bsets[length-1]:
            return str(bsets[length-1]) + "up"
        if value < bsets[0]:
            return str(bsets[0]) + "down"   
        for i in xrange(1,length):
            if value < bsets[i]:
                return '_'.join( [str(f) for f in bsets[i-1:i+1] ])                   

    def _create_nfeat(self, column_idx, column_val):
        ''' 创建特征 numeric mapping的id '''
        current_max_id = len(self.dc_feat)
        self.dc_feat[column_idx] = current_max_id + 1
        return current_max_id + 1

    def _search_nfeat(self, column_idx, column_val): 
        ''' 搜索特征 '''
        if column_idx in self.dc_feat.keys():
            return self.dc_feat[column_idx]
        else:
            return None

    def _create_cfeat(self, column_idx, column_val):
        ''' 创建特征category mapping的id '''
        k = str(column_idx) + "_" + str(column_val)
        current_max_id = len(self.dc_feat)
        self.dc_feat[k] = current_max_id + 1
        return current_max_id + 1

    def update_featureidx(self, column_idx, feature_name):
        km = str(column_idx) + "_" + str(feature_name)
        self.feature_length += 1
        self.dc_feat[km] = self.feature_length

    def create_featmapping(self, feat_stat):
        if not isinstance(feat_stat, FeatStat):
            raise TypeError("参数错误, 请输入FeatStat对象")
        if len(feat_stat.statsinfo) == 0:
            raise ValueError("please run feat_stat.stat()")
        for k in feat_stat.statsinfo.keys():
            if isinstance(feat_stat.statsinfo[k], list):
                l = len(feat_stat.statsinfo[k])
                for j in range(l):
                    if j == 0:
                        km = str(k) + "_" + str(feat_stat.statsinfo[k][0]) + "down"
                    if j == l - 1:    
                        km = str(k) + "_" + str(feat_stat.statsinfo[k][j]) + "up"
                    else:
                        km = str(k) + "_" + str(feat_stat.statsinfo[k][j]) + "_" + str(feat_stat.statsinfo[k][j+1])    
                    self.update_featureidx(k,kk)        
            else:
                for kk in feat_stat.statsinfo[k].keys():
                    self.update_featureidx(k,kk)
        print 'finish mapping'

    def save_dc_feat(self):
        ''' 保存特征mapping的id '''
        if self.feaure_save_file:
            with open(self.feaure_save_file,'w') as f:
                for k, v in self.dc_feat.items():
                    f.write(str(k) + ":" + str(v) + "\n")
        else:
            print "no file to save"

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
        self.statsinfo  = {}

    def _get_nfeat(self):
        numeric_field = [ f for f in self.feature_filed if f['type'] == 'n' ]       
        return numeric_field

    def _stat_auto_bin(self, column_valist):
        # bin操作
        column_valist = np.asarray(column_valist)
        _numeric_bin = np.percentile( column_valist, range(0,100,100/self.bin_num) )   
        _numeric_bin = list(set(_numeric_bin)) # 去除重复数据
        return sorted(_numeric_bin)

    def _stat_count(self, column_valist):
        # 分类型统计次数
        d = {}
        for val in column_valist:
            # 考虑特征可能包含多个：红色,深红色
            for v in val.split(','):
                if v not in ('',' ', 'NULL'):
                    if v not in d.keys():
                        d[v] = 1
                    d[v] += 1
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
                column_valist = [ float(c) for c in column_valist ] 
                r = self._stat_auto_bin(column_valist)
            else:
                r = self._stat_count(column_valist)
            print "统计结果为：{}".format(r)
            self.statsinfo[str(f['id'])] = r
        print "finish statisic field"

    def _get_single_columns(self, idx):
        reader = csv.reader(open(self.datafile), delimiter='\t')
        if self.skip_headers:
            reader.next()        
        columns = [ line[idx ] for line in reader ]
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

def main():
    if len(sys.argv) < 2:
        print 'usage python featureMap <config.yaml>'
        exit(1)

    liblinearjob = transJob(sys.argv[1])
    feature_map  = featureMap(sys.argv[1])
    feat_stat = FeatStat(sys.argv[1])
    ### 计算统计更新特征
    print '\tstep-1: 计算统计特征'
    feat_stat.stat()
    feature_map.get_numeric_bin(feat_stat)
    liblinearjob.run(feature_map)
    feature_map.save_dc_feat()
    feat_stat.save_statsinfo()

if __name__ == '__main__':
    main()
       