# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 16:56:57 2014

@author: sun
"""

def get_vw_model_weights(vw_modelfile):
    info = [line.strip() for line in open(vw_modelfile)]
    index = 1
    for index in range(len(info)):
       if 'Constant' in info[index]:
          bias = float(info[index].split(':')[2])
          break
    feature_weights = []
    for v in info[(index+1):]:
        s1 = v.split('^')
        namespace = s1[0]
        s2 = s1[1].split(':')
        id = s2[0]
        weight = float(s2[2])
        feature_weights.append({'namespace':namespace,'id':id,'weight':weight})
    return {'bias': bias,'feature':feature_weights}

def get_libsvm_model_weights(modelfile):   
    info = [line.strip() for line in open(modelfile)]
    model_type = info[0].split(' ')[1]
    index = 1
    for index in range(len(info)):
       if 'nr_feature' in info[index]:
          feature_num = int(info[index].split(' ')[1])
          next
       if 'bias' in info[index]:
          bias = float(info[index].split(' ')[1])
          break
    weights = [ float(v) for v in info[(index+2):]] 
    return {'model_type':model_type,'fn':feature_num,
            'bias':bias,'weights':weights}

def get_feature_mapping(fm):
    featm = [ line.strip() for line in open(fm) ]   
    feat_dc = {}
    for f in featm:
        sf = f.split(':')
        feat_dc[sf[1]] = sf[0]
    return feat_dc


if __name__ == "__main__":
    # libsvm
    modelfile = '/Users/sun/workspace/data/gxh_model_libsvm.model'
    w = get_libsvm_model_weights(modelfile)
    # vw    
    vw_modelfile = '/Users/sun/workspace/data/gxh_vw_model.model'
    get_vw_model_weights(vw_modelfile)
        
    fm = '/Users/sun/workspace/data/featmap.fm'
    get_feature_mapping(fm)
