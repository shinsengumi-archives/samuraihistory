import sys
import os
from os.path import isdir, exists
import json
from datetime import datetime
import html
import base64


isTest = False
testTids = [1208]

metadataFiles = {'': ['message_metadata_0.json', 'message_metadata_1.json', 'message_metadata_2.json', 'message_metadata_3.json', 'message_metadata_4.json', 'message_metadata_5.json', 'message_metadata_6.json', 'message_metadata_7.json', 'message_metadata_8.json', 'message_metadata_9.json', 'message_metadata_10.json']}

templateIndexFilepath = 'templates/topics.html'

def decodeJapanese(content):    
    content = html.unescape(content)
    ichars = [i for i in range(len(content)) if ord(content[i]) > 127]
    istart = -1
    chunks = []
    for i in range(len(ichars)):
        if i == len(ichars)-1 or ichars[i+1] - ichars[i] > 1:
            if i - istart > 2:
                chunk = ichars[istart+1:i+1]
                if (i-istart)%2==1:
                    chunk.append(chunk[-1]+1)
                chunks.append(chunk)
            istart = i
    
    key = '-'
    orig = [content[chunk[0]:chunk[-1]+1] for chunk in chunks]
    encoded = key.join(orig).encode('iso-8859-1', 'xmlcharrefreplace').decode('shift_jis', 'replace').split(key)
    for i, s in enumerate(orig):
        content = content.replace(s, encoded[i])
    return content



def getFromBase64(email, iBase64):
    istart = email.find('\r\n\r\n', iBase64)+4
    ieq = email.find('==', istart)
    ienter = email.find('\r\n\r\n', istart)
    iend = min((ieq if ieq > 0 else 9223372036854775800)+2, (ienter if ienter > 0 else 9223372036854775807))
    encoded = email[istart:iend].replace('\\r\\n', '\r\n')
    if isTest:
        print(istart, iend, encoded)
        t = base64.b64decode(encoded)
        print(t)
        print([x for x in t])
    return base64.b64decode(encoded).decode('utf-8', 'backslashreplace').replace('\n', '<br/>')


def getFromEmail(content, email):
    iBase64 = email.find('Content-Transfer-Encoding: base64')
    if iBase64 != -1:
        content = getFromBase64(email, iBase64)
    iBase64 = email.find('Content-Transfer-Encoding: base64', iBase64+10)
    if iBase64 != -1:
        content = content + getFromBase64(email, iBase64)
    return content
    

def readEncodedFile(file):
    if not exists(file):
        return False
    try:
        f = open(file, encoding='utf-8')
        content = json.load(f)
        f.close()
    except:
        f = open(file, encoding='iso-8859-1')
        content = json.load(f)
        f.close()
    return content


def genPage(group, tid, md):
    dataPath = group+'data/topics/'
    topicJsonFile = dataPath+str(tid)+'.json'

    templateFilepath = 'templates/topic.html'
    outputPage = group+'forum/'+str(tid)+'.html'
    
    topic = readEncodedFile(topicJsonFile)
    
    templateFile = open(templateFilepath, "r", encoding="utf8")
    template = templateFile.read()
    output = template.replace('{{group}}', group.replace('_', ' ').replace('/', ' '))
    output = output.replace('{{title}}', md['subject'])
    
    topicNav = ''
    if topic['prevTopicId'] != 0:
        topicNav = '<a href="'+str(topic['prevTopicId'])+'.html">[Previous Topic]</a> '
    if topic['nextTopicId'] != 0:
        topicNav = topicNav + '<a href="'+str(topic['nextTopicId'])+'.html">[Next Topic]</a>'
    output = output.replace('{{topicNav}}', topicNav)
    
    content = ''
    messages = sorted(topic['messages'], key=lambda msg: msg['msgId'])
    for msg in messages:
        content = content + '<div id="msg-'+str(msg['msgId'])+'">\n'
        
        date = datetime.fromtimestamp(int(msg['postDate']))
        content = content + '#'+str(msg['msgId'])+' ['+date.strftime('%Y-%m-%d %H:%M:%S')+']\n'
        
        if isTest:
            content = content + ' '+str(msg['msgId'])+' '+str(msg['prevInTopic'])+' '+str(msg['nextInTopic'])+'\n'
            
        content = content + '<h3>'
        subject = '(no subject)'
        if 'subject' in msg:
            subject = msg['subject']
        content = content + subject+'</h3>\n'
        
        author = '(no author)'
        if 'profile' in msg:
            author = msg['profile']
        elif 'authorName' in msg:
            author = msg['authorName']
        elif 'from' in msg:
            author = msg['from']
        content = content + 'by <i>'+author+'</i>\n<br/><br/>\n'
        
        body = msg['messageBody']
        email = readEncodedFile('data/email/'+str(msg['msgId'])+'_raw.json')
        if email:
            body = getFromEmail(body, email['rawEmail'])
        content = content + decodeJapanese(body)+'\n<br/>\n'
        
        if msg['prevInTopic'] != 0:
            content = content + '<a href="#msg-'+str(msg['prevInTopic'])+'">[Previous #'+str(msg['prevInTopic'])+']</a> '
        if msg['nextInTopic'] != 0:
            content = content + '<a href="#msg-'+str(msg['nextInTopic'])+'">[Next #'+str(msg['nextInTopic'])+']</a>'
            
        content = content + '\n</div>\n<hr/>\n\n'
        
    output = output.replace('{{content}}', content)
    
    out = open(outputPage, "w+", encoding="utf8")	
    out.write(output)
    out.close()
    templateFile.close()
    
    

def gen(group):
    dataPath = group+'data/topics/'
    topicIdsFile = dataPath+'retrievedTopicIds.json'
    indexPage = group+'forum.html'

    f = open(topicIdsFile)
    topicIds = json.load(f)
    f.close()
    topicIds.sort(reverse=True)
    if isTest:
        topicIds = testTids

    metadataList = []
    for mf in metadataFiles[group]:
        md = readEncodedFile(dataPath+mf)
        metadataList.extend(md['messages'])
        

    print(len(metadataList))

    metadata = {}
    for md in metadataList:
        metadata[md['messageId']] = md

    content = ''
    for tid in topicIds:
        if tid not in metadata:
            print('topic not found in metadata', tid)
            continue
        
        md = metadata[tid]
        date = datetime.fromtimestamp(md['date'])
        author = md['yahooAlias'] if md['yahooAlias'] != "" else md['email']
        nReplies = md['numRecords']
        if nReplies > 0:
            nReplies = nReplies-1
        if nReplies == 1:
            nReplies = str(nReplies) + ' reply'
        else:
            nReplies = str(nReplies) + ' replies'
            
        content = content + '<li>#'+str(tid)+' <b>['+date.strftime('%Y-%m-%d %H:%M')+']</b> '
        content = content + '<a href="forum/'+str(tid)+'.html">'+md['subject']+'</a> '
        content = content + '<b>('+nReplies+')</b> '
        content = content + '- <i>'+author+'</i><br/>\n'
        content = content + md['summary']+'...</li>\n'
        try:
            genPage(group, tid, md)
        except Exception as e:
            print(tid, e)

    templateIndexFile = open(templateIndexFilepath, "r", encoding="utf8")
    templateIndex = templateIndexFile.read()
    output = templateIndex.replace('{{group}}', group.replace('_', ' ').replace('/', ' '))
    output = output.replace('{{content}}', content)
    out = open(indexPage, "w", encoding="utf8")	
    out.write(output)
    out.close()
    templateIndexFile.close()
    

gen('')
