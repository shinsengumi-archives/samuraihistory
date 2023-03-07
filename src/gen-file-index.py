import sys
import os
from os.path import isdir
import json

dataPath = 'data/'

def getTitle(directory):
    title = directory.replace('-', ' ')
    title = title.replace('_', '')
    title = ''.join([i for i in title if not i.isdigit()]).strip()
    return title

def getListing(type, path, file):
    if type == 'files':
        return '<a href="'+path+'">'+file+'</a><br/>\n'
    
    return '<a href="'+path+'"><img src="'+path+'" alt="'+file+'" height=150 /></a>\n'


def getFilesInDirectory(type, content, group, path, dir, lev):
    subfiles = sorted(os.listdir(group+path), key=lambda f: f if f.find('_') == 2 else '0'+f)
    if len(subfiles) <= 1:
        return content, False
        
    content = content + '<h'+str(lev)+' id="'+dir+'">' + getTitle(dir) + '</h'+str(lev)+'>\n'
    for subfile in subfiles:
        if subfile.endswith('.json'):
            continue
        if isdir(group+path+'/'+subfile):
            content, added = getFilesInDirectory(type, content, group, path+'/'+subfile, subfile, lev+1)
        else:
            content = content + getListing(type, path+'/'+subfile, subfile)
    content = content + '<br/>\n'
            
    return content, True

def gen(type, group):
    templateFile = open('templates/'+type+'.html', "r", encoding="utf8")
    template = templateFile.read()

    content = ''
    directories = []
    files = sorted(os.listdir(group+dataPath+type), key=lambda f: f if f.find('_') == 2 else '0'+f)
    for file in files:
        if file.endswith('.json'):
            continue
            
        path = dataPath+type+'/'+file
        if isdir(group+path):
            content, added = getFilesInDirectory(type, content, group, path, file, 3)
            if added:
                directories.append(file)
        else:
            content = content + getListing(type, path, file)
            
    nav = ''
    for dir in directories:
        nav = nav + '<li>'+'<a href="#'+dir+'">'+getTitle(dir)+'</a></li>\n'
    
    output = template.replace('{{group}}', group.replace('_', ' ').replace('/',' '))
    output = output.replace('{{table-of-contents}}', nav)
    output = output.replace('{{list}}', content)
    out = open(group+type+'.html', "w", encoding="utf8")	
    out.write(output)
    out.close()
    templateFile.close()

gen('files', '')
gen('photos', '')
