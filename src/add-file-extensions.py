import sys
import os
from os.path import isdir
import json

def updateFiles(path):
    files = os.listdir(path)
    for file in files:
        if isdir(path+file):
            updateFiles(path+file+'/')
            continue
            
        if file.find('.') == -1:
            print(file)
            
            fh = open(path+file, "r", encoding="ansi")
            f = fh.read()
            front = '<html>\n<head>\n<meta charset="utf-8">\n<title>'+file+'</title>\n</head>\n<body>\n<pre>\n'
            back = '\n</pre>\n</body>\n</html>\n'
            out = open(path+file, "w", encoding="utf8")
            out.write(front+f+back)
            out.close()
            fh.close()
            os.rename(path+file, path+file+'.html')
            
        

updateFiles('data/files/')
