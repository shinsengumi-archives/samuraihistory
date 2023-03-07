import sys
import os
from os.path import isdir
import json
import re
import html

dataPath = 'data/'

def getFileMetadata(metadata, directory, nameKey):
    dir = re.sub('[^a-zA-Z0-9]+', '', directory)
    print(directory, dir)
    for md in metadata:
        name = re.sub('[^a-zA-Z0-9]+', '', html.unescape(md[nameKey]))
        print('-', md[nameKey], name)
        if dir.endswith(name):
            return md
            

def getPhotoMetadata(metadata, file):
    for md in metadata:
        if file.startswith(str(md['photoId'])):
            return md


def getListing(type, group, path, file, md):
    print(path)
    if type == 'files':
        return '<a href="'+path+'">'+md['fileName']+'</a> - '+md['description']+'<br/>\n'
        
    desc = ''
    if 'description' in md:
        desc = md['description']
        
    templateFile = open('templates/image.html', "r", encoding="utf8")
    template = templateFile.read()
    output = template.replace('{{name}}', md['photoName'])
    output = output.replace('{{file}}', file)
    output = output.replace('{{path}}', path)
    output = output.replace('{{desc}}', desc)
    outFile = file.replace('.jpg', '.html').replace('.png', '.html')
    out = open(group+'images/'+outFile, "w+", encoding="utf8")	
    out.write(output)
    out.close()
    templateFile.close()
    
    return '<table border=0><tr><td><a href="images/'+outFile+'"><img src="'+path+'" alt="'+file+'" height=150 /></a></td></tr><tr><td style="word-wrap: break-word; width: 100px;"><a href="images/'+outFile+'">'+md['photoName']+'</a></td></tr></table>\n'


def getFilesInDirectory(type, content, group, path, dir, metadata, lev):
    subfiles = sorted(os.listdir(group+path), key=lambda f: f if f.find('_') == 2 else '0'+f)
    if len(subfiles) <= 1:
        return content, False
        
    if type == 'files':
        metadataFile = open(group+path+'/fileinfo.json', "r", encoding="utf8")
        nameKey = 'fileName'
    else:
        metadataFile = open(group+path+'/photos-0.json', "r", encoding="utf8")
        nameKey = 'albumName'
    mds = json.load(metadataFile)
        
    print(metadata, dir)
    content = content + '<h'+str(lev)+' id="'+dir+'">' + metadata[nameKey] + '</h'+str(lev)+'>\n'
    content = content + '<p>'+metadata['description']+'</p>\n'
    if type == 'photos':
        content = content+'<div style="display: flex; flex-direction: row; flex-wrap: wrap;">\n'
    
    for subfile in subfiles:
        if subfile.endswith('.json'):
            continue
        if type == 'files':
            md = getFileMetadata(mds, subfile, nameKey)
        else:
            md = getPhotoMetadata(mds, subfile)
        
        if isdir(group+path+'/'+subfile):
            content, added = getFilesInDirectory(type, content, group, path+'/'+subfile, subfile, metadata, lev+1)
        else:
            content = content + getListing(type, group, path+'/'+subfile, subfile, md)
    if type == 'photos':
        content = content+'</div>\n'
    content = content + '<br/>\n'
            
    return content, True

def gen(type, group):
    templateFile = open('templates/'+type+'.html', "r", encoding="utf8")
    template = templateFile.read()
    
    if type == 'files':
        metadataFile = open(group+'data/files/fileinfo.json', "r", encoding="utf8")
        nameKey = 'fileName'
    else:
        metadataFile = open(group+'data/photos/albums.json', "r", encoding="utf8")
        nameKey = 'albumName'
    metadata = json.load(metadataFile)

    content = ''
    nav = ''
    directories = []
    files = sorted(os.listdir(group+dataPath+type), key=lambda f: f if f.find('_') == 2 else '0'+f)
    for file in files:
        if file.endswith('.json'):
            continue
            
        path = dataPath+type+'/'+file
        md = getFileMetadata(metadata, file, nameKey)
        if isdir(group+path):
            content, added = getFilesInDirectory(type, content, group, path, file, md, 3)
            if added:
                desc = md['description']
                if desc != '':
                    desc = ' - ' + desc
                nav = nav + '<li>'+'<a href="#'+file+'">'+md[nameKey]+'</a>'+desc+'</li>\n'
        else:
            content = content + getListing(type, group, path, file, md)

    output = template.replace('{{group}}', group.replace('_', ' ').replace('/',' '))
    output = output.replace('{{table-of-contents}}', nav)
    output = output.replace('{{list}}', content)
    out = open(group+type+'.html', "w", encoding="utf8")	
    out.write(output)
    out.close()
    templateFile.close()

gen('files', '')
gen('photos', '')
