# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 14:33:14 2014

@author: sun
"""

import csv
import pandas as pd

def libsvm2vw(input_file, output_file):
    ''' 
    将liblinear的格式转换为vw的格式
    '''
    i = open( input_file )
    o = open( output_file, 'wb' )
    for line in i:
        try:
            y, x = line.split(" ", 1)
        except ValueError:
            print "line with ValueError (skipping):"
            print line         
        new_line = y + " |feature " + x
        o.write( new_line )

def libsvm2csv(input_file, output_file, d):
    reader = csv.reader( open( input_file ), delimiter = " " )
    writer = csv.writer( open( output_file, 'wb' ))
    for line in reader:
        label = line.pop( 0 )
        if line[-1].strip() == '':
            line.pop( -1 )
        line = map( lambda x: tuple( x.split( ":" )), line )
        new_line = [ label ] + [ 0 ] * d
        for i, v in line:
            i = int( i )
            if i <= d:
                new_line[i] = v
        writer.writerow( new_line )

def read_file_df(inputfile):  
    d = pd.read_csv(inputfile,header = None)
    return d 

if __name__ == "__main__":
    ''' run
    '''
    return
