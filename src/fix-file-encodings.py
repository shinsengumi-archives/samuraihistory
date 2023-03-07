import sys
import os
from os.path import isdir
import json

charsets = ['windows-1252', 'iso-8859-1', 'shift_jis']

def rewriteFiles(path):
    files = os.listdir(path)
    for file in files:
        if file.endswith('.htm'):
            try:
                fh = open(path+file, "r", encoding=charsets[0])
                f = fh.read()
            except:
                try:
                    fh = open(path+file, "r", encoding=charsets[1])
                    f = fh.read()
                except:
                    fh = open(path+file, "r", encoding=charsets[2])
                    f = fh.read()
            i = f.lower().rfind('charset=')+8
            j = f.find('"', i)
            charset = f[i:j]
            fh.close()
            
            print(file, charset)
            if len(charset) == 0:
                continue
            fh = open(path+file, "r", encoding=charset)
            f = fh.read()
            f = f.replace('charset='+charset, 'charset=utf-8')
            f = f.replace('CHARSET='+charset, 'CHARSET=utf-8')
            out = open(path+file, "w", encoding="utf8")	
            out.write(f)
            out.close()
            fh.close()
            
        if isdir(path+file):
            rewriteFiles(path+file+'/')

rewriteFiles('data/files/')
